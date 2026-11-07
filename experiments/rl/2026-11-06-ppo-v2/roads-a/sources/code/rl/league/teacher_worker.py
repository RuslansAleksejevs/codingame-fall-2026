#!/usr/bin/env python3
"""Reuse imports while resetting the unchanged public teacher for each training game."""
import argparse
import gc
import hashlib
from pathlib import Path
import sys

class EndGame(EOFError):pass

def main():
    parser=argparse.ArgumentParser();parser.add_argument('source',type=Path);args=parser.parse_args()
    source=args.source.read_bytes();code=compile(source,str(args.source),'exec')
    def read():
        line=sys.stdin.readline()
        if not line or line.rstrip('\n')=='@END':raise EndGame()
        return line.rstrip('\n')
    print('@READY',flush=True)
    while True:
        line=sys.stdin.readline()
        if not line or line.rstrip('\n')=='@STOP':break
        if not line.startswith('@BEGIN '):raise RuntimeError('Expected a new game marker')
        scope={'__name__':'__main__','__file__':str(args.source),'input':read}
        try:exec(code,scope,scope)
        except EndGame:pass
        finally:
            scope.clear();gc.enable();gc.collect()
        print('@READY',flush=True)
if __name__=='__main__':main()
