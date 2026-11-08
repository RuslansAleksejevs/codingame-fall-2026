"""Synthetic tests only; never reads unopened independent maps."""
import copy
import unittest
from student_analyze import *


def fixture():
    return [dict(r,valid=True,returncode=0,own_action_errors=[],opponent_action_errors=[],
        outcome='loss' if r['candidate']=='control' else 'win',map_content_sha256=str(r['seed'])) for r in schedule()]


class Gates(unittest.TestCase):
    def test_complete_pass(self):self.assertTrue(evaluate(fixture())['student_gate_passed'])
    def test_missing_fails(self):self.assertFalse(evaluate(fixture()[:-1])['student_gate_passed'])
    def test_own_error_counts_as_loss(self):
        rows=fixture();r=next(r for r in rows if r['candidate']=='student');r['own_action_errors']=['Timeout!']
        self.assertEqual(score(r),0);self.assertFalse(evaluate(rows)['student_gate_passed'])
    def test_opponent_excludes_whole_cluster(self):
        rows=fixture();r=rows[0];r['opponent_action_errors']=['Timeout!'];d=evaluate(rows)
        self.assertEqual(d['clean_paired']['per_opponent'][r['opponent']]['complete_maps'],39)
    def test_teacher_retention_fails(self):
        rows=fixture()
        for r in rows:
            if r['candidate']=='student' and r['seed'] in CONFIRM[:3]:r['outcome']='loss'
        d=evaluate(rows);self.assertFalse(d['all_games']['retention_passed']);self.assertFalse(d['student_gate_passed'])
    def test_replay_and_export_required(self):
        self.assertFalse(evaluate(fixture(),verification_pass=False)['student_gate_passed'])
        self.assertFalse(evaluate(fixture(),package_pass=False)['student_gate_passed'])
    def test_duplicate_rows_rejected(self):
        rows=fixture()
        with self.assertRaises(AssertionError):evaluate(rows+[rows[0]])
    def test_map_content_mismatch_rejected(self):
        rows=fixture();rows[0]['map_content_sha256']='different'
        with self.assertRaises(AssertionError):evaluate(rows)


if __name__=='__main__':unittest.main()