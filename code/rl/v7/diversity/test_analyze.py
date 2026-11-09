"""Artificial whole-map/technical/gate tests, no generated maps."""
import unittest
from analyze import *
from collect import turns


class Contracts(unittest.TestCase):
    def rows(self, n=16):
        return [{'candidate': a, 'opponent': o, 'seed': s, 'seat': p, 'valid': True, 'returncode': 0,
            'own_action_errors': [], 'opponent_action_errors': [], 'outcome': 'win' if a.startswith('broad') else 'loss'}
            for a in ARMS for o in OPPONENTS for s in range(n) for p in (0, 1)]

    def test_positive(self):
        result = summarize(self.rows(), list(range(16)), ARMS)
        self.assertTrue(promise(result)); self.assertEqual(result['all']['broad-minus-narrow']['ci95'], [1., 1.])

    def test_tie_not_promise(self):
        rows = self.rows()
        for row in rows: row['outcome'] = 'win'
        self.assertFalse(promise(summarize(rows, list(range(16)), ARMS)))

    def test_incomplete(self):
        result = summarize(self.rows()[:-1], list(range(16)), ARMS)
        self.assertFalse(result['complete']); self.assertFalse(promise(result))

    def test_technical(self):
        rows = self.rows(); rows[0]['own_action_errors'] = ['timeout']
        result = summarize(rows, list(range(16)), ARMS)
        self.assertEqual(len(result['clean']['maps']), 15); self.assertFalse(promise(result))

    def test_whole_map(self):
        rows = self.rows()
        for row in rows: row['outcome'] = 'win' if row['seat'] == 0 else 'loss'
        result = summarize(rows, list(range(16)), ARMS)
        self.assertEqual(result['all']['external']['broad1']['ci95'], [.5, .5])

    def test_turns(self):
        self.assertEqual(turns(1), [0]); self.assertEqual(turns(10), list(range(10)))
        self.assertEqual(len(turns(200)), 16); self.assertEqual(turns(200)[-1], 199)


if __name__ == '__main__': unittest.main()