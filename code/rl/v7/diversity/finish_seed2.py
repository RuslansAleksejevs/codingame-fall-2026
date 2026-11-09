"""Complete only the two not-yet-trained prescribed models; never retrain seed1."""
from support import *

for arm in ('narrow2', 'broad2'):
    assert not (OUT/'models'/arm).exists()
    run([PYTHON, '-B', rel(CODE/'train.py'), 'train', arm], arm+'-train-only', 650)