"""Pure synthetic coverage for late stderr and player ownership; no games."""
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from common import OUT
from technical_errors import inspect_failure


class LateLogs(unittest.TestCase):
    def row(self, seat=0, own=True):
        return dict(candidate='search2', opponent='example', seed=62041, seat=seat,
                    outcome='loss', score=-1, opponent_score=7, returncode=0, valid=True,
                    own_action_errors=['timeout'] if own else [],
                    opponent_action_errors=[] if own else ['timeout'], own_plan_us=[1000])

    def inspect(self, row, side, stderr):
        game = {'outputs': {'0': [None, 'WAIT', None], '1': [None, 'WAIT', None]},
                'errors': {'0': [None, None, None], '1': [None, None, None]},
                'tooltips': [{'turn': 3, 'text': f'${side} timeout!'}], 'summaries': ['', 'timeout']}
        game['errors'][str(side)][2] = stderr
        content = gzip.compress(json.dumps(game).encode())
        with patch.object(Path, 'read_bytes', return_value=content):
            return inspect_failure(OUT / 'confirm3', row)

    def test_late_log_not_lost_with_accepted_turn_filter(self):
        result = self.inspect(self.row(), 0, 'turn=24 units=43 triangles=3 plan_us=75244\n')
        late = result['failed_sides'][0]['last_internal_log']
        self.assertEqual(result['own_accepted_turn_plan_us_max'], 1000)
        self.assertEqual(late['internal_plan_us'], 75244)
        self.assertEqual(late['frame'], 2)
        self.assertFalse(late['same_frame_output_recorded'])

    def test_opponent_seat_is_absolute(self):
        result = self.inspect(self.row(seat=1, own=False), 0, 'turn=17 units=4 plan_us=9248\n')
        self.assertFalse(result['failed_sides'][0]['is_own'])
        self.assertEqual(result['failed_sides'][0]['absolute_side'], 0)

    def test_missing_log_not_invented(self):
        result = self.inspect(self.row(), 0, 'unknown failure\n')
        self.assertIsNone(result['failed_sides'][0]['last_internal_log'])


if __name__ == '__main__':
    unittest.main()