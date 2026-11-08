"""Pure evidence checks, with complete-map pairing and predeclared thresholds."""
import statistics
from common import EXTERNAL
from rl.eval.analyze import interval, value


def clean(row):
    return (row['valid'] and row['returncode'] == 0 and not row['own_action_errors']
            and not row['opponent_action_errors'])


def evaluate(rows, confirmation=False):
    opponents = (*EXTERNAL, 'league3m', *(('v6', 'bc') if confirmation else ()))
    seeds = sorted({r['seed'] for r in rows})
    by_key = {(r['candidate'], r['opponent'], r['seed'], r['seat']): r for r in rows}
    assert len(by_key) == len(rows), 'Duplicate evidence'
    expected = {(c, o, s, p) for c in ('greedy', 'search2') for o in opponents for s in seeds for p in (0, 1)}
    assert set(by_key) == expected, 'Incomplete or extra evidence'
    errors = sum(not r['valid'] or r['returncode'] != 0 or bool(r['own_action_errors']) for r in rows)
    paired, full_deltas, direct = {}, {}, []
    for opponent in opponents:
        clusters, kept = [], []
        for seed in seeds:
            keys = [(c, opponent, seed, seat) for c in ('greedy', 'search2') for seat in (0, 1)]
            assert len({by_key[key]['map_content_sha256'] for key in keys}) == 1, 'Map mismatch'
            if all(clean(by_key[key]) for key in keys):
                delta = [value(by_key['search2', opponent, seed, seat])-value(by_key['greedy', opponent, seed, seat]) for seat in (0, 1)]
                clusters.append(delta)
                full_deltas[opponent, seed] = delta
                kept += [by_key[key] for key in keys]
        paired[opponent] = {
            'complete_maps': len(clusters), 'clean_paired_games': 2*len(clusters),
            'gain_pp': 100*statistics.mean(sum(clusters, [])) if clusters else None,
            'paired_95_pp': interval(clusters),
            'search_score': statistics.mean(value(r) for r in kept if r['candidate']=='search2') if kept else None,
            'greedy_score': statistics.mean(value(r) for r in kept if r['candidate']=='greedy') if kept else None,
            'clean_paired_results': {c:{result:sum(r['outcome']==result for r in kept if r['candidate']==c) for result in ('win','draw','loss')} for c in ('greedy','search2')},
            'all_results': {c: {result: sum(r['outcome']==result for r in rows if r['candidate']==c and r['opponent']==opponent) for result in ('win','draw','loss')} for c in ('greedy','search2')},
        }
    composite = [sum([full_deltas[o, s] for o in EXTERNAL], []) for s in seeds if all((o, s) in full_deltas for o in EXTERNAL)]
    for seed in seeds:
        rr = [by_key['search2', 'league3m', seed, seat] for seat in (0, 1)]
        if all(clean(r) for r in rr):
            direct.append([value(r) for r in rr])
    gain = 100*statistics.mean(sum(composite, [])) if composite else None
    direct_score = 100*statistics.mean(sum(direct, [])) if direct else None
    external_ci, direct_ci = interval(composite), interval(direct)
    external_guard = all(paired[o]['gain_pp'] is not None and paired[o]['gain_pp'] >= -5 for o in EXTERNAL)
    preliminary = (gain is not None and gain >= 5 and direct_score is not None and direct_score >= 55
                   and external_guard and errors == 0)
    confirmed = (confirmation and preliminary and len(seeds)==40 and len(composite)>=36
                 and external_ci[0]>0 and direct_ci[0]>50
                 and all(v['complete_maps']>=36 and v['gain_pp']>=-5 for v in paired.values()))
    return {'maps': len(seeds), 'games': len(rows), 'paired': paired,
            'external_gain_pp': gain, 'external_gain_paired_95_pp': external_ci,
            'complete_composite_maps': len(composite), 'direct_score_percent': direct_score,
            'direct_score_95_percent': direct_ci, 'own_or_control_error_games': errors,
            'screen_passed': bool(preliminary), 'teacher_strength_gate_passed': bool(confirmed)}