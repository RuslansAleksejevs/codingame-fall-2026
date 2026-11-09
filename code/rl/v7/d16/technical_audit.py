"""Compact early handoff: raw technical checks before independent strength maps."""
from common import *
from analyze import read_rows

def main():
    guard();rows,bindings,timing=read_rows(['regression','development'])
    assert len(rows)==78 and not any(r['own_failure'] for r in rows)
    verifications=[]
    for name,count in [('regression',6),('development',72)]:
        path=OUT/(name+'-verification.json');report=json.loads(path.read_text())
        assert report['passed'] and report['rows']==count and report['matches_sha256']==sha(OUT/name/'matches.jsonl')
        assert report['manifest_sha256']==sha(OUT/name/'manifest.json')
        verifications.append({'path':rel(path),'sha256':sha(path),'games':report['clean_games'],'states':report['states'],'transitions':report['transitions'],'excluded':report['excluded']})
    package=json.loads((OUT/'package.json').read_text());contracts=json.loads((OUT/'contracts.json').read_text())
    assert package['passed'] and contracts['passed'] and sha(ROOT/package['source'])==package['source_sha256']==contracts['source_sha256']
    own=timing['candidate'];assert own and all(x['search']['baseline_complete']==1 and not x['search']['emergency'] and x['through_flush_us']<40000 for x in own)
    report={'as_of':now(),'technical_ready':True,'scope':'Early official technical tests allowed; independent final strength NOT YET measured','source':package['source'],'source_sha256':package['source_sha256'],'source_utf16':package['source_utf16'],'package_sha256':sha(OUT/'package.json'),'contracts_sha256':sha(OUT/'contracts.json'),'new_games':78,'old_map_regression_games':6,'fresh_technical_dev_games':72,'own_control_teacher_technical_failure_games':0,'opponent_failure_games':sum(r['opponent_failure'] for r in rows),'candidate_outputs':len(own),'candidate_through_flush_us_max':max(x['through_flush_us'] for x in own),'candidate_baseline_us_max':max(x['search']['baseline_us'] for x in own),'candidate_emergency_turns':0,'replay':verifications,'raw_bindings':bindings,'official_requests':rel(OUT/'official-test-requests.json'),'official_requests_sha256':sha(OUT/'official-test-requests.json'),'stderr_contract':{'turn_record_prefix':'deadline=','parse':'Concatenate own-agent stderr frames in order, split lines, json.loads(line after deadline=).','baseline_complete':'search.baseline_complete == 1 for every own output','emergency':'search.emergency == 0; never erase or relabel this','budget_stop':'search.stopped == 1 means optional cooperative stop, not an error when baseline_complete == 1','through_flush':'through_flush_us includes post-first-score input, restore, baseline, optional work and stdout flush; <40000 local gate','components':['parse_us','restore_us','search.baseline_us','optional_us','flush_us'],'postflush_marker':'post_flush_us=([0-9.]+)','non_additivity':'Nested search component counters overlap; do not sum them; pre-first-token/startup and final stderr write excluded.'},'budget':budget(),'protected':guard()}
    save(OUT/'technical-readiness.json',report);print(json.dumps(report),flush=True)

if __name__=='__main__':main()