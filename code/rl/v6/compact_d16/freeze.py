"""Freeze the complete schedule before generating any corresponding fresh maps."""
from common import *
from panel import identities,schedule
from final_audit import audit

def main():
    guard();stage=sys.argv[1];assert stage in ('development','final')
    package=json.loads((OUT/'package-attempt2.json').read_text());assert package['source_utf16']<=98000
    assert sha(ROOT/package['source'])==package['source_sha256']
    contracts=json.loads((OUT/'contracts.json').read_text());assert contracts['passed'] and contracts['saved_games']>=100
    regression=json.loads((OUT/'regression-verification.json').read_text());assert regression['passed'] and regression['clean_games']==6
    if stage=='development':
        audit(['regression'],'regression')
        raw=json.loads((OUT/'regression-raw-audit.json').read_text());assert raw['totals']['own_errors']==raw['totals']['emergencies']==0
        run([sys.executable,'-B',CODE/'test_analyze.py'],'analyzer-tests-before-development',120)
    else:
        assert json.loads((OUT/'development-decision.json').read_text())['gate_passed']
        assert json.loads((OUT/'development-raw-audit.json').read_text())['passed']
        run([sys.executable,'-B',CODE/'test_analyze.py'],'analyzer-tests-before-final',120)
    seeds=list(range(71001,71013)) if stage=='development' else list(range(40001,40101))
    save(OUT/(stage+'-freeze.json'),{'as_of':now(),'stage':stage,'identities':identities(),'protocol_sha256':sha(OUT/'PROTOCOL.md'),
        'source_sha256':package['source_sha256'],'source_utf16':package['source_utf16'],'selected_precision':9,
        'maps_generated':False,'seeds':seeds,'schedule':schedule(seeds),'games':len(seeds)*42,'bootstrap_seed':20261109,
        'technical_evidence':{rel(p):sha(p) for p in (OUT/'contracts.json',OUT/'regression-verification.json',OUT/'regression-raw-audit.json')},
        'requires_coordinator_release_before_generation':stage=='final','reserve65001_65040':'CLOSED','budget':budget()})
    print(json.dumps({'frozen':stage,'sha256':sha(OUT/(stage+'-freeze.json')),'games':len(seeds)*42}),flush=True)

if __name__=='__main__':main()