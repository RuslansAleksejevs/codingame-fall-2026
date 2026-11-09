"""Reparse every raw game independently of the panel's metric extractor."""
import gzip
import re
from common import *
NORMAL={'is dominated','no units or triangles left',"can't score any more points"}

def audit(names,report):
    guard();checked=[];failures=[];totals={'games':0,'own_errors':0,'opponent_errors':0,'emergencies':0,'timed_turns':0}
    for name in names:
        path=OUT/name/'matches.jsonl'
        if not path.exists():continue
        rows=[json.loads(line) for line in path.read_text().splitlines()]
        for row in rows:
            stem=f'{row["candidate"]}-vs-{row["opponent"]}-seed{row["seed"]}-seat{row["seat"]}'
            original=OUT/name/(stem+'-raw.json');portable=OUT/name/(stem+'.json.gz')
            raw=json.loads(original.read_text());copy=json.loads(gzip.decompress(portable.read_bytes()))
            assert clean(raw)==copy,(name,stem,'Portable raw differs')
            seat=row['seat'];summaries=''.join(s or '' for s in raw.get('summaries',[]))
            errors={p:[message for who,message in re.findall(r'\$(\d): ([^\n]+)',summaries) if int(who)==p and message not in NORMAL] for p in (0,1)}
            score=raw.get('scores',{});a=score.get(str(seat));b=score.get(str(1-seat))
            referee=[s for s in raw.get('errors',{}).get('referee',[]) if s]
            valid=a is not None and b is not None and not raw.get('failCause') and not referee
            outcome=('win' if a>b else 'loss' if a<b else 'draw') if valid else 'invalid'
            stderr=''.join(s or '' for s in raw.get('errors',{}).get(str(seat),[]))
            deadline=[json.loads(line[len('deadline='):]) for line in stderr.splitlines() if line.startswith('deadline=')]
            outputs=sum(bool(s) for s in raw.get('outputs',{}).get(str(seat),[]))
            post=[float(x) for x in re.findall(r'post_flush_us=([0-9.]+)',stderr)]
            plans=[int(x) for x in re.findall(r'plan_us=(\d+)',stderr)]
            props=dict(line.split('=',1) for line in ''.join(raw['gameParameters']).splitlines() if '=' in line)
            board={k:[list(map(int,x.split(','))) for x in props[k].split('_') if x] for k in ('nodes','units','edges')}
            digest=hashlib.sha256(json.dumps(board,sort_keys=True,separators=(',',':')).encode()).hexdigest()
            expected={'valid':bool(valid),'outcome':outcome,'score':a,'opponent_score':b,'own_action_errors':errors[seat],
                'opponent_action_errors':errors[1-seat],'referee_errors':referee,'fail_cause':raw.get('failCause'),'map_content_sha256':digest,
                'deadline_measurements':deadline,'post_flush_us':post,'own_plan_us':plans,'own_output_count':outputs,
                'emergency':any(d['search']['emergency'] for d in deadline),'timing_coverage_pass':len(deadline)==outputs==len(post),
                'internal_margin_pass':all(d['through_flush_us']<40000 for d in deadline)}
            mismatch=[k for k,v in expected.items() if row[k]!=v]
            if mismatch:failures.append({'stage':name,'game':stem,'fields':mismatch})
            totals['games']+=1;totals['own_errors']+=bool(errors[seat]) or not valid or row['returncode']!=0
            totals['opponent_errors']+=bool(errors[1-seat]);totals['emergencies']+=expected['emergency'];totals['timed_turns']+=len(deadline)
            checked.append({'stage':name,'game':stem,'raw_sha256':sha(original),'portable_sha256':sha(portable)})
    save(OUT/(report+'-raw-audit.json'),{'as_of':now(),'passed':not failures,'totals':totals,'failures':failures,'records':checked,
        'source_sha256':sha(Path(__file__)),'scope':'All original raw and normalized portable files, independently parsed fields, no clean-only filtering'})
    assert not failures,'Raw audit mismatch';print(json.dumps({'audit':report,'passed':True,**totals}),flush=True)

def main():
    stage=sys.argv[1];names=[stage] if stage in ('regression','development') else [f'confirm{i}' for i in range(1,11)]
    audit(names,stage)

if __name__=='__main__':main()