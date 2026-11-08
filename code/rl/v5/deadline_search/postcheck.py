"""Optional additional audits, never modifies frozen candidate/gate sources."""
from common import *


if __name__=='__main__':
    run([sys.executable,'-B',rel(CODE/'control_parity.py')],'control-parity')