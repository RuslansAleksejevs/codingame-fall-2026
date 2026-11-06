#!/usr/bin/env python3
"""Compile the reviewed public Java bot and benchmark launcher; verify exact source copies."""
import hashlib
import json
from pathlib import Path
import subprocess
from run_matches import BASE, REPO, java_home

jdk=java_home()
public=BASE/'code/opponents/public'
for folder, filename in [('lacoz-7f190183','bot.py'),('khoufou-372c1cd6','Player.java')]:
    root=public/folder
    meta=json.loads((root/'PROVENANCE.json').read_text())
    data=(root/filename).read_bytes()
    assert hashlib.sha256(data).hexdigest()==meta['sha256'], f'Changed upstream source: {filename}'
    assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==meta['github_blob_sha']
k=public/'khoufou-372c1cd6'
(k/'build').mkdir(exist_ok=True)
subprocess.run([str(jdk/'bin/javac'),'-d',str(k/'build'),str(k/'Player.java')],check=True)
cp=str(REPO/'target/classes')+':'+(REPO/'classpath.txt').read_text().strip()
subprocess.run([str(jdk/'bin/javac'),'-cp',cp,'-d',str(BASE/'code/build'),str(BASE/'code/arena/BenchmarkMatch.java')],check=True)
py=BASE/'code/arena/.venv-lacoz/bin/python'
if not py.exists():
    raise SystemExit('Create code/arena/.venv-lacoz and install requirements-public.txt; see code/opponents/public/README.md')
subprocess.run([str(py),'-c','import numpy,scipy.optimize; print("NumPy",numpy.__version__,"SciPy",scipy.__version__)'],check=True)
print('Both source hashes verified; Java bot and launcher compiled.')
