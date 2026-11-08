"""Closing diagnostic, frozen aggregate analysis and independent raw audit."""
from common import *


if __name__=='__main__':
    run([sys.executable,'-B',rel(CODE/'legacy_timing.py')],'legacy-timing')
    run([sys.executable,'-B',rel(CODE/'stage.py'),'decision'],'aggregate-analysis')
    run([sys.executable,'-B',rel(CODE/'final_audit.py')],'final-audit')