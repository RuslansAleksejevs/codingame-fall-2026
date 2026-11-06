#!/usr/bin/env python3
"""Build our bot, the separate benchmark and the local referee launcher."""
import os
from pathlib import Path
import shutil
import subprocess
from run_matches import BASE, REPO, java_home

build = BASE/'code/build'
build.mkdir(exist_ok=True)
for source, target in [('bot.cpp', 'bot'), ('opponents/wood1_port.cpp', 'wood1_port')]:
    subprocess.run(['clang++', '-std=c++17', '-O2', '-Wall', '-Wextra', '-Wpedantic',
                    str(BASE/'code'/source), '-o', str(build/target)], check=True)

jdk = java_home()
env = dict(os.environ, JAVA_HOME=str(jdk), PATH=str(jdk/'bin')+os.pathsep+os.environ['PATH'])
cpfile = REPO/'classpath.txt'
dependencies_present = cpfile.exists() and all(Path(p).exists() for p in cpfile.read_text().strip().split(os.pathsep))
if not (REPO/'target/classes/engine/Board.class').exists() or not dependencies_present:
    maven = os.environ.get('TRYANGLE_MAVEN') or shutil.which('mvn') or '/tmp/tryangle-tools/apache-maven-3.9.9/bin/mvn'
    if not Path(maven).exists():
        raise SystemExit('Set TRYANGLE_MAVEN to Maven 3.9.9/bin/mvn. See code/README.md.')
    cache = os.environ.get('TRYANGLE_MAVEN_REPO', '/tmp/tryangle-tools/m2')
    subprocess.run([maven, '-B', '-Dmaven.repo.local='+cache, '-Dmaven.test.skip=true',
                    'package', 'dependency:build-classpath', '-Dmdep.outputFile='+str(cpfile)],
                   cwd=REPO, env=env, check=True)

classpath = str(REPO/'target/classes')+os.pathsep+cpfile.read_text().strip()
subprocess.run([str(jdk/'bin/javac'), '-cp', classpath, '-d', str(build),
                str(BASE/'code/arena/LocalMatch.java')], env=env, check=True)
print('Built bot, wood1_port and LocalMatch.')
