"""One explicitly requested finite block per shared lease; never loops/retries."""
from support import *


def freeze_data():
    teacher = teacher_guard()
    assert json.loads((OUT/'contracts.json').read_text())['passed']
    run([PYTHON, '-B', rel(CODE/'test_analyze.py')], 'synthetic-tests')
    identities = {**sources(), **teacher, rel(OUT/'contracts.json'): sha(OUT/'contracts.json')}
    save(OUT/'data-freeze.json', {'as_of': now(), 'identities': identities, 'teacher_adapter_changed': False,
        'train_maps': TRAIN, 'narrow_maps': TRAIN[:12], 'labeldev_maps': LABELDEV, 'gamedev_maps': GAMEDEV,
        'conditional_final_maps': FINAL, 'training_seeds': SEEDS, 'final_seed_designated': SEEDS[0],
        'teacher_command': [rel(BUILD/'bot'), *[rel(p) for p in [ACTOR, CRITIC, *ENEMIES]], '4', '16']})


def freeze_a1():
    teacher = teacher_guard()
    assert sha(OUT/'data-freeze.json') == 'a9f1a788cc7b205708ade8f8a13102ed699773c34e0d88e4ba2dca5e9ab62f4e'
    assert sha(OUT/'PROTOCOL.md') == 'b5f6638e3219069592091c9b100ce00966ecd14d0d2f78a3edcca32e84f80f00'
    assert sha(OUT/'pre-a1-sources.tar') == 'd113dde6c8886bd194d103d6d8b67cc86de5acf373591208087755a951f24754'
    assert not list(OUT.glob('labels-*.npz')) and not (OUT/'models').exists()
    original = json.loads((OUT/'data-freeze.json').read_text())
    revised = {rel(CODE/(name+'.py')) for name in ('support', 'collect', 'stage', 'job')}
    for path, digest in original['identities'].items():
        if path not in revised: assert sha(ROOT/path) == digest, path
    run([PYTHON, '-B', rel(CODE/'test_analyze.py')], 'a1-original-synthetic-tests')
    run([PYTHON, '-B', rel(CODE/'test_a1.py')], 'a1-exclusion-tests')
    identities = {**sources(), **teacher, rel(OUT/'data-freeze.json'): sha(OUT/'data-freeze.json'),
        rel(OUT/'pre-a1-sources.tar'): sha(OUT/'pre-a1-sources.tar')}
    save(OUT/'data-freeze-a1.json', {'as_of': now(), 'identities': identities, 'teacher_adapter_changed': False,
        'original_stop_preserved': True, 'already_played_games': 64, 'known_excluded_maps': [73017],
        'training_labels_at_amendment': 0, 'optimizer_updates_at_amendment': 0,
        'train_maps': TRAIN, 'narrow_maps': TRAIN[:12], 'labeldev_maps': LABELDEV, 'gamedev_maps': GAMEDEV,
        'conditional_final_maps': FINAL, 'training_seeds': SEEDS, 'final_seed_designated': SEEDS[0]})


def freeze_candidates(final=False):
    check_freeze()
    if final: assert json.loads((OUT/'gamedev-decision.json').read_text())['promise']
    arms = ('narrow1', 'broad1', 'base') if final else ARMS
    identities = sources()
    for arm in arms:
        if arm == 'base': continue
        directory = OUT/'models'/arm
        assert json.loads((directory/'verify/summary.json').read_text())['passed']
        for name in ('checkpoint.pt', 'weights.txt', 'config.json', 'summary.json', 'native-parity.json',
                     'package/bot.cpp', 'package/package.json', 'verify/summary.json', 'verify/packaged'):
            identities[rel(directory/name)] = sha(directory/name)
    save(OUT/('final-freeze.json' if final else 'candidate-freeze.json'), {'as_of': now(), 'identities': identities,
        'designated_seed': SEEDS[0], 'no_seed_selection': True,
        'schedule': game_schedule(FINAL if final else GAMEDEV, arms)})


def main(stage):
    if stage == 'freeze-data': freeze_data()
    elif stage == 'freeze-data-a1': freeze_a1()
    elif stage == 'freeze-candidates': freeze_candidates()
    elif stage == 'freeze-final': freeze_candidates(True)
    elif stage.startswith('gamedev') or stage.startswith('final'):
        final = stage.startswith('final'); index = int(stage[-1])-1
        assert 0 <= index < 4
        frozen = check_freeze('final-freeze.json' if final else 'candidate-freeze.json')
        seeds = FINAL[index*10:(index+1)*10] if final else GAMEDEV[index*4:(index+1)*4]
        hashes = prepare(stage, seeds)
        schedule = [r for r in frozen['schedule'] if r['seed'] in seeds]
        try: panel(stage, schedule, hashes)
        finally:
            if (OUT/stage/'matches.jsonl').exists(): verify(stage)
    else: raise ValueError(stage)


if __name__ == '__main__':
    stage = sys.argv[1]
    try: main(stage)
    except BaseException as error:
        target = OUT/(stage+'-stage-failure.json')
        if not target.exists(): save(target, {'as_of': now(), 'stage': stage, 'error': repr(error)})
        raise