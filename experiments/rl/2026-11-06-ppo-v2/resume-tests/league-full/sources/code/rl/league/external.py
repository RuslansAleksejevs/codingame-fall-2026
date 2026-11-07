"""Persistent isolated teacher processes; per-game globals reset by the worker."""
import ctypes as C
import hashlib
import json
from pathlib import Path
import select
import subprocess
import time
from rl.league.rollout import EXTERNAL,LIB,ROOT

class Teachers:
    def __init__(self,workers,out):
        self.processes=[];self.files=[];self.active=[False]*workers;self.buffers=[None]*workers
        self.errors=[];self.calls=0;self.seconds=0.;self.games=0;self.recent=[[] for _ in range(workers)];self.out=Path(out);self.out.mkdir(parents=True,exist_ok=True)
        source=ROOT/'code/opponents/public/lacoz-7f190183/bot.py'
        provenance=json.loads(source.with_name('PROVENANCE.json').read_text())
        assert hashlib.sha256(source.read_bytes()).hexdigest()==provenance['sha256']
        for w in range(workers):
            log=(self.out/f'worker-{w}.log').open('w');self.files.append(log)
            process=subprocess.Popen([str(ROOT/'code/arena/.venv-lacoz/bin/python'),'-u',str(ROOT/'code/rl/league/teacher_worker.py'),str(source)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=log,text=True,bufsize=1,env=self.environment())
            self.processes.append(process);assert self.read(w,10)=='@READY'
        self.callback=EXTERNAL(self.dispatch)
    @staticmethod
    def environment():
        import os
        env=dict(os.environ);env.update({'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','VECLIB_MAXIMUM_THREADS':'1'});return env
    def read(self,w,timeout):
        process=self.processes[w]
        if not select.select([process.stdout],[],[],timeout)[0]:raise TimeoutError(f'Training teacher worker {w} stalled')
        line=process.stdout.readline()
        if not line:raise RuntimeError(f'Training teacher worker {w} exited: {process.poll()}')
        return line.rstrip('\n')
    def dispatch(self,w,game,turn,raw):
        try:
            process=self.processes[w]
            if turn<0:
                process.stdin.write('@END\n');process.stdin.flush();assert self.read(w,5)=='@READY';self.active[w]=False;answer='OK';self.games+=1
            else:
                observation=raw.decode()
                if turn==0:
                    assert not self.active[w];self.active[w]=True;self.recent[w]=[];process.stdin.write(f'@BEGIN {game}\n')
                else:assert self.active[w]
                start=time.monotonic();process.stdin.write(observation);process.stdin.flush();answer=self.read(w,10 if turn==0 else 2)
                assert answer and not answer.startswith('@'),answer
                self.calls+=1;self.seconds+=time.monotonic()-start
                self.recent[w].append({'game':game,'turn':turn,'observation':observation,'actions':answer})
            self.buffers[w]=C.create_string_buffer(answer.encode());return C.addressof(self.buffers[w])
        except Exception as exc:
            self.errors.append({'worker':w,'game':game,'turn':turn,'error':repr(exc)})
            (self.out/f'failure-worker-{w}.json').write_text(json.dumps({'error':self.errors[-1],'recent_game':self.recent[w]},indent=2)+'\n');return None
    def attach(self,collector):LIB.league_set_external(collector.ptr,self.callback)
    def metrics(self):return {'games':self.games,'calls':self.calls,'summed_call_seconds':self.seconds,'errors':self.errors,'teacher_source_sha256':hashlib.sha256((ROOT/'code/opponents/public/lacoz-7f190183/bot.py').read_bytes()).hexdigest()}
    def close(self):
        for w,p in enumerate(self.processes):
            if p.poll() is None:
                try:
                    if self.active[w]:p.stdin.write('@END\n')
                    p.stdin.write('@STOP\n');p.stdin.flush();p.wait(timeout=10)
                except (BrokenPipeError,subprocess.TimeoutExpired):p.kill();p.wait(timeout=5)
            p.stdin.close();p.stdout.close()
        for f in self.files:f.close()
        self.processes=[]
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
