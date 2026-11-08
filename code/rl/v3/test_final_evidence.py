#!/usr/bin/env python3
"""Synthetic decision-gate tests. No maps, checkpoints or real games are opened."""
import copy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'code'))
from rl.v3.final_evidence import evidence, EXTERNAL, SEEDS


def synthetic(candidate_wins=80, base_wins=60, direct_wins=80):
    rows = []
    for name in ('league3m', 'ppo3'):
        for opponent in (*EXTERNAL, 'league3m'):
            if name == opponent:
                continue
            wins = base_wins if name == 'league3m' else direct_wins if opponent == 'league3m' else candidate_wins
            for index, seed in enumerate(SEEDS):
                for seat in (0, 1):
                    rows.append({'candidate': name, 'opponent': opponent, 'seed': seed, 'seat': seat,
                                 'map_content_sha256': 'SYNTHETIC-NOT-A-MAP-'+str(seed),
                                 'outcome': 'win' if index < wins else 'loss', 'valid': True,
                                 'returncode': 0, 'own_action_errors': [], 'opponent_action_errors': []})
    return rows


def main():
    strong = synthetic()
    result = evidence(strong, 'ppo3')
    assert result['promotion_evidence_passed'] and result['equal_weight_external_gain_pp'] == 20
    assert result['games'] == 2200 and result['complete_composite_maps'] == 100
    assert not evidence(synthetic(60, 60, 50), 'ppo3')['promotion_evidence_passed']
    assert not evidence(synthetic(62, 60, 80), 'ppo3')['promotion_evidence_passed']
    assert not evidence(synthetic(80, 60, 54), 'ppo3')['promotion_evidence_passed']
    uncertain = evidence(synthetic(80, 60, 55), 'ppo3')
    assert uncertain['gates']['direct_score_at_least_55_percent']
    assert not uncertain['gates']['direct_map_lower_95_above_50_percent']
    assert not uncertain['promotion_evidence_passed']
    regression = copy.deepcopy(strong)
    for row in regression:
        if row['candidate'] == 'ppo3' and row['opponent'] == 'v6':
            row['outcome'] = 'loss'
    assert not evidence(regression, 'ppo3')['promotion_evidence_passed']
    error = copy.deepcopy(strong)
    next(r for r in error if r['candidate'] == 'ppo3')['own_action_errors'] = ['synthetic timeout']
    assert not evidence(error, 'ppo3')['promotion_evidence_passed']
    technical_wins = copy.deepcopy(strong)
    for row in technical_wins:
        if row['candidate'] == 'ppo3' and row['opponent'] == 'lacoz' and row['seed'] < 40021:
            row['opponent_action_errors'] = ['synthetic opponent timeout']
    low_coverage = evidence(technical_wins, 'ppo3')
    assert low_coverage['paired_candidate_minus_base']['lacoz']['clean_pairs'] == 160
    assert not low_coverage['promotion_evidence_passed']
    for invalid in (strong[:-1], strong[:-1]+[strong[0]]):
        try:
            evidence(invalid, 'ppo3')
        except AssertionError:
            pass
        else:
            raise AssertionError('Incomplete/duplicate panel accepted')
    unequal = copy.deepcopy(strong)
    next(r for r in unequal if r['candidate'] == 'ppo3')['map_content_sha256'] = 'different synthetic board'
    try:
        evidence(unequal, 'ppo3')
    except AssertionError:
        pass
    else:
        raise AssertionError('Mismatched paired maps accepted')
    print(json.dumps({'passed': True, 'synthetic_contract_cases': 11,
                      'real_games_played': 0, 'reserved_maps_generated_or_read': 0,
                      'scope': 'Synthetic final-evidence gates only, not a measured contest result.'}))


if __name__ == '__main__':
    main()