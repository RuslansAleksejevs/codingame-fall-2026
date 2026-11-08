"""Finite leased stages with retained stdout, failures and actual durations."""
import argparse
from common import *


def main():
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['contracts','terminal-check','freeze','decision','regression','development','confirm1','confirm2','confirm3','confirm4']);args=ap.parse_args()
    if args.stage=='contracts':run([sys.executable,'-B',rel(CODE/'contracts.py')],'contracts')
    elif args.stage in ('freeze','decision'):
        filename='freeze.py' if args.stage=='freeze' else 'analyze.py'
        run([sys.executable,'-B',rel(CODE/filename)],args.stage)
    elif args.stage=='terminal-check':
        run([sys.executable,'-B',rel(CODE/'verify.py'),'regression'],'regression-terminal-verify')
        run([sys.executable,'-B',rel(CODE/'probe_changed.py')],'changed-plan-contracts')
    else:
        try:run([sys.executable,'-B',rel(CODE/'panel.py'),args.stage],args.stage)
        finally:
            if (OUT/args.stage/'matches.jsonl').exists():
                run([sys.executable,'-B',rel(CODE/'verify.py'),args.stage],args.stage+'-verify')


if __name__=='__main__':main()