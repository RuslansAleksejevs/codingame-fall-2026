"""Logged finite stage dispatch. Invoke only inside the shared v7 lease."""
from support import *


def main(name):
    jobs = {
        'collection-a1': [('stage.py', 'freeze-data-a1'), ('collect.py', 'resume-train1'), ('collect.py', 'train2')],
        'collection1': [('stage.py', 'freeze-data'), ('collect.py', 'train1')],
        'collection2': [('collect.py', 'train2')],
        'labeldev': [('collect.py', 'labeldev'), ('collect.py', 'assemble')],
        'optimize1': [('train.py', 'train', 'narrow1'), ('train.py', 'train', 'broad1'),
                      ('train.py', 'package', 'narrow1'), ('train.py', 'package', 'broad1')],
        'optimize2': [('train.py', 'train', 'narrow2'), ('train.py', 'train', 'broad2'),
                      ('train.py', 'package', 'narrow2'), ('train.py', 'package', 'broad2'), ('stage.py', 'freeze-candidates')],
        'gamedev-decision': [('analyze.py', 'gamedev')],
        'final-freeze': [('stage.py', 'freeze-final')],
        'final-decision': [('analyze.py', 'final')],
    }
    for phase in ('gamedev', 'final'):
        for index in range(1, 5): jobs[phase+str(index)] = [('stage.py', phase+str(index))]
    commands = [[PYTHON, '-B', rel(CODE/args[0]), *args[1:]] for args in jobs[name]]
    guard(); start = time.monotonic()
    save(OUT/'execution'/(name+'-start.json'), {'as_of': now(), 'commands': commands, 'budget': budget()})
    outcomes = []; failure = None
    try:
        for i, command in enumerate(commands):
            began = time.monotonic()
            proc = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            with (OUT/'execution'/f'{name}-{i}.log').open('x') as log:
                for line in proc.stdout: log.write(clean(line)); log.flush()
            code = proc.wait(timeout=1200)
            outcomes.append({'command': command, 'returncode': code, 'seconds': time.monotonic()-began})
            print(json.dumps({'job': name, 'step': i, 'returncode': code, 'seconds': time.monotonic()-began}), flush=True)
            assert code == 0, f'Failed stage {command}'
    except BaseException as error:
        failure = repr(error)
        raise
    finally:
        save(OUT/'execution'/(name+'-end.json'), {'as_of': now(), 'outcomes': outcomes,
            'seconds': time.monotonic()-start, 'failure': failure, 'budget': budget()})


if __name__ == '__main__': main(sys.argv[1])