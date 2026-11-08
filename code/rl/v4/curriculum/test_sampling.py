"""Small synthetic tests: no games, training, builds, timing or benchmark load."""
import unittest
import numpy as np
from train import completed_prefix, scheduled


class SamplingContract(unittest.TestCase):
    def test_identical_opponent_map_and_seat_stream(self):
        bank = [{'category': c, 'seat': s} for c in ('loss', 'win', 'fresh') for s in (0, 1)]
        restored = total = 0
        for iteration in range(100):
            a = scheduled(202611081, iteration, 2000, bank, 0.)
            b = scheduled(202611081, iteration, 2000, bank, .15)
            self.assertTrue(np.array_equal(a[:, :3], b[:, :3]))
            self.assertTrue(np.all(a[:, 3] == -1))
            self.assertTrue(np.all(b[b[:, 1] == -2, 3] == -1))
            restored += int(np.sum(b[:, 3] >= 0))
            total += len(b)
        self.assertLess(.12, restored / total)
        self.assertLess(restored / total, .18)

    def test_trim_only_after_terminal(self):
        n = 9
        data = {'x': np.ones((n, 128), np.float32), 'value_x': np.ones((n, 128), np.float32),
                'old_logp': np.zeros(n), 'old_entropy': np.zeros(n), 'reward': np.array([0, 1, 0, 0, -1, 0, 0, 0, 1]),
                'group_offsets': np.arange(n + 1), 'turn_offsets': np.arange(n + 1), 'choices': np.zeros(n, np.int32),
                'episode_offsets': np.array([0, 2, 5, 9]), 'game_ids': np.array([0, 0, 1, 1, 1, 2, 2, 2, 2]),
                'players': np.zeros(n, np.int32), 'stats': {'games': 3, 'outcomes': [[0, 0, -1, 1, 2], [0, 0, 0, -1, 3], [0, 0, -1, 1, 4]]}}
        for target, expected in ((1, 2), (2, 2), (3, 5), (5, 5), (6, 9), (9, 9), (10, 9)):
            cut = completed_prefix(data, target)
            self.assertEqual(len(cut['old_logp']), expected)
            self.assertNotEqual(cut['reward'][-1], 0)
            self.assertEqual(cut['episode_offsets'][-1], expected)
            self.assertEqual(cut['turn_offsets'][-1], len(cut['choices']))
            self.assertEqual(cut['group_offsets'][-1], len(cut['x']))


if __name__ == '__main__':
    unittest.main()