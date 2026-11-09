"""Small pre-freeze checks of point estimates and whole-cluster exclusion."""
import unittest
from analyze import summarize, OPPONENTS, CANDIDATES

class PairedTests(unittest.TestCase):
    def rows(self):
        return [{'candidate':c,'opponent':o,'seed':s,'seat':p,
                 'points':float(c!='control'),'own_failure':False,'opponent_failure':False,
                 'map_content_sha256':str(s)}
                for s in range(1,5) for o in OPPONENTS for c in CANDIDATES for p in (0,1)]
    def test_known_paired_gain(self):
        result=summarize(self.rows(),list(range(1,5)))
        for view in result.values():
            self.assertEqual(view['external_gain']['point_percent'],100)
            self.assertEqual(view['external_gain']['map_95_percent'],[100,100])
            self.assertEqual(view['teacher_retention']['point_percent'],0)
            self.assertTrue(all(view['exploratory_sanity'].values()))
    def test_whole_cluster_exclusion(self):
        rows=self.rows();rows[0]['opponent_failure']=True
        result=summarize(rows,list(range(1,5)))
        self.assertEqual(result['all_games']['external_seeds'],[1,2,3,4])
        clean=result['clean_paired']
        self.assertEqual(clean['external_seeds'],[2,3,4])
        self.assertEqual(clean['per_opponent']['lacoz']['seeds'],[2,3,4])
        self.assertEqual(clean['per_opponent']['khoufou']['seeds'],[1,2,3,4])
    def test_missing_row_not_independent_game(self):
        rows=self.rows();rows.pop()
        result=summarize(rows,list(range(1,5)))
        self.assertEqual(result['all_games']['per_opponent']['b2m']['seeds'],[1,2,3])
    def test_duplicate_rejected(self):
        rows=self.rows();rows.append(rows[0])
        with self.assertRaises(AssertionError):summarize(rows,list(range(1,5)))

if __name__=='__main__':unittest.main()