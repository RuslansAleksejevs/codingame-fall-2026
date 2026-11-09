"""A1 applies mechanically to both seats; no outcomes enter exclusion."""
import unittest
from collect import exclude_maps


class Exclusion(unittest.TestCase):
    def rows(self):
        return [{'seed': s, 'seat': p, 'valid': True, 'returncode': 0, 'own_action_errors': [],
                 'opponent_action_errors': [], 'outcome': 'win' if p == 0 else 'loss'}
                for s in (73001, 73017) for p in (0, 1)]

    def test_whole_map(self):
        rows = self.rows(); rows[0]['opponent_action_errors'] = ['timeout']
        retained, excluded = exclude_maps(rows)
        self.assertEqual(excluded, [73001]); self.assertEqual([r['seed'] for r in retained], [73017, 73017])

    def test_own_still_stops(self):
        rows = self.rows(); rows[0]['own_action_errors'] = ['timeout']
        with self.assertRaises(AssertionError): exclude_maps(rows)

    def test_outcomes_irrelevant(self):
        rows = self.rows(); rows[-1]['opponent_action_errors'] = ['timeout']
        a = exclude_maps(rows)
        for row in rows: row['outcome'] = 'draw'
        b = exclude_maps(rows)
        self.assertEqual(a[1], b[1]); self.assertEqual([r['seed'] for r in a[0]], [r['seed'] for r in b[0]])


if __name__ == '__main__': unittest.main()