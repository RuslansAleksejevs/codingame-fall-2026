"""Post-freeze independent raw integrity audit, no candidate or gate changes."""
import gzip
import re
from collections import Counter
from student_common import *
from benchmark_public import NORMAL_ENDS


def quantiles(values):
    return {str(q):float(np.quantile(values,q)) for q in (.5,.95,.99,1)} if values else {}


def main():
    teacher_guard();frozen=json.loads((STUDENT/'freeze.json').read_text())
    for p,h in frozen['identities'].items():assert sha(ROOT/p)==h,p
    data_freeze=json.loads((STUDENT/'data-training-freeze.json').read_text())
    for p,h in data_freeze['identities'].items():assert sha(ROOT/p)==h,p
    decision=json.loads((STUDENT/'decision.json').read_text());groups={};rows=[];bindings={};maps={};missing=[];errors=[]
    timing={c:{'outputs':0,'plan_us':[],'details':[],'post_flush_us':[]} for c in ('student','control','teacher')}
    for number in range(1,5):
        directory=STUDENT/f'confirm{number}';path=directory/'matches.jsonl'
        if not path.exists():continue
        block=[json.loads(s) for s in path.read_text().splitlines()];rows.extend(block)
        verified=json.loads((STUDENT/f'confirm{number}-verification.json').read_text());assert verified['matches_sha256']==sha(path) and verified['passed']
        for r in block:
            c,o,p=r['candidate'],r['opponent'],r['seat'];stem=f'{c}-vs-{o}-seed{r["seed"]}-seat{p}'
            rawpath=directory/(stem+'-raw.json');gzpath=directory/(stem+'.json.gz')
            raw=json.loads(rawpath.read_text());assert clean(raw)==json.loads(gzip.decompress(gzpath.read_bytes()))
            bindings[rel(rawpath)]=sha(rawpath);bindings[rel(gzpath)]=sha(gzpath)
            summaries=''.join(s or '' for s in raw['summaries'])
            own=[m for m in re.findall(r'\$'+str(p)+r': ([^\n]+)',summaries) if m not in NORMAL_ENDS]
            other=[m for m in re.findall(r'\$'+str(1-p)+r': ([^\n]+)',summaries) if m not in NORMAL_ENDS]
            assert own==r['own_action_errors'] and other==r['opponent_action_errors']
            assert raw['scores'].get(str(p))==r['score'] and raw['scores'].get(str(1-p))==r['opponent_score']
            value=0 if own or not r['valid'] or r['returncode'] else (1 if r['score']>r['opponent_score'] else .5 if r['score']==r['opponent_score'] else 0)
            count=groups.setdefault((c,o,p),Counter());count['games']+=1;count['win' if value==1 else 'draw' if value==.5 else 'loss']+=1
            params=dict(s.split('=',1) for s in ''.join(raw['gameParameters']).splitlines() if '=' in s)
            board={k:[list(map(int,s.split(','))) for s in params[k].split('_') if s] for k in ('nodes','units','edges')}
            digest=hashlib.sha256(json.dumps(board,sort_keys=True,separators=(',',':')).encode()).hexdigest()
            assert r['map_content_sha256']==digest and maps.setdefault(r['seed'],digest)==digest
            outputs=sum(bool(s) for s in raw['outputs'][str(p)]);assert outputs==r['own_output_count']
            stderr=''.join(s or '' for s in raw.get('errors',{}).get(str(p),[]));plans=list(map(int,re.findall(r'plan_us=(\d+)',stderr)))
            details=[json.loads(s.split('=',1)[1]) for s in stderr.splitlines() if s.startswith('deadline=')]
            assert plans==r['own_plan_us'] and details==r['deadline_measurements']
            if c=='student':
                turns=list(map(int,re.findall(r'turn=(\d+) ',stderr)))
                if len(plans)!=outputs or turns!=list(range(1,outputs+1)):missing.append({'record':stem,'kind':'package_plan_us','outputs':outputs,'turns':turns})
            else:
                turns=[v['turn'] for v in details]
                if len(details)!=outputs or turns!=list(range(1,outputs+1)):missing.append({'record':stem,'kind':'deadline_measurements','outputs':outputs,'turns':turns})
                for v in details:
                    s=v['search'];assert len(s['values'])==s['complete'] and (s['selected']==0 or s['selected']<s['complete'])
            t=timing[c];t['outputs']+=outputs;t['plan_us'].extend(plans);t['details'].extend(details);t['post_flush_us'].extend(r['post_flush_us'])
            if own or other or not r['valid'] or r['returncode']:errors.append({'record':stem,'own':own,'opponent':other,'valid':r['valid'],'returncode':r['returncode']})
    key=lambda r:tuple(r[k] for k in ('candidate','opponent','seed','seat'))
    assert list(map(key,rows))==list(map(key,frozen['schedule'][:len(rows)])),'Execution differs from fixed ordered schedule'
    assert len(maps)==len(set(maps.values())) and len(rows)==decision['completed_games']
    for (c,o,p),observed in groups.items():
        expected=decision['observed_all_rows'][c][o]['seats'][str(p)]
        for k in ('games','win','draw','loss'):assert observed[k]==expected[k]
    summary={}
    for c,t in timing.items():
        details=t['details'];summary[c]={'outputs':t['outputs'],'plan_us_records':len(t['plan_us']),'plan_us':quantiles(t['plan_us']),
            'deadline_records':len(details),'total_components':{k:quantiles([d[k] for d in details]) for k in ('parse_us','restore_us','flush_us','through_flush_us')},
            'post_flush_us':quantiles(t['post_flush_us']),'changed':sum(d['search']['selected']>0 for d in details),
            'emergency':sum(d['search']['emergency'] for d in details),'budget_stops':sum(d['search']['stopped'] for d in details)}
    integrity=not missing and len(rows)==1680 and len(maps)==40
    save(STUDENT/'timing.json',{'as_of':now(),'candidates':summary,'missing_timing_records':missing,
        'scope':'Original referee enforces50ms; package plan_us excludes parsing/output/startup/scheduling. D16 through_flush excludes time before first score token and referee/platform accounting. Not platform measurements.'})
    save(STUDENT/'raw-audit.json',{'as_of':now(),'raw_score_error_count_hash_order_audit_passed':True,'integrity_passed':integrity,
        'games':len(rows),'maps':len(maps),'technical_records':errors,'missing_timing_records':missing,
        'frozen_inputs_unchanged':True,'freeze_sha256':sha(STUDENT/'freeze.json'),'decision_sha256':sha(STUDENT/'decision.json'),
        'raw_bindings':bindings,'protected':guard(),'budget':budget(),
        'student_admitted':bool(integrity and decision['student_gate_passed'])})
    print(json.dumps({'games':len(rows),'maps':len(maps),'integrity':integrity,'missing_timing':len(missing),
        'technical_records':len(errors),'student_admitted':bool(integrity and decision['student_gate_passed'])}),flush=True)


if __name__=='__main__':main()