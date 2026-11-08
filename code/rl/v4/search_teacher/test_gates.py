"""Small synthetic tests only; no simulator, maps, network or timing loads."""
import unittest
from unittest.mock import patch
import gates
from common import checked_seeds


def rows(n=40):
    return [{'candidate': c, 'opponent': o, 'seed': s, 'seat': p,
             'outcome': 'win' if c=='search2' else 'loss', 'valid': True,
             'returncode': 0, 'own_action_errors': [], 'opponent_action_errors': [],
             'map_content_sha256': str(s)}
            for s in range(62019, 62019+n) for c in ('greedy', 'search2')
            for o in (*gates.EXTERNAL, 'league3m', 'v6', 'bc') for p in (0, 1)]


class Gates(unittest.TestCase):
    @patch('gates.interval', return_value=[60, 100])
    def test_pass(self, _):
        self.assertTrue(gates.evaluate(rows(), True)['teacher_strength_gate_passed'])

    @patch('gates.interval', return_value=[0, 100])
    def test_zero_bound_does_not_pass(self, _):
        self.assertFalse(gates.evaluate(rows(), True)['teacher_strength_gate_passed'])

    @patch('gates.interval', return_value=[60, 100])
    def test_own_failure_rejects(self, _):
        data = rows(); data[0]['own_action_errors'] = ['timeout']
        self.assertFalse(gates.evaluate(data, True)['teacher_strength_gate_passed'])

    @patch('gates.interval', return_value=[60, 100])
    def test_low_coverage_rejects(self, _):
        data = rows()
        for r in data:
            if r['seed'] < 62024: r['opponent_action_errors'] = ['timeout']
        result = gates.evaluate(data, True)
        self.assertEqual(result['complete_composite_maps'], 35)
        self.assertFalse(result['teacher_strength_gate_passed'])

    @patch('gates.interval', return_value=[50, 100])
    def test_direct_boundary_rejects(self, _):
        self.assertFalse(gates.evaluate(rows(), True)['teacher_strength_gate_passed'])

    @patch('gates.interval', return_value=[60, 100])
    def test_guard_regression_rejects(self, _):
        data=rows()
        for r in data:
            if r['opponent']=='bc': r['outcome']='loss' if r['candidate']=='search2' else 'win'
        self.assertFalse(gates.evaluate(data, True)['teacher_strength_gate_passed'])

    @patch('gates.interval', return_value=[60, 100])
    def test_no_early_confirmation(self, _):
        self.assertFalse(gates.evaluate(rows(39), True)['teacher_strength_gate_passed'])

    def test_map_identity_required(self):
        data=rows();data[0]['map_content_sha256']='different'
        with self.assertRaises(AssertionError): gates.evaluate(data, True)

    def test_duplicate_and_incomplete_reject(self):
        data = rows()
        for bad in (data+data[:1], data[1:]):
            with self.assertRaises(AssertionError): gates.evaluate(bad, True)

    def test_reserved_seeds_reject(self):
        for seed in (40001, 40100, 65001, 65040, 61999):
            with self.assertRaises(AssertionError): checked_seeds([seed])


if __name__ == '__main__':
    unittest.main()