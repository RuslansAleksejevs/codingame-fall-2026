"""Pure validation and encoding for fully settled, nonterminal boundaries."""
import hashlib
import json


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def validate(s):
    assert s['schema'] == 1 and s['phase'] == 'settled_predecision' and s['queue'] == []
    assert not s['done'] and s['surrounded'] and 0 <= s['turn'] < 200
    assert s['errors'] == [0, 0] and len(s['score']) == 2
    n = len(s['nodes'])
    assert 1 <= n <= 52 and len(s['units']) == n and s['remaining'] == s['units']
    assert all(len(v) == 2 and all(type(x) is int for x in v) for v in s['nodes'] + s['units'])
    assert all(x >= 0 for v in s['units'] for x in v)
    assert s['edges'] == sorted(s['edges']) and len({tuple(e) for e in s['edges']}) == len(s['edges'])
    assert all(len(e) == 2 and 0 <= e[0] < e[1] < n for e in s['edges'])
    assert len(s['initial_owners']) == len(s['triangles'])
    for t, initial in zip(s['triangles'], s['initial_owners']):
        assert len(t) == 6 and 0 <= t[0] < t[1] < t[2] < n
        assert t[3] in (-1, 0, 1) and initial == t[3] and t[4] in (0, 1) and t[5] in (0, 1)
        if t[3] >= 0:
            assert t[4 + t[3]] == 0 and t[5 - t[3]] == 1


def encode(s):
    validate(s)
    rows = ['CURRICULUM1', f"{len(s['nodes'])} {s['turn']} {s['score'][0]} {s['score'][1]} 0 1"]
    rows.extend(' '.join(map(str, xy + units + remaining)) for xy, units, remaining in zip(s['nodes'], s['units'], s['remaining']))
    rows += [str(len(s['edges'])), *(' '.join(map(str, e)) for e in s['edges']), str(len(s['triangles']))]
    rows.extend(' '.join(map(str, t[:4] + [initial] + t[4:])) for t, initial in zip(s['triangles'], s['initial_owners']))
    return '\n'.join(rows)