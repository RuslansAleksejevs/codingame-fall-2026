"""Whole-map paired full-game endpoints; no label-based strength decisions."""
from support import *
import numpy as np


def estimate(values):
    values = np.asarray(values, dtype=float)
    if not len(values): return {'maps': 0, 'point': None, 'ci95': [None, None]}
    rng = np.random.default_rng(20261109)
    samples = values[rng.integers(0, len(values), size=(10000, len(values)))].mean(axis=1)
    return {'maps': len(values), 'point': float(values.mean()), 'ci95': np.quantile(samples, [.025, .975]).tolist()}


def clean_row(row):
    return row['valid'] and not row['returncode'] and not row['own_action_errors'] and not row['opponent_action_errors']


def score(row):
    return {'win': 1., 'draw': .5, 'loss': 0., 'invalid': 0.}[row['outcome']]


def summarize(rows, seeds, arms):
    indexed = {(r['candidate'], r['opponent'], r['seed'], r['seat']): r for r in rows}
    assert len(indexed) == len(rows)
    expected = {(a, o, s, p) for a in arms for o in OPPONENTS for s in seeds for p in (0, 1)}
    complete = set(indexed) == expected
    technical = {a: sum(not r['valid'] or r['returncode'] != 0 or bool(r['own_action_errors'])
        for r in rows if r['candidate'] == a) for a in arms}
    result = {'games': len(rows), 'expected_games': len(expected), 'complete': complete,
        'own_technical_errors': technical, 'opponent_error_games': sum(bool(r['opponent_action_errors']) for r in rows)}
    if not complete:
        result['missing_games'] = len(expected-set(indexed)); return result
    for mode in ('all', 'clean'):
        selected = list(seeds) if mode == 'all' else [s for s in seeds if all(clean_row(indexed[(a, o, s, p)])
            for a in arms for o in OPPONENTS for p in (0, 1))]
        section = {'maps': selected, 'per_opponent': {}, 'external': {}, 'gains': {}, 'direct': {}}
        vectors = {}
        for arm in arms:
            for opponent in OPPONENTS:
                key = arm+'-vs-'+opponent
                selected_rows = [indexed[(arm, opponent, s, p)] for s in selected for p in (0, 1)]
                values = [np.mean([score(indexed[(arm, opponent, s, p)]) for p in (0, 1)]) for s in selected]
                vectors[(arm, opponent)] = np.asarray(values)
                section['per_opponent'][key] = {**estimate(values), 'wdl': [sum(r['outcome'] == v for r in selected_rows) for v in ('win', 'draw', 'loss')],
                    'seats': {str(p): {**estimate([score(indexed[(arm, opponent, s, p)]) for s in selected]),
                        'wdl': [sum(indexed[(arm, opponent, s, p)]['outcome'] == v for s in selected) for v in ('win', 'draw', 'loss')]}
                        for p in (0, 1)}}
            vectors[(arm, 'external')] = np.mean([vectors[(arm, o)] for o in OPPONENTS[:3]], axis=0)
            section['external'][arm] = estimate(vectors[(arm, 'external')])
            section['direct'][arm] = {o: estimate(vectors[(arm, o)]) for o in ('league3m', 'b2m')}
        comparisons = [(a, 'base') for a in arms if a != 'base'] + [('broad1', 'narrow1')]
        if 'broad2' in arms: comparisons.append(('broad2', 'narrow2'))
        for a, b in comparisons:
            section['gains'][a+'-minus-'+b] = {o: estimate(vectors[(a, o)]-vectors[(b, o)]) for o in (*OPPONENTS, 'external')}
        if 'broad2' in arms:
            for comparison, control in (('broad-minus-narrow', 'narrow'), ('broad-minus-base', 'base')):
                delta = sum(vectors[(f'broad{i}', 'external')]-vectors[(control+str(i) if control == 'narrow' else control, 'external')]
                    for i in (1, 2))/2
                section[comparison] = estimate(delta)
        result[mode] = section
    return result


