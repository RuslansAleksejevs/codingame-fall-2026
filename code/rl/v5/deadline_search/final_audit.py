"""Independent raw-outcome/integrity audit after the fixed series, no new games."""
import gzip
import re
from collections import Counter
from common import *
from benchmark_public import NORMAL_ENDS


def main():
    preserved=guard();freeze=json.loads((OUT/'freeze.json').read_text());decision=json.loads((OUT/'decision.json').read_text())
    for p,h in {**freeze['sources'],**freeze['weights'],**freeze['binaries'],**freeze['dependencies']}.items():
        assert sha(ROOT/p)==h,'Frozen input changed: '+p
    assert sha(OUT/'PROTOCOL.md')==freeze['protocol_sha256']
    assert sha(CODE/'analyze.py')==freeze['analyzer_sha256']
    groups={};count=0;turns=0;raw_bindings={};missing=[];technical=[];map_hashes={};java_states=java_transitions=0
    for stage in ['regression','development',*[f'confirm{i}' for i in range(1,5)]]:
        directory=OUT/stage;path=directory/'matches.jsonl'
        if not path.exists():continue
        rows=[json.loads(s) for s in path.read_text().splitlines()]
        verification=OUT/(stage+'-final-verification.json' if stage in ('regression','development') else stage+'-verification.json')
        report=json.loads(verification.read_text());assert report['passed'] and report['matches_sha256']==sha(path)
        assert report['rows']==len(rows)
        if stage.startswith('confirm'):
            java_states+=report['states'];java_transitions+=report['transitions']
        for row in rows:
            stem=f'{row["candidate"]}-vs-{row["opponent"]}-seed{row["seed"]}-seat{row["seat"]}'
            original=directory/(stem+'-raw.json');compressed=directory/(stem+'.json.gz')
            raw=json.loads(original.read_text());copy=json.loads(gzip.decompress(compressed.read_bytes()))
            assert clean(raw)==copy,'Raw portable copy changed data'
            raw_bindings[rel(original)]=sha(original);raw_bindings[rel(compressed)]=sha(compressed)
            p=row['seat'];summaries=''.join(s or '' for s in raw['summaries'])
            errors=[m for m in re.findall(r'\$'+str(p)+r': ([^\n]+)',summaries) if m not in NORMAL_ENDS]
            other_errors=[m for m in re.findall(r'\$'+str(1-p)+r': ([^\n]+)',summaries) if m not in NORMAL_ENDS]
            assert errors==row['own_action_errors'] and other_errors==row['opponent_action_errors']
            assert raw['scores'][str(p)]==row['score'] and raw['scores'][str(1-p)]==row['opponent_score']
            output_count=sum(bool(s) for s in raw['outputs'][str(p)])
            assert output_count==row['own_output_count']
            measurements=row['deadline_measurements'];turn_ids=[m['turn'] for m in measurements]
            if len(measurements)!=output_count or turn_ids!=list(range(1,output_count+1)):
                missing.append({'stage':stage,'game':stem,'outputs':output_count,'turn_ids':turn_ids})
            for m in measurements:
                stats=m['search'];assert len(stats['values'])==stats['complete']
                assert stats['selected']==0 or stats['selected']<stats['complete']
            if errors or other_errors:technical.append({'stage':stage,'game':stem,'own':errors,'opponent':other_errors})
            params=dict(s.split('=',1) for s in ''.join(raw['gameParameters']).splitlines() if '=' in s)
            board={k:[list(map(int,r.split(','))) for r in params[k].split('_') if r] for k in ('nodes','units','edges')}
            digest=hashlib.sha256(json.dumps(board,sort_keys=True,separators=(',',':')).encode()).hexdigest()
            assert digest==row['map_content_sha256']
            if stage.startswith('confirm'):
                key=(row['candidate'],row['opponent'],p)
                group=groups.setdefault(key,Counter())
                value=0 if errors or not row['valid'] or row['returncode'] else (1 if row['score']>row['opponent_score'] else .5 if row['score']==row['opponent_score'] else 0)
                group['win' if value==1 else 'draw' if value==.5 else 'loss']+=1
                group['games']+=1;count+=1;turns+=len(measurements)
                old=map_hashes.setdefault(row['seed'],digest);assert old==digest
    assert count==decision['completed_games']
    for (candidate,opponent,seat),counts in groups.items():
        expected=decision['all_games']['per_opponent'][opponent]['candidates'][candidate]['seats'][str(seat)]['results']
        # Complete-series comparisons are exact. Partial series cannot satisfy admission.
        if decision['complete_fixed_series']:
            for k in ('win','draw','loss','games'):assert counts[k]==expected[k],(candidate,opponent,seat,k)
    integrity=not missing and count==1120 and len(map_hashes)==40 and len(set(map_hashes.values()))==40
    result={'as_of':now(),'classification':'PROJECT_REPORTED','raw_outcome_count_audit_passed':True,
        'integrity_gate_passed':integrity,'missing_timing_records':missing,'confirmation_games':count,
        'confirmation_raw_timing_turns':turns,'confirmation_maps':len(map_hashes),'java_states':java_states,
        'java_transitions':java_transitions,'technical_records':technical,
        'raw_groups':[{'candidate':c,'opponent':o,'seat':s,**dict(v)} for (c,o,s),v in sorted(groups.items())],
        'teacher_admitted':bool(integrity and decision['teacher_gate_passed']),
        'frozen_source_identity_unchanged':True,'freeze_sha256':sha(OUT/'freeze.json'),
        'decision_sha256':sha(OUT/'decision.json'),'protected':preserved,'raw_bindings':raw_bindings,
        'budget':budget(),'scope':'Independent raw score/error/count audit; frozen bootstrap is not independently reimplemented.'}
    save(OUT/'final-audit.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('raw_groups','raw_bindings')},indent=2))


if __name__=='__main__':main()