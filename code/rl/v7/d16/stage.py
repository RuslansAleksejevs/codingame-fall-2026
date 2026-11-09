"""Finite command receipts. One stage per externally limited shared lease."""
from common import *

if __name__=='__main__':
    stage=sys.argv[1]
    if stage=='contracts':run([sys.executable,'-B',rel(CODE/'contracts.py')],stage,1200)
    elif stage=='technical-games':
        run([sys.executable,'-B',rel(CODE/'test_analyze.py')],'analyzer-tests',180)
        run([sys.executable,'-B',rel(CODE/'panel.py'),'regression'],'regression',180)
        run([sys.executable,'-B',rel(CODE/'panel.py'),'development'],'development',900)
        run([sys.executable,'-B',rel(CODE/'technical_audit.py')],'technical-audit',180)
    elif stage=='analyze':run([sys.executable,'-B',rel(CODE/'analyze.py')],stage,180)
    elif stage in ('freeze','confirm1','confirm2','confirm3','confirm4'):
        run([sys.executable,'-B',rel(CODE/'panel.py'),stage],stage,1400)
    else:raise ValueError(stage)