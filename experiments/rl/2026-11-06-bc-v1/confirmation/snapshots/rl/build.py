#!/usr/bin/env python3
"""Build native simulation and a differential oracle against the pinned source."""
import subprocess
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from run_matches import BASE, REPO, java_home

def main():
    build=BASE/'code/build';build.mkdir(exist_ok=True)
    subprocess.run(['clang++','-std=c++17','-O3','-Wall','-Wextra','-shared','-fPIC',str(BASE/'code/rl/sim/api.cpp'),'-o',str(build/'libtryangle.dylib')],check=True)
    subprocess.run(['clang++','-std=c++17','-O3','-Wall','-Wextra',str(BASE/'code/rl/export/bot.cpp'),'-o',str(build/'bc-bot')],check=True)
    cp=str(REPO/'target/classes')+':'+(REPO/'classpath.txt').read_text().strip()
    subprocess.run([str(java_home()/'bin/javac'),'-cp',cp,'-d',str(build),str(BASE/'code/rl/sim/Oracle.java')],check=True)
if __name__=='__main__':main()
