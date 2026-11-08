"""Exact compact-policy export contracts, before any fresh strength comparison."""
from student_train import load_bank, Policy
from student_common import *
import torch
from rl.sim.native import LIB
from rl.sim.native import Simulator
from rl.league.rollout import LIB as LEAGUE
from rl.data.replays import read


def wrapper_parity(weights,verification):
    reference=json.loads((verification/'summary.json').read_text());streams=[]
    for index,item in enumerate(reference['streams']):
        record=read(ROOT/item['record']);p=item['player'];sim=Simulator(record['map']);inputs=[]
        try:
            for turn,decision in enumerate(record['decisions']):
                inputs.append(LEAGUE.league_observation(sim.ptr,p,int(turn==0)));sim.step(decision['actions'])
        finally:sim.close()
        inp=b''.join(inputs);command=[str(build_dir()/'bot'),*[str(x) for x in [weights,CRITIC,*ENEMIES]],'1','0']
        wrapper=subprocess.run(command,input=inp,capture_output=True,timeout=60)
        package=subprocess.run([str(verification/'packaged')],input=inp,capture_output=True,timeout=60)
        passed=(wrapper.returncode==package.returncode==0 and wrapper.stdout==package.stdout and len(wrapper.stdout.splitlines())==len(inputs))
        save(STUDENT/'package-streams'/f'{index:03}.json',{'record':item['record'],'player':p,'passed':passed,
            'wrapper_command':command,'package_command':[str(verification/'packaged')],'input_sha256':hashlib.sha256(inp).hexdigest(),
            'wrapper_stdout':wrapper.stdout.decode(),'wrapper_stderr':wrapper.stderr.decode(),
            'package_stdout':package.stdout.decode(),'package_stderr':package.stderr.decode(),
            'returncodes':[wrapper.returncode,package.returncode]})
        assert passed,'Collection wrapper / exact package command discrepancy'
        streams.append({'record':item['record'],'player':p,'plans':len(inputs),'passed':True})
    save(STUDENT/'collection-package-parity.json',{'as_of':now(),'passed':True,'streams':len(streams),
        'plans':sum(s['plans'] for s in streams),'records':streams,'scope':'Untimed command parity; no new maps or strength evidence.'})


def main():
    teacher_guard();selected=json.loads((STUDENT/'selection.json').read_text());weights=ROOT/selected['weights_path']
    assert sha(weights)==selected['weights_sha256'];training=weights.parent
    torch.set_num_threads(2);model=Policy();ckpt=torch.load(training/'checkpoint.pt',map_location='cpu',weights_only=False)
    model.load_state_dict(ckpt['actor']);model.eval();tokens=weights.read_text().split()
    values=np.asarray(list(map(float,tokens[6:])),dtype=np.float32)
    expected=np.concatenate([p.detach().numpy().ravel() for p in model.parameters()])
    assert values.shape==expected.shape==(24833,) and np.array_equal(values.view(np.uint32),expected.view(np.uint32))
    lib=LIB;lib.net_new.argtypes=[C.c_char_p];lib.net_new.restype=C.c_void_p
    lib.net_evaluate.argtypes=[C.c_void_p,C.POINTER(C.c_float)];lib.net_evaluate.restype=C.c_float;lib.net_delete.argtypes=[C.c_void_p]
    net=lib.net_new(str(weights).encode());assert net;dev=load_bank('development');errors=[];agree=0
    try:
        with torch.no_grad():
            for a,b in zip(dev['offsets'][:-1],dev['offsets'][1:]):
                x=dev['x'][a:b];yy=model(torch.from_numpy(x)).numpy()
                zz=np.asarray([lib.net_evaluate(net,row.ctypes.data_as(C.POINTER(C.c_float))) for row in x])
                errors.extend(np.abs(yy-zz).tolist());agree+=int(yy.argmax()==zz.argmax())
    finally:lib.net_delete(net)
    passed=agree==len(dev['labels']) and max(errors)<.001
    save(STUDENT/'native-logit-parity.json',{'as_of':now(),'passed':passed,'groups':len(dev['labels']),'argmax_agree':agree,
        'candidate_logits':len(errors),'maximum_absolute_error':max(errors),'mean_absolute_error':float(np.mean(errors)),
        'checkpoint_text_float32_exact':True,'weights_sha256':sha(weights),'feature_rewriting':False})
    assert passed,'Stop on native/PyTorch discrepancy'
    python='code/arena/.venv-rl/bin/python'
    run([python,'-B','code/rl/export/package.py','--league','full','--weights',rel(weights),'--sha256',sha(weights),
        '--out',rel(STUDENT/'package')],'student-package-build')
    verification=STUDENT/'build/verify-package'
    run([python,'-B','code/rl/v3/verify_package.py','--manifest',rel(STUDENT/'package/package.json'),
        '--panel',rel(OUT/'confirm1'),'--out',rel(verification),'--records','100'],'student-package-parity')
    report=json.loads((verification/'summary.json').read_text());assert report['passed']
    save(STUDENT/'package-parity.json',report)
    wrapper_parity(weights,verification)


if __name__=='__main__':main()