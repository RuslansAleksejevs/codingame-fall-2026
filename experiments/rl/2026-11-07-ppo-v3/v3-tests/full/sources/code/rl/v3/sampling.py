"""Bounded difficulty priority, with a fixed self-play share and per-style floors."""
import numpy as np

NAMES = ('current', 'league3m', 'long3m', 'league_extended', 'recent0', 'recent1', 'lacoz')


def probabilities(scores, external=True):
    """Allocate 35% current and 65% across eligible opponents (6--25% each)."""
    active = list(range(1, len(NAMES) if external else len(NAMES) - 1))
    result = np.zeros(len(NAMES), dtype=np.float64)
    result[0] = .35
    result[active] = .06
    remaining = .65 - .06 * len(active)
    priorities = np.array([(0.2 + 1 - scores[i]) ** 1.5 for i in active])
    while remaining > 1e-12:
        room = .25 - result[active]
        available = room > 1e-12
        weights = priorities * available
        addition = np.minimum(room, remaining * weights / weights.sum())
        result[active] += addition
        remaining -= addition.sum()
    assert abs(result.sum() - 1) < 1e-9
    return result


def schedule(rng, games, scores, external=True):
    weights = probabilities(scores, external)
    labels = rng.choice(len(NAMES), size=games, p=weights)
    # 0=current, 2=greedy frozen/history pool, 3=unchanged external Lacoz.
    rows = [(0 if label == 0 else 3 if label == 6 else 2,
             max(0, label - 1), int(rng.integers(2))) for label in labels]
    return labels, np.array(rows, dtype=np.int32), weights


def update_scores(scores, labels, outcomes):
    for label in range(1, len(NAMES)):
        values = [(row[3] + 1) / 2 for ident, row in zip(labels, outcomes) if ident == label]
        if values:
            # Effective ~100-game EMA, independent of rare-label minibatch size.
            decay = .99 ** len(values)
            scores[label] = decay * scores[label] + (1 - decay) * np.mean(values)