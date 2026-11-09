"""One <=5min agreed slot: fixed labeldev, four models/exports, diagnostics."""
from job import main
from support import *

for stage in ('labeldev', 'optimize1', 'optimize2'):
    main(stage)
run([PYTHON, '-B', rel(CODE/'coverage_audit.py')], 'coverage-content-audit')