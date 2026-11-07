#!/usr/bin/env python3
"""Build the separate league library without replacing a running v1 collector."""
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from run_matches import BASE,REPO,java_home
subprocess.run(['clang++','-std=c++17','-O3','-Wall','-Wextra','-Wpedantic','-shared','-fPIC','-pthread',str(BASE/'code/rl/league/rollout_league.cpp'),'-o',str(BASE/'code/build/libtryangle_league.dylib')],check=True)
cp=str(BASE/'code/build')+':'+str(REPO/'target/classes')+':'+(REPO/'classpath.txt').read_text().strip()
subprocess.run([str(java_home()/'bin/javac'),'-cp',cp,'-d',str(BASE/'code/build'),str(BASE/'code/rl/league/InputOracle.java')],check=True)