def promise(result):
    if not result['complete'] or any(result['own_technical_errors'].values()): return False
    if len(result['clean']['maps']) < 14: return False
    for mode in ('all', 'clean'):
        s = result[mode]; gains = s['gains']
        if s['broad-minus-narrow']['point'] <= 0 or s['broad-minus-base']['point'] < 0: return False
        if any(gains[f'broad{i}-minus-base']['external']['point'] < -.05-1e-12 for i in (1, 2)): return False
        if gains['broad1-minus-narrow1']['external']['point'] <= 0 or gains['broad1-minus-base']['external']['point'] < 0: return False
        if s['direct']['broad1']['league3m']['point'] < .5: return False
        if any(gains['broad1-minus-base'][o]['point'] < -.05-1e-12 for o in OPPONENTS): return False
    return True


def final_go(result):
    if not result['complete'] or any(result['own_technical_errors'].values()): return False
    if len(result['clean']['maps']) < 36: return False
    for mode in ('all', 'clean'):
        s = result[mode]
        for comp in ('broad1-minus-narrow1', 'broad1-minus-base'):
            metric = s['gains'][comp]['external']
            if metric['point'] < .03-1e-12 or metric['ci95'][0] <= 0: return False
        direct = s['direct']['broad1']['league3m']
        if direct['point'] < .55-1e-12 or direct['ci95'][0] <= .5: return False
        if any(s['gains']['broad1-minus-base'][o]['point'] < -.05-1e-12 for o in OPPONENTS): return False
    return True


def main(stage):
    check_freeze()
    arms, seeds, blocks = (ARMS, GAMEDEV, range(1, 5)) if stage == 'gamedev' else (('narrow1', 'broad1', 'base'), FINAL, range(1, 5))
    rows = []; bindings = {}
    from panel import metrics
    for i in blocks:
        name = stage+str(i); directory = OUT/name
        part = [json.loads(s) for s in (directory/'matches.jsonl').read_text().splitlines()]
        expected = json.loads((directory/'panel-spec.json').read_text())['schedule']
        assert [{k: r[k] for k in ('candidate', 'opponent', 'seed', 'seat')} for r in part] == expected
        replay = json.loads((OUT/(name+'-verification.json')).read_text())
        assert replay['passed'] and replay['matches_sha256'] == sha(directory/'matches.jsonl')
        assert replay['clean_games']+len(replay['excluded']) == len(part)
        for row in part:
            stem = f'{row["candidate"]}-vs-{row["opponent"]}-seed{row["seed"]}-seat{row["seat"]}'
            raw = json.loads((directory/(stem+'-raw.json')).read_text())
            reparsed = metrics(raw, row['seat'])
            for field in ('outcome', 'valid', 'score', 'opponent_score', 'own_action_errors', 'opponent_action_errors', 'own_output_count'):
                assert reparsed[field] == row[field], (stem, field)
            bindings[rel(directory/(stem+'-raw.json'))] = sha(directory/(stem+'-raw.json'))
        rows.extend(part)
        bindings[rel(directory/'matches.jsonl')] = sha(directory/'matches.jsonl')
        bindings[rel(OUT/(name+'-verification.json'))] = sha(OUT/(name+'-verification.json'))
    result = summarize(rows, seeds, arms)
    result.update(as_of=now(), stage=stage, data_bindings=bindings, source_sha256=sha(Path(__file__)),
        bootstrap_samples=10000, bootstrap_seed=20261109, unit='whole map with both seats/all arms/opponents together')
    result['promise' if stage == 'gamedev' else 'go'] = promise(result) if stage == 'gamedev' else final_go(result)
    save(OUT/(stage+'-decision.json'), result)
    print(json.dumps({k: result[k] for k in ('games', 'complete', 'own_technical_errors', 'promise' if stage == 'gamedev' else 'go')}))


if __name__ == '__main__': main(sys.argv[1])