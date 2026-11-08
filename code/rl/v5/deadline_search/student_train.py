"""One predeclared two-round CPU distillation pilot; no outcome selection."""
from student_common import *
import platform
import torch
from torch import nn
from rl.train.bc import Policy, export


def load_bank(name):
    p=STUDENT/('labels-'+name+'.npz');meta=json.loads(p.with_suffix('.json').read_text());assert meta['passed'] and sha(p)==meta['dataset_sha256']
    bank=dict(np.load(p));assert bank['x'].dtype==np.float32 and np.all(bank['x'][:,13:15]==.5)
    bank['probabilities']=np.where(bank['changed'],3.,1.);bank['probabilities']/=bank['probabilities'].sum()
    return bank


def batch(items):
    lengths=[int(b['offsets'][g+1]-b['offsets'][g]) for b,g in items];width=max(lengths)
    x=np.zeros((len(items),width,128),dtype=np.float32);mask=np.zeros((len(items),width),dtype=np.bool_);labels=[]
    for i,((b,g),length) in enumerate(zip(items,lengths)):
        x[i,:length]=b['x'][b['offsets'][g]:b['offsets'][g+1]];mask[i,:length]=True;labels.append(b['labels'][g])
    return torch.from_numpy(x),torch.from_numpy(mask),torch.tensor(labels,dtype=torch.long)


def evaluate(model,bank):
    losses=[];correct=[]
    with torch.no_grad():
        for start in range(0,len(bank['labels']),128):
            x,mask,y=batch([(bank,g) for g in range(start,min(start+128,len(bank['labels'])))])
            logits=model(x).masked_fill(~mask,-1e9)
            losses.extend(nn.functional.cross_entropy(logits,y,reduction='none').tolist());correct.extend((logits.argmax(-1)==y).tolist())
    per_root=[float(np.mean(losses[a:b])) for a,b in zip(bank['root_offsets'][:-1],bank['root_offsets'][1:])]
    return {'mean_per_root_group_cross_entropy':float(np.mean(per_root)),'group_accuracy':float(np.mean(correct)),
        'groups':len(losses),'roots':len(per_root),'per_root_loss':per_root}


