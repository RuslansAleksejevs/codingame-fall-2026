"""Read-only content uniqueness diagnostic; never changes banks or selection."""
from support import *
import numpy as np
import platform
import torch


def main():
    check_freeze()
    reports = {}; lengths = {}; model_exposures = {}
    for name in ('narrow', 'broad', 'development'):
        path = OUT/('bank-'+name+'.npz'); metadata = json.loads(path.with_suffix('.json').read_text())
        assert sha(path) == metadata['dataset_sha256']
        data = dict(np.load(path)); labels_by_features = {}; target_hashes = set()
        lengths[name] = np.diff(data['offsets'])
        for group, (a, b) in enumerate(zip(data['offsets'][:-1], data['offsets'][1:])):
            digest = hashlib.sha256(data['x'][a:b].tobytes()).hexdigest()
            target = int(data['labels'][group])
            labels_by_features.setdefault(digest, set()).add(target)
            target_hashes.add((digest, target))
        reports[name] = {'roots': metadata['roots'], 'unique_states': metadata['unique_states'],
            'maps': len(metadata['maps']), 'total_prefix_group_records': len(data['labels']),
            'distinct_exact_feature_matrices': len(labels_by_features),
            'distinct_exact_feature_matrix_target_pairs': len(target_hashes),
            'feature_matrices_with_multiple_targets': sum(len(targets) > 1 for targets in labels_by_features.values()),
            'candidate_rows': len(data['x']), 'dataset_sha256': sha(path),
            'changed_by_phase': [sum(r['changed'] and r['phase'] == phase for r in metadata['records']) for phase in range(3)]}
    for arm in ARMS[:-1]:
        path = OUT/'models'/arm/'exposures.npy'
        if not path.exists(): continue
        exposure = np.load(path); counts = lengths[arm[:-1]][exposure[:, :, 1]]
        assert exposure.shape == (800, 32, 2)
        model_exposures[arm] = {'updates': 800, 'root_group_exposures': 25600,
            'distinct_exposed_roots': int(len(np.unique(exposure[:, :, 0]))),
            'distinct_exposed_group_indices': int(len(np.unique(exposure[:, :, 1]))),
            'candidate_rows_in_sampled_groups': int(counts.sum()),
            'padded_candidate_slots': int(counts.max(axis=1).sum()*32), 'exposures_sha256': sha(path)}
    save(OUT/'coverage-content-audit.json', {'as_of': now(), 'banks': reports,
        'model_exposures': model_exposures, 'matched_budget_definition': '800 updates and25,600 root/group exposures per model; variable candidate-set sizes mean FLOPs/walltime are not exactly matched.',
        'definition': 'Exact legal candidate feature-matrix bytes, optionally plus target index; not a new independent game count.',
        'role': 'Diagnostic only; no architecture/objective/seed/sample or gate selection.', 'source_sha256': sha(Path(__file__))})
    save(OUT/'environment.json', {'as_of': now(), 'python': platform.python_version(), 'numpy': np.__version__,
        'torch': torch.__version__, 'platform': platform.platform(), 'machine': platform.machine(),
        'compiler': subprocess.run(['clang++', '--version'], capture_output=True, text=True).stdout,
        'java': subprocess.run([str(java_home()/'bin/java'), '-version'], capture_output=True, text=True).stderr,
        'new_environment_installed': False, 'external_spend': 0})


if __name__ == '__main__': main()