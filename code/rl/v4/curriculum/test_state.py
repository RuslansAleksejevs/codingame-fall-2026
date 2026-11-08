"""Pure contract tests, no simulator, policy, compilation or games."""
import copy
import unittest
from state import encode, validate


class StateContract(unittest.TestCase):
    def setUp(self):
        self.s = {'schema': 1, 'phase': 'settled_predecision', 'queue': [], 'turn': 4, 'done': False,
                  'surrounded': True, 'score': [8, 2], 'nodes': [[0, 0], [100, 0], [50, 100]],
                  'units': [[1, 0], [1, 0], [1, 0]], 'remaining': [[1, 0], [1, 0], [1, 0]],
                  'edges': [[0, 1], [0, 2], [1, 2]], 'triangles': [[0, 1, 2, 0, 0, 1]],
                  'initial_owners': [0], 'errors': [0, 0]}

    def test_valid(self):
        self.assertTrue(encode(self.s).startswith('CURRICULUM1\n3 4 8 2 0 1'))

    def test_hidden_fields_required(self):
        for key in ('queue', 'remaining', 'initial_owners', 'surrounded'):
            s = copy.deepcopy(self.s)
            del s[key]
            with self.assertRaises(KeyError):
                validate(s)

    def test_wrong_boundaries_rejected(self):
        for key, value in [('queue', ['MOVE']), ('remaining', [[0, 0]] * 3), ('initial_owners', [-1]),
                           ('turn', 200), ('done', True), ('surrounded', False), ('errors', [1, 0])]:
            s = dict(self.s, **{key: value})
            with self.assertRaises(AssertionError):
                validate(s)

    def test_neutral_capture_block_preserved(self):
        self.s['triangles'][0] = [0, 1, 2, -1, 0, 1]
        self.s['initial_owners'] = [-1]
        self.assertTrue(encode(self.s).endswith('0 1 2 -1 -1 0 1'))


if __name__ == '__main__':
    unittest.main()