def train(number):
    teacher_guard();assert number in (1,2);torch.set_num_threads(2);torch.manual_seed(20261108)
    torch.use_deterministic_algorithms(True);rng=np.random.default_rng(20261108)
    anchor=Policy();baseline=torch.load(ACTOR.with_name('checkpoint.pt'),map_location='cpu',weights_only=False)
    anchor.load_state_dict(baseline['actor']);anchor.eval();model=Policy()
    initial=ACTOR.with_name('checkpoint.pt') if number==1 else STUDENT/'round1/checkpoint.pt'
    initial_state=baseline if number==1 else torch.load(initial,map_location='cpu',weights_only=False)
    model.load_state_dict(initial_state['actor'])
    if number==2:rng.bit_generator.state=initial_state['numpy_rng'];torch.set_rng_state(initial_state['torch_rng'])
    banks=[load_bank('anchor')]+([load_bank('current')] if number==2 else []);dev=load_bank('development')
    out=STUDENT/f'round{number}';out.mkdir(exist_ok=False)
    config={'as_of':now(),'round':number,'seed':20261108,'device':'cpu','threads':2,'updates':400,'max_seconds':600,
        'batch_roots':32,'changed_root_weight':3,'bank_probabilities':[1] if number==1 else [.5,.5],
        'optimizer':'AdamW','learning_rate':3e-5,'weight_decay':1e-5,'gradient_clip':.5,'anchor_kl_coefficient':.2,
        'parameters':sum(p.numel() for p in model.parameters()),'initial_checkpoint':rel(initial),'initial_sha256':sha(initial),
        'datasets':{n:sha(STUDENT/('labels-'+n+'.npz')) for n in ['anchor','development']+(['current'] if number==2 else [])},
        'python':platform.python_version(),'torch':torch.__version__,'numpy':np.__version__,'source_sha256':sha(Path(__file__)),
        'protocol_sha256':sha(OUT/'STUDENT_PROTOCOL.md'),'external_spend':0}
    assert config['parameters']==24833;save(out/'config.json',config)
    optimizer=torch.optim.AdamW(model.parameters(),lr=3e-5,weight_decay=1e-5)
    start=time.monotonic();history=[];updates=0
    for step in range(400):
        if time.monotonic()-start>=600:break
        items=[]
        for _ in range(32):
            bank=banks[int(rng.integers(len(banks)))];root=int(rng.choice(len(bank['changed']),p=bank['probabilities']))
            group=int(rng.integers(bank['root_offsets'][root],bank['root_offsets'][root+1]));items.append((bank,group))
        x,mask,y=batch(items);student_logits=model(x).masked_fill(~mask,-1e9)
        with torch.no_grad():anchor_logits=anchor(x).masked_fill(~mask,-1e9);anchor_p=anchor_logits.softmax(-1)
        ce=nn.functional.cross_entropy(student_logits,y)
        kl=nn.functional.kl_div(student_logits.log_softmax(-1),anchor_p,reduction='batchmean')
        loss=ce+.2*kl;assert torch.isfinite(loss);optimizer.zero_grad(set_to_none=True);loss.backward()
        norm=nn.utils.clip_grad_norm_(model.parameters(),.5);optimizer.step();updates+=1
        history.append({'update':updates,'cross_entropy':float(ce.detach()),'kl':float(kl.detach()),'loss':float(loss.detach()),'gradient_norm':float(norm),'seconds':time.monotonic()-start})
        if updates%100==0:print(json.dumps({'stage':'train'+str(number),**history[-1]}),flush=True)
    elapsed=time.monotonic()-start
    checkpoint={'actor':model.state_dict(),'optimizer':optimizer.state_dict(),'updates':updates,'numpy_rng':rng.bit_generator.state,'torch_rng':torch.get_rng_state(),'config':config}
    torch.save(checkpoint,out/('checkpoint.pt' if updates==400 else 'FAILED-partial.pt'))
    save(out/'history.json',history)
    if updates!=400 or elapsed>600:
        save(out/'failure.json',{'as_of':now(),'reason':'Predeclared 600s cap','updates':updates,'seconds':elapsed});raise RuntimeError('Student pilot wall cap failed')
    export(model,out/'weights.txt');model.eval();result=evaluate(model,dev)
    save(out/'summary.json',{'as_of':now(),'passed':True,'updates':updates,'training_seconds':elapsed,'dev':result,
        'weights_sha256':sha(out/'weights.txt'),'checkpoint_sha256':sha(out/'checkpoint.pt'),'budget':budget()})
    print(json.dumps({'stage':'train'+str(number),'updates':updates,'seconds':elapsed,'dev_loss':result['mean_per_root_group_cross_entropy']}),flush=True)


def select():
    rows=[json.loads((STUDENT/f'round{n}/summary.json').read_text()) for n in (1,2)];assert all(r['passed'] and r['updates']==400 for r in rows)
    loss=[r['dev']['mean_per_root_group_cross_entropy'] for r in rows];chosen=2 if loss[1]<loss[0]-1e-6 else 1
    save(STUDENT/'selection.json',{'as_of':now(),'round':chosen,'dev_losses':loss,'rule':'Minimum mean per-root/per-group dev CE; earlier wins within1e-6',
        'weights_path':rel(STUDENT/f'round{chosen}/weights.txt'),'weights_sha256':rows[chosen-1]['weights_sha256'],
        'full_game_strength_used_for_selection':False,'protocol_sha256':sha(OUT/'STUDENT_PROTOCOL.md')})


if __name__=='__main__':
    if sys.argv[1]=='select':select()
    else:train(int(sys.argv[1]))