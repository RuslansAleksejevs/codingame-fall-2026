"""Synthetic prospective tests; never read game outcomes."""
import copy
import unittest
from analyze import *

def fixture(n=12):
    return [{**r,'valid':True,'returncode':0,'own_action_errors':[],'opponent_action_errors':[],
        'outcome':'loss' if r['candidate']=='control' else 'win','map_content_sha256':f'synthetic{r["seed"]}',
        'emergency':False,'timing_coverage_pass':True,'internal_margin_pass':True} for r in schedule(list(range(n)))]

def run(rows,n=12,stage='development',replay=True,raw=True,package=True):return evaluate(rows,list(range(n)),stage,replay,raw,package)

class Tests(unittest.TestCase):
    def test_constant(self):self.assertEqual(estimate([.5]*12)['map_95_percent'],[50.,50.])
    def test_pass(self):self.assertTrue(run(fixture())['gate_passed'])
    def test_pair_seats(self):
        rows=fixture()
        for r in rows:
            if r['candidate']=='candidate':r['outcome']='win' if r['seat'] else 'loss'
        d=run(rows);self.assertEqual(d['all_games']['direct_league3m']['map_95_percent'],[50.,50.]);self.assertFalse(d['gate_passed'])
    def test_whole_cluster_exclusion(self):
        rows=fixture();rows[0]['opponent_action_errors']=['synthetic'];d=run(rows)
        self.assertEqual(d['clean_paired']['external_gain']['maps'],11);self.assertTrue(d['gate_passed'])
        for c in CANDIDATES:self.assertEqual(d['clean_paired']['per_opponent'][rows[0]['opponent']]['candidates'][c]['results']['games'],22)
    def test_composite_intersection(self):
        rows=fixture()
        for s,o in [(0,'lacoz'),(1,'khoufou2')]:next(r for r in rows if r['seed']==s and r['opponent']==o)['opponent_action_errors']=['synthetic']
        self.assertFalse(run(rows)['checks']['clean_coverage'])
    def test_failures_and_partial(self):
        self.assertFalse(run(fixture()[:-1])['gate_passed']);self.assertFalse(run(fixture(),replay=False)['gate_passed'])
        self.assertFalse(run(fixture(),raw=False)['gate_passed']);self.assertFalse(run(fixture(),package=False)['gate_passed'])
        rows=fixture();rows[0]['emergency']=True;self.assertEqual(points(rows[0]),0);self.assertFalse(run(rows)['gate_passed'])
    def test_identities(self):
        rows=fixture()
        with self.assertRaises(AssertionError):run(rows+[rows[0]])
        for r in rows:r['map_content_sha256']='duplicate'
        with self.assertRaises(AssertionError):run(rows)
    def test_final_strict_boundaries(self):
        view=run(fixture())['all_games'];self.assertTrue(all(gates(view,'final').values()))
        view['external_gain']={'point_percent':3.,'map_95_percent':[0.,6.]};self.assertFalse(gates(view,'final')['external_lower_positive'])
        view['direct_b2m']={'point_percent':55.,'map_95_percent':[50.,60.]};self.assertFalse(gates(view,'final')['b2m_lower50'])
        view['external_candidate_minus_teacher']={'point_percent':-2.,'map_95_percent':[-5.,1.]};self.assertFalse(gates(view,'final')['retention_lower_minus5'])
    def test_final_coverage(self):
        rows=fixture(20);rows[0]['opponent_action_errors']=['synthetic'];self.assertTrue(run(rows,20,'final')['gate_passed'])
        next(r for r in rows if r['seed']==1)['opponent_action_errors']=['synthetic'];self.assertFalse(run(rows,20,'final')['gate_passed'])

if __name__=='__main__':unittest.main(verbosity=2)