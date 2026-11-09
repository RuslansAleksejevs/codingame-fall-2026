"""Read-only identity/count audit; writes only this pilot's closeout evidence."""
from support import *


def main():
    protected = guard()
    teacher = teacher_guard()
    freezes = {}
    for name in ('data-freeze-a1.json', 'candidate-freeze.json'):
        frozen = check_freeze(name)
        freezes[name] = {'sha256': sha(OUT/name), 'identities_checked': len(frozen['identities'])}
    decision = json.loads((OUT/'gamedev-decision.json').read_text())
    assert decision['complete'] and decision['games'] == 800 and not decision['promise']
    assert decision['all'] == decision['clean']
    assert not any(decision['own_technical_errors'].values()) and not decision['opponent_error_games']
    for path, digest in decision['data_bindings'].items():
        assert sha(ROOT/path) == digest, path
    assert not list(OUT.glob('final*')), 'Final must remain unopened'
    stages = {}
    map_hashes = {}
    for name in ('train1', 'train2', 'labeldev', 'gamedev1', 'gamedev2', 'gamedev3', 'gamedev4'):
        directory = OUT/name
        rows = [json.loads(line) for line in (directory/'matches.jsonl').read_text().splitlines()]
        replay = json.loads((OUT/(name+'-verification.json')).read_text())
        novelty = json.loads((OUT/(name+'-novelty.json')).read_text())
        hashes = json.loads((OUT/(name+'-map-hashes.json')).read_text())
        assert replay['passed'] and replay['matches_sha256'] == sha(directory/'matches.jsonl')
        assert novelty['passed'] and not novelty['collisions']
        assert not (set(map_hashes) & set(hashes))
        map_hashes.update(hashes)
        raw = list(directory.glob('*-raw.json'))
        portable = list(directory.glob('*.json.gz'))
        assert len(raw) == len(portable) == len(rows)
        for row in rows:
            stem = f'{row["candidate"]}-vs-{row["opponent"]}-seed{row["seed"]}-seat{row["seat"]}'
            assert (directory/(stem+'-raw.json')).is_file() and (directory/(stem+'.json.gz')).is_file()
        stages[name] = {'games': len(rows), 'maps': len(hashes), 'raw_files': len(raw),
            'portable_files': len(portable), 'clean_java_games': replay['clean_games'],
            'states': replay['states'], 'transitions': replay['transitions'],
            'own_error_games': sum(bool(r['own_action_errors']) for r in rows),
            'opponent_error_games': sum(bool(r['opponent_action_errors']) for r in rows),
            'matches_sha256': sha(directory/'matches.jsonl')}
    assert len(map_hashes) == len(set(map_hashes.values())) == 96
    assert set(map(int, map_hashes)) == set(TRAIN+LABELDEV+GAMEDEV)
    assert sum(s['games'] for s in stages.values()) == 960
    assert sum(s['own_error_games'] for s in stages.values()) == 0
    assert sum(s['opponent_error_games'] for s in stages.values()) == 1
    models = {}
    for arm in ARMS[:-1]:
        directory = OUT/'models'/arm
        summary = json.loads((directory/'summary.json').read_text())
        assert summary['updates'] == 800 and summary['root_exposures'] == 25600
        assert summary['passed'] and json.loads((directory/'verify/summary.json').read_text())['passed']
        models[arm] = {'updates': summary['updates'], 'root_exposures': summary['root_exposures'],
            'distinct_roots': summary['distinct_exposed_roots'], 'distinct_groups': summary['distinct_exposed_groups'],
            'training_seconds': summary['training_seconds'],
            'files': {rel(directory/p): sha(directory/p) for p in
                ('checkpoint.pt', 'weights.txt', 'package/bot.cpp', 'verify/packaged', 'exposures.npy')}}
    banks = {}
    data = json.loads((OUT/'data-summary.json').read_text())
    for name, bank in data['banks'].items():
        path = OUT/('bank-'+name+'.npz')
        assert sha(path) == bank['dataset_sha256']
        banks[name] = {k: bank[k] for k in ('roots', 'unique_states', 'groups', 'candidate_rows', 'changed_roots', 'dataset_sha256')}
        banks[name]['maps'] = len(bank['maps'])
    result = {'as_of': now(), 'classification': 'PROJECT_REPORTED', 'passed': True,
        'outcome': 'NO_GO_GAMEDEV_PROMISE', 'final_unopened': True, 'no_retraining': True,
        'freezes': freezes, 'protected': protected, 'teacher_identities_checked': len(teacher),
        'decision_sha256': sha(OUT/'gamedev-decision.json'), 'decision_bindings_checked': len(decision['data_bindings']),
        'data_summary_sha256': sha(OUT/'data-summary.json'), 'stages': stages, 'models': models, 'banks': banks,
        'new_full_games': 960, 'fresh_strength_games': 800, 'new_maps': 96,
        'teacher_calls': data['teacher_calls'], 'total_updates': 3200, 'total_root_exposures': 102400,
        'budget_at_audit_start': budget(), 'source_sha256': sha(Path(__file__)),
        'process_note': 'Run under the finite shared wrapper, which terminates its own child process group on exit. Separate post-exit process/timer evidence belongs in REPORT.'}
    save(OUT/'closeout-audit.json', result)
    print(json.dumps({'passed': True, 'new_full_games': 960, 'fresh_strength_games': 800,
        'total_updates': 3200, 'final_unopened': True}))


if __name__ == '__main__':
    main()