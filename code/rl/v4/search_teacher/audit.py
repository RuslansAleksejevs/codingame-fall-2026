"""Read completed branch evidence, including timed search truncation diagnostics."""
import argparse
import gzip
import json
from pathlib import Path
import re
import statistics
from common import OUT, ROOT, check_preserved, now, relative, save, sha


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();preserved=check_preserved()
    stages={};totals=[];search=[];registry={}
    for stage in ('smoke','screen','confirm1','confirm2','confirm3','confirm4'):
        directory=OUT/stage
        if not (OUT/(stage+'-java.json')).exists():continue
        native=json.loads((OUT/(stage+'-native.json')).read_text())
        java=json.loads((OUT/(stage+'-java.json')).read_text())
        assert java['passed'] and not native['native_replay_mismatches']
        assert java['panel_matches_sha256']==sha(directory/'matches.jsonl')==native['panel_matches_sha256']
        rows=[json.loads(line) for line in (directory/'matches.jsonl').read_text().splitlines()]
        counts=[]
        for row in rows:
            key=str(row['seed']);digest=row['map_content_sha256']
            assert key not in registry or registry[key]==digest
            registry[key]=digest
            if row['candidate']!='search2':continue
            name=f'{row["candidate"]}-vs-{row["opponent"]}-seed{row["seed"]}-seat{row["seat"]}.json.gz'
            game=json.loads(gzip.decompress((directory/name).read_bytes()))
            for value in game['errors'][str(row['seat'])]:
                if not value:continue
                for line in value.splitlines():
                    if line.startswith('search='):
                        info=json.loads(line.split('=',1)[1]);counts.append(info);search.append(info)
        stages[stage]={'games':len(rows),'own_error_games':sum(bool(r['own_action_errors']) for r in rows),
            'opponent_error_games':sum(bool(r['opponent_action_errors']) for r in rows),
            'full_java_states':java['full_states_compared'],'transitions':java['joint_transitions'],
            'manifest_sha256':sha(directory/'manifest.json'),'matches_sha256':sha(directory/'matches.jsonl'),
            'search_decisions':len(counts),'budget_stops':sum(d['stopped_by_budget'] for d in counts),
            'changed_plans':sum(d['selected']>0 for d in counts),
            'plan_us_max':max([t for r in rows if r['candidate']=='search2' for t in r['own_plan_us']],default=None)}
        totals += rows
    result={'as_of':now(),'stages':stages,'games':len(totals),'unique_timed_maps':len(registry),
            'preserved':preserved,'own_error_games':sum(bool(r['own_action_errors']) for r in totals),
            'invalid_games':sum(not r['valid'] or r['returncode']!=0 for r in totals),
            'opponent_error_games':sum(bool(r['opponent_action_errors']) for r in totals),
            'search_decisions':len(search),'budget_stops':sum(d['stopped_by_budget'] for d in search),
            'mean_complete_candidates':statistics.mean(d['complete_candidates'] for d in search) if search else None,
            'changed_plans':sum(d['selected']>0 for d in search),
            'candidate_manifest_sha256':sha(OUT/'candidate.json') if (OUT/'candidate.json').exists() else None,
            'dependency_sha256':{relative(ROOT/p):sha(ROOT/p) for p in (
                'code/build/libtryangle.dylib','code/build/libtryangle_league.dylib',
                'code/build/MapGenerator.class','code/build/Oracle.class','code/build/BenchmarkMatch.class')},
            'scope':'Timed original-referee evidence; plan_us is internal elapsed time, not total platform CPU.',
            'external_spend':0}
    save(args.out,result);print(json.dumps(result,indent=2))


if __name__=='__main__':main()