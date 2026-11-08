"""Separate undiscounted outcome ordering from discounted speed-of-win ordering."""
import gzip
import json
import statistics
from common import OUT, now, save, sha
from rl.eval.analyze import interval


def aggregate(values):
    return .5*statistics.mean(values)+.5*min(values)


def choose(values):
    selected=0
    for i,v in enumerate(values[1:],1):
        if v>values[0]+.02 and v>values[selected]:selected=i
    return selected


def main():
    path=OUT/'diagnostic/cases.json.gz'
    cases=json.loads(gzip.decompress(path.read_bytes()))
    metrics={}
    for index,depth in enumerate((1,2,4,8)):
        model_changes=[{'improved':0,'worsened':0,'equal':0} for _ in range(3)]
        concordant=comparable=changed=0;deltas={};discounted={};better=worse=equal=0
        for case in cases:
            plans=case['plans']
            predictions=[aggregate([m['short_values'][index] for m in p['models']]) for p in plans]
            outcomes=[aggregate([m['terminal'] for m in p['models']]) for p in plans]
            values=[aggregate([m['discounted_terminal'] for m in p['models']]) for p in plans]
            selected=choose(predictions);changed+=selected!=0
            delta=outcomes[selected]-outcomes[0]
            deltas.setdefault(case['seed'],[]).append(delta)
            discounted.setdefault(case['seed'],[]).append(values[selected]-values[0])
            if selected:
                better+=delta>1e-8;worse+=delta<-1e-8;equal+=abs(delta)<=1e-8
                for m in range(3):
                    d=plans[selected]['models'][m]['terminal']-plans[0]['models'][m]['terminal']
                    model_changes[m]['improved' if d>0 else 'worsened' if d<0 else 'equal']+=1
            for i in range(len(plans)):
                for j in range(i):
                    d=outcomes[i]-outcomes[j]
                    if abs(d)>1e-8:
                        comparable+=1;concordant+=(predictions[i]-predictions[j])*d>0
        # interval() uses percentage units; undo that scaling for signed ±1 values.
        metrics[str(depth)]={'changed_roots':changed,'raw_outcome_better_roots':better,
            'raw_outcome_worse_roots':worse,'raw_outcome_equal_roots':equal,
            'raw_outcome_pairwise_concordant':concordant,'raw_outcome_pairwise_non_tied':comparable,
            'raw_outcome_mean_robust_delta':statistics.mean(sum(deltas.values(),[])),
            'raw_outcome_delta_map95':[x/100 for x in interval(list(deltas.values()))],
            'discounted_delta_map95':[x/100 for x in interval(list(discounted.values()))],
            'per_model_undiscounted_changes':model_changes}
    result={'as_of':now(),'source_sha256':sha(path),'maps':len({c['seed'] for c in cases}),
        'metrics':metrics,'method':'Whole-map bootstrap, all both-seat roots kept in each cluster, 10000 resamples/seed20261106.',
        'caveat':'Six diagnostic maps and three in-teacher response policies only. Not external strength or optimal value.'}
    save(OUT/'diagnostic/raw-outcome-summary.json',result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()