"""Matched NEW students; same initialization/objective/budget, two paired seeds."""
from support import *
import ctypes as C
import platform
import numpy as np
import torch
from torch import nn
from rl.train.bc import Policy, export
from student_train import batch, evaluate
from rl.sim.native import LIB


def bank(name):
    path = OUT/('bank-'+name+'.npz'); metadata = json.loads(path.with_suffix('.json').read_text())
    assert sha(path) == metadata['dataset_sha256']
    result = dict(np.load(path))
    assert result['x'].dtype == np.float32 and np.all(result['x'][:, 13:15] == .5)
    result['probabilities'] = np.where(result['changed'], 3., 1.)
    result['probabilities'] /= result['probabilities'].sum()
    return result


def train(arm):
    check_freeze(); teacher_guard()
    assert arm in ARMS[:-1]
    seed = SEEDS[int(arm[-1])-1]; name = arm[:-1]
    torch.set_num_threads(2); torch.manual_seed(seed); torch.use_deterministic_algorithms(True)
    rng = np.random.default_rng(seed)
    state = torch.load(ACTOR.with_name('checkpoint.pt'), map_location='cpu', weights_only=False)
    anchor, model = Policy(), Policy()
    anchor.load_state_dict(state['actor']); model.load_state_dict(state['actor']); anchor.eval()
    assert sum(p.numel() for p in model.parameters()) == 24833
    data, development = bank(name), bank('development')
    destination = OUT/'models'/arm; destination.mkdir(parents=True, exist_ok=False)
    config = {'as_of': now(), 'arm': arm, 'seed': seed, 'updates': 800, 'maximum_seconds': 600,
        'batch_roots': 32, 'changed_root_weight': 3, 'optimizer': 'AdamW', 'learning_rate': 3e-5,
        'weight_decay': 1e-5, 'clip_grad_norm': .5, 'anchor_kl_coefficient': .2, 'device': 'cpu', 'threads': 2,
        'parameters': 24833, 'initial_checkpoint': rel(ACTOR.with_name('checkpoint.pt')),
        'initial_sha256': sha(ACTOR.with_name('checkpoint.pt')), 'data_sha256': sha(OUT/('bank-'+name+'.npz')),
        'development_sha256': sha(OUT/'bank-development.npz'), 'data_freeze_sha256': sha(OUT/'data-freeze.json'),
        'python': platform.python_version(), 'torch': torch.__version__, 'numpy': np.__version__, 'external_spend': 0}
    save(destination/'config.json', config)
    initial_diagnostic = evaluate(model, development)
    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-5, weight_decay=1e-5)
    start = time.monotonic(); history = []; exposures = []; updates = 0
    for step in range(800):
        if time.monotonic()-start >= 600: break
        items = []; sampled = []
        for _ in range(32):
            root = int(rng.choice(len(data['changed']), p=data['probabilities']))
            group = int(rng.integers(data['root_offsets'][root], data['root_offsets'][root+1]))
            items.append((data, group)); sampled.append((root, group))
        x, mask, y = batch(items)
        logits = model(x).masked_fill(~mask, -1e9)
        with torch.no_grad(): anchor_p = anchor(x).masked_fill(~mask, -1e9).softmax(-1)
        ce = nn.functional.cross_entropy(logits, y)
        kl = nn.functional.kl_div(logits.log_softmax(-1), anchor_p, reduction='batchmean')
        loss = ce+.2*kl; assert torch.isfinite(loss)
        optimizer.zero_grad(set_to_none=True); loss.backward()
        norm = nn.utils.clip_grad_norm_(model.parameters(), .5); optimizer.step(); updates += 1
        exposures.append(sampled)
        history.append({'update': updates, 'ce': float(ce.detach()), 'kl': float(kl.detach()),
            'loss': float(loss.detach()), 'gradient_norm': float(norm), 'seconds': time.monotonic()-start})
        if updates % 200 == 0: print(json.dumps({'arm': arm, **history[-1]}), flush=True)
    elapsed = time.monotonic()-start
    checkpoint = {'actor': model.state_dict(), 'optimizer': optimizer.state_dict(), 'updates': updates,
        'numpy_rng': rng.bit_generator.state, 'torch_rng': torch.get_rng_state(), 'config': config}
    torch.save(checkpoint, destination/('checkpoint.pt' if updates == 800 else 'FAILED-partial.pt'))
    save(destination/'history.json', history)
    exposure = np.asarray(exposures, dtype=np.int64)
    np.save(destination/'exposures.npy', exposure)
    assert updates == 800 and elapsed <= 600, 'Incomplete matched optimization: stop without extension'
    model.eval(); export(model, destination/'weights.txt')
    diagnostic = evaluate(model, development)
    save(destination/'summary.json', {'as_of': now(), 'passed': True, 'updates': updates, 'training_seconds': elapsed,
        'initial_labeldev': initial_diagnostic, 'labeldev': diagnostic, 'root_exposures': int(exposure.shape[0]*exposure.shape[1]),
        'distinct_exposed_roots': int(len(np.unique(exposure[:, :, 0]))),
        'distinct_exposed_groups': int(len(np.unique(exposure[:, :, 1]))),
        'weights_sha256': sha(destination/'weights.txt'), 'checkpoint_sha256': sha(destination/'checkpoint.pt'),
        'strength_selection': False, 'exposures_sha256': sha(destination/'exposures.npy')})


def package(arm):
    check_freeze(); teacher_guard()
    torch.set_num_threads(2)
    destination = OUT/'models'/arm; weights = destination/'weights.txt'
    state = torch.load(destination/'checkpoint.pt', map_location='cpu', weights_only=False)
    model = Policy(); model.load_state_dict(state['actor']); model.eval()
    values = np.asarray(list(map(float, weights.read_text().split()[6:])), dtype=np.float32)
    expected = np.concatenate([p.detach().numpy().ravel() for p in model.parameters()])
    assert values.shape == expected.shape == (24833,) and np.array_equal(values.view(np.uint32), expected.view(np.uint32))
    LIB.net_new.argtypes = [C.c_char_p]; LIB.net_new.restype = C.c_void_p
    LIB.net_evaluate.argtypes = [C.c_void_p, C.POINTER(C.c_float)]; LIB.net_evaluate.restype = C.c_float
    LIB.net_delete.argtypes = [C.c_void_p]
    net = LIB.net_new(str(weights).encode()); assert net
    data = bank('development'); errors = []; agree = 0
    try:
        with torch.no_grad():
            for a, b in zip(data['offsets'][:-1], data['offsets'][1:]):
                x = data['x'][a:b]; predicted = model(torch.from_numpy(x)).numpy()
                actual = np.asarray([LIB.net_evaluate(net, r.ctypes.data_as(C.POINTER(C.c_float))) for r in x])
                errors.extend(np.abs(predicted-actual).tolist()); agree += int(predicted.argmax() == actual.argmax())
    finally: LIB.net_delete(net)
    passed = agree == len(data['labels']) and max(errors) < .001
    save(destination/'native-parity.json', {'passed': passed, 'groups': len(data['labels']), 'agree': agree,
        'maximum_logit_error': max(errors), 'text_checkpoint_float32_exact': True})
    assert passed
    run([PYTHON, '-B', 'code/rl/export/package.py', '--league', 'full', '--weights', rel(weights),
         '--sha256', sha(weights), '--out', rel(destination/'package')], arm+'-package')
    manifest = json.loads((destination/'package/package.json').read_text())
    assert manifest['source_utf16_units'] < 98000
    run([PYTHON, '-B', 'code/rl/v3/verify_package.py', '--manifest', rel(destination/'package/package.json'),
        '--panel', rel(V5/'confirm1'), '--out', rel(destination/'verify'), '--records', '20'], arm+'-verify')
    assert json.loads((destination/'verify/summary.json').read_text())['passed']


if __name__ == '__main__':
    if sys.argv[1] == 'train': train(sys.argv[2])
    elif sys.argv[1] == 'package': package(sys.argv[2])
    else: raise ValueError(sys.argv[1])