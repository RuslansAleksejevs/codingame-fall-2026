#!/usr/bin/env python3
"""Validate the frozen packages, run the one final panel, and apply fixed gates.

Requires an existing freeze after research completion. No training, selected
policy mutation, OAuth, publication, Git operation, or submission is performed.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'code'))
from rl.train.ppo import save, sha

EXP = ROOT / 'experiments/rl/2026-11-07-ppo-v3'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--research-complete', action='store_true')
    args = ap.parse_args()
    assert args.research_complete, 'Inspect processes and finish all research before running final games'
    assert datetime.now(timezone.utc) < datetime(2026, 11, 9, 6, tzinfo=timezone.utc), 'Insufficient final-panel window'
    frozen = EXP / 'finalist'
    freeze_path = frozen / 'freeze.json'
    freeze = json.loads(freeze_path.read_text())
    prepared = json.loads((frozen / 'prepared.json').read_text())
    assert prepared['freeze_sha256'] == sha(freeze_path)
    assert prepared['spec_sha256'] == sha(frozen / 'panel-spec.json')
    assert prepared['registry_sha256'] == sha(frozen / 'map-registry.json')
    assert freeze['no_more_training_or_final_set_tuning']
    assert not (EXP / 'final-status.json').exists(), 'Partial/completed final run requires review, never silent restart'
    for path, digest in freeze['frozen_sources'].items():
        assert sha(ROOT / path) == digest

    def stage(label, **values):
        record = {'as_of': datetime.now(timezone.utc).isoformat(), 'pid': os.getpid(), 'stage': label, **values}
        save(EXP / 'final-status.json', record)
        with (EXP / 'final-events.jsonl').open('a') as f:
            f.write(json.dumps(record)+'\n')
        print(json.dumps(record), flush=True)

    def run(command, label):
        stage(label, command=[str(x).replace(str(ROOT), '${PROJECT_ROOT}') for x in command])
        with (EXP / (label+'.log')).open('x') as log:
            subprocess.run([str(x) for x in command], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)

    try:
        for name, package in freeze['packages'].items():
            run([sys.executable, 'code/rl/v3/verify_package.py', '--manifest', ROOT / package['manifest_path'],
                 '--panel', ROOT / freeze['development_panel_path'], '--records', '100',
                 '--out', frozen / ('verify-'+name)], 'final-package-check-'+name)
        panel = EXP / 'final-confirmation'
        run([sys.executable, 'code/rl/eval/panel.py', '--spec', frozen / 'panel-spec.json', '--out', panel], 'final-panel')
        native, java = EXP / 'final-native-verification.json', EXP / 'final-java-verification.json'
        run([sys.executable, 'code/rl/eval/verify_panel.py', panel, '--out', native], 'final-native-verify')
        run([sys.executable, 'code/rl/eval/verify_java_panel.py', panel, '--out', java], 'final-java-verify')
        result_path = EXP / 'final-evidence.json'
        run([sys.executable, 'code/rl/v3/final_evidence.py', '--panel', panel, '--freeze', freeze_path,
             '--native-verification', native, '--java-verification', java, '--out', result_path], 'final-analysis')
        result = json.loads(result_path.read_text())
        chosen = result['local_recommendation']
        package = freeze['packages'][chosen]
        recommendation = {'as_of': datetime.now(timezone.utc).isoformat(), 'provenance': 'PROJECT_REPORTED',
                          'candidate': chosen, 'promotion_evidence_passed': result['promotion_evidence_passed'],
                          'package': package, 'final_evidence_sha256': sha(result_path),
                          'platform_verification': 'PENDING; new read/play OAuth needed',
                          'deployed_submission_unchanged': 41657621, 'submission_authorized': False,
                          'external_spend': 0, 'objective_complete': False}
        save(EXP / 'local-recommendation.json', recommendation)
        stage('local_final_verified_platform_pending', recommendation=recommendation)
    except Exception as error:
        stage('failed', error=str(error), required_next='Inspect preserved logs/records; no automatic rerun, no promotion or submission')
        raise


if __name__ == '__main__':
    main()