"""Explicit scheduled PPO-v3 rollouts; separate binary from legacy training."""
import ctypes as C
import json
from pathlib import Path
import numpy as np
from rl.sim.native import map_text

ROOT = Path(__file__).resolve().parents[3]
LIB = C.CDLL(str(ROOT / 'code/build/libtryangle_v3.dylib'))
EXTERNAL = C.CFUNCTYPE(C.c_void_p, C.c_int, C.c_int, C.c_int, C.c_char_p)
FLOAT = C.POINTER(C.c_float)
INT = C.POINTER(C.c_int)
LIB.league_new.argtypes = [C.c_char_p]
LIB.league_new.restype = C.c_void_p
LIB.league_delete.argtypes = [C.c_void_p]
LIB.league_error.restype = C.c_char_p
LIB.league_add_map.argtypes = [C.c_void_p, C.c_char_p]
LIB.league_set_actor.argtypes = [C.c_void_p, FLOAT]
LIB.league_set_anchor.argtypes = [C.c_void_p, FLOAT]
LIB.league_add_pool.argtypes = [C.c_void_p]
LIB.league_clear_pool.argtypes = [C.c_void_p]
LIB.league_set_pool.argtypes = [C.c_void_p, C.c_int, FLOAT]
LIB.league_set_external.argtypes = [C.c_void_p, EXTERNAL]
LIB.league_collect_scheduled.argtypes = [C.c_void_p, C.c_int, C.c_int, C.c_ulonglong, C.c_double, C.c_int, INT]
for name in ('league_stats', 'league_records'):
    getattr(LIB, name).argtypes = [C.c_void_p]
    getattr(LIB, name).restype = C.c_char_p
LIB.league_float.argtypes = [C.c_void_p, C.c_int]
LIB.league_float.restype = FLOAT
LIB.league_int.argtypes = [C.c_void_p, C.c_int]
LIB.league_int.restype = INT
LIB.league_episodes.argtypes = [C.c_void_p]


def flatten(state):
    if hasattr(state, 'state_dict'):
        state = state.state_dict()
    return np.concatenate([v.detach().cpu().numpy().ravel() for v in state.values()]).astype(np.float32)


class Rollout:
    def __init__(self, weights, maps):
        self.ptr = LIB.league_new(str(Path(weights).resolve()).encode())
        if not self.ptr:
            raise RuntimeError(LIB.league_error().decode())
        for data in maps:
            LIB.league_add_map(self.ptr, map_text(data).encode())

    def set_actor(self, state):
        data = flatten(state)
        LIB.league_set_actor(self.ptr, data.ctypes.data_as(FLOAT))

    def set_pool(self, states):
        LIB.league_clear_pool(self.ptr)
        for state in states:
            self.set_actor(state)
            LIB.league_add_pool(self.ptr)

    def collect(self, schedule, workers, seed, temperature=.7, audit=0):
        schedule = np.ascontiguousarray(schedule, dtype=np.int32)
        assert schedule.ndim == 2 and schedule.shape[1] == 3
        if LIB.league_collect_scheduled(self.ptr, len(schedule), workers, seed, temperature, audit, schedule.ctypes.data_as(INT)):
            raise RuntimeError(LIB.league_error().decode())
        stats = json.loads(LIB.league_stats(self.ptr))
        n, g, c = (stats[k] for k in ('controlled_decisions', 'groups', 'candidates'))
        e = LIB.league_episodes(self.ptr)
        f = lambda which, shape: np.ctypeslib.as_array(LIB.league_float(self.ptr, which), shape=shape)
        i = lambda which, size: np.ctypeslib.as_array(LIB.league_int(self.ptr, which), shape=(size,))
        return {'x': f(0, (c * 128,)).reshape(c, 128), 'value_x': f(1, (n * 128,)).reshape(n, 128),
                'old_logp': f(2, (n,)), 'old_entropy': f(3, (n,)), 'reward': f(4, (n,)),
                'group_offsets': i(0, g + 1), 'choices': i(1, g), 'turn_offsets': i(2, n + 1),
                'episode_offsets': i(3, e + 1), 'game_ids': i(4, n), 'players': i(5, n), 'stats': stats}

    def records(self):
        return json.loads(LIB.league_records(self.ptr))

    def close(self):
        if self.ptr:
            LIB.league_delete(self.ptr)
            self.ptr = None

    def __del__(self):
        self.close()