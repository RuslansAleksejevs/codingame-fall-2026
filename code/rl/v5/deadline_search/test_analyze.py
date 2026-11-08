"""Pure preregistered gate tests, before independent outcomes."""
import unittest
from analyze import evaluate, strategic_pass
from panel import schedule


def synthetic():
    return [dict(r,valid=True,returncode=0,own_action_errors=[],opponent_action_errors=[],
        outcome='win' if r['candidate']=='search' else 'loss',map_content_sha256=str(r['seed']))
        for r in schedule(list(range(70101,70141)))]


class Gates(unittest.TestCase):
    def test_positive(self):self.assertTrue(evaluate(synthetic())['teacher_gate_passed'])
    def test_own_failure(self):
        rows=synthetic();rows[0]['own_action_errors']=['timeout'];r=evaluate(rows)
        self.assertFalse(r['teacher_gate_passed']);self.assertEqual(r['own_control_error_games'],1)
    def test_missing(self):self.assertFalse(evaluate(synthetic()[:-1])['teacher_gate_passed'])
    def test_duplicate(self):
        rows=synthetic()
        with self.assertRaises(AssertionError):evaluate(rows+[rows[0]])
    def test_replay(self):self.assertFalse(evaluate(synthetic(),False)['teacher_gate_passed'])
    def test_strict_boundaries(self):
        d={'external_gain':{'point_percent':5.,'map_95_percent':[.01,10]},
           'direct_league3m':{'point_percent':55.,'map_95_percent':[50.01,70]},
           'per_opponent':{'a':{'gain':{'point_percent':-5}}}}
        self.assertTrue(strategic_pass(d));d['external_gain']['map_95_percent'][0]=0
        self.assertFalse(strategic_pass(d));d['external_gain']['map_95_percent'][0]=.01
        d['direct_league3m']['map_95_percent'][0]=50;self.assertFalse(strategic_pass(d))
        d['direct_league3m']['map_95_percent'][0]=50.01;d['per_opponent']['a']['gain']['point_percent']=-5.001
        self.assertFalse(strategic_pass(d))
    def test_opponent_failure_kept_and_excluded(self):
        rows=synthetic();rows[0]['opponent_action_errors']=['timeout'];r=evaluate(rows)
        opponent=rows[0]['opponent'];self.assertEqual(r['opponent_error_games'],1)
        self.assertEqual(r['all_games']['per_opponent'][opponent]['complete_maps'],40)
        self.assertEqual(r['clean_paired']['per_opponent'][opponent]['complete_maps'],39)


if __name__=='__main__':unittest.main()