"""Conditional student helpers; all frozen teacher sources remain read-only."""
import ctypes as C
import numpy as np
from common import *
from diagnose import Native
from maps import registry, classpath
from run_matches import java_home
import panel as original_panel

STUDENT=OUT/'student'
TRAIN=list(range(70201,70213));DEV=list(range(70301,70309));CONFIRM=list(range(70401,70441))
SELECTED_TURNS=list(range(0,28,3))


def teacher_guard():
    guard();audit=json.loads((OUT/'final-audit.json').read_text());assert audit['teacher_admitted']
    frozen=json.loads((OUT/'freeze.json').read_text())
    for p,h in {**frozen['sources'],**frozen['weights'],**frozen['binaries'],**frozen['dependencies']}.items():assert sha(ROOT/p)==h,p
    assert sha(OUT/'PROTOCOL.md')==frozen['protocol_sha256']
    return frozen


def prepare(name,seeds):
    teacher_guard();assert set(seeds)<=set(TRAIN+DEV+CONFIRM)
    exclusions=registry('student-'+name);known=set(exclusions['canonical']);legacy=set(exclusions['legacy'])
    process=subprocess.Popen([str(java_home()/'bin/java'),'-Xmx1g','-cp',classpath(),'MapGenerator'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    entries=[];hashes={};overlaps=[]
    try:
        for seed in seeds:
            process.stdin.write(str(seed)+'\n');process.stdin.flush();props=json.loads(process.stdout.readline())
            board={k:[list(map(int,r.split(','))) for r in props[k].split('_') if r] for k in ('nodes','units','edges')}
            digest=hashlib.sha256(json.dumps(board,sort_keys=True,separators=(',',':')).encode()).hexdigest()
            old=hashlib.sha256(json.dumps(props,sort_keys=True).encode()).hexdigest()
            if digest in known or old in legacy or digest in hashes.values():overlaps.append(seed)
            hashes[str(seed)]=digest;entries.append({'seed':seed,'hash':digest,'legacy_hash':old,'map':board})
    finally:process.stdin.close();process.wait(timeout=20)
    save(STUDENT/(name+'-maps.json'),{'as_of':now(),'maps':entries,'overlaps':overlaps})
    save(OUT/('student-'+name+'-map-hashes.json'),hashes)
    save(STUDENT/(name+'-novelty.json'),{'as_of':now(),'passed':not overlaps,'seeds':seeds,'overlaps':overlaps,
        'previous_canonical':len(known),'previous_legacy':len(legacy),'registry_sha256':sha(OUT/('student-'+name+'-registry.json'))})
    assert not overlaps,'Stop on content overlap, no substitution'
    return hashes


class Trace:
    def __init__(self):
        self.native=Native();self.lib=C.CDLL(str(build_dir()/'student-trace.dylib'))
        lib=self.lib
        lib.tr_make.argtypes=[C.c_void_p,C.c_void_p,C.c_int,C.c_int];lib.tr_make.restype=C.c_char_p
        lib.tr_features.restype=C.POINTER(C.c_float);lib.tr_offsets.restype=C.POINTER(C.c_int);lib.tr_choices.restype=C.POINTER(C.c_int)
        lib.ds_error.restype=C.c_char_p
    def capture(self,sim,player,selected,command):
        before=sim.state();raw=self.lib.tr_make(self.native.ptr,sim.ptr,player,selected)
        assert raw,self.lib.ds_error();meta=json.loads(raw)
        assert meta['command']==command and sim.state()==before
        groups=meta['groups'];n=meta['candidate_rows'];assert 0<groups<=400 and 0<n<=12000
        x=np.ctypeslib.as_array(self.lib.tr_features(),shape=(n*128,)).copy().reshape(n,128)
        offsets=np.ctypeslib.as_array(self.lib.tr_offsets(),shape=(groups+1,)).copy()
        labels=np.ctypeslib.as_array(self.lib.tr_choices(),shape=(groups,)).copy()
        lengths=np.diff(offsets);assert offsets[0]==0 and offsets[-1]==n and np.all(lengths>0)
        assert np.all((labels>=0)&(labels<lengths));assert np.isfinite(x).all() and np.max(np.abs(x))<=5
        assert np.all(x[:,13:15]==.5),'No style rewriting allowed'
        for length,label in zip(lengths,labels):
            target=np.zeros(length,dtype=np.float32);target[label]=1;assert target.sum()==1
        meta['feature_sha256']=hashlib.sha256(x.tobytes()).hexdigest()
        return meta,x,offsets,labels
    def close(self):self.native.close()


def teacher_stream(inputs,name):
    command=[str(build_dir()/'bot'),*[str(p) for p in [ACTOR,CRITIC,*ENEMIES]],'4','16']
    result=subprocess.run(command,input=b''.join(inputs),capture_output=True,timeout=90)
    lines=result.stdout.decode().splitlines();stats=[json.loads(s.split('=',1)[1]) for s in result.stderr.decode().splitlines() if s.startswith('deadline=')]
    save(STUDENT/'teacher-streams'/(name+'.json'),{'as_of':now(),'command':command,'returncode':result.returncode,
        'input_sha256':hashlib.sha256(b''.join(inputs)).hexdigest(),'outputs':lines,'stderr':result.stderr.decode()})
    assert result.returncode==0 and len(lines)==len(inputs)==len(stats)
    assert [s['turn'] for s in stats]==list(range(1,len(inputs)+1))
    return lines,stats


def collect(name,seeds,candidate,weights,hashes):
    teacher_guard();assert (STUDENT/'trace-contracts.json').exists()
    cmds=original_panel.commands();cmds[candidate]=[rel(build_dir()/'bot'),*[rel(p) for p in [weights,CRITIC,*ENEMIES]],'1','0']
    # Process-local adapter only: the unchanged panel records these exact commands
    # and this adapter's SHA. No frozen file or global registry is modified.
    original_panel.commands=lambda:cmds
    opponents=('lacoz','khoufou2','khoufou','b2m')
    entries=[{'candidate':candidate,'opponent':opponents[i%4],'seed':seed,'seat':p}
             for i,seed in enumerate(seeds) for p in (i%2,1-i%2)]
    original_panel.panel('student/'+name,entries,hashes,'distillation_state_collection_not_strength')
