"""ctypes for isolated full-state restoration and matched rollouts."""
import ctypes as C
import json
from pathlib import Path
import numpy as np
from common import BUILD
from state import encode

LIB = C.CDLL(str(BUILD / 'libcurriculum.dylib'))
P, F, I = C.c_void_p, C.POINTER(C.c_float), C.POINTER(C.c_int)
EXTERNAL = C.CFUNCTYPE(P, C.c_int, C.c_int, C.c_int, C.c_char_p)


def bind(name, arguments, result=C.c_int):
    fn = getattr(LIB, name)
    fn.argtypes, fn.restype = arguments, result
    return fn


for name in ('sim_new', 'curr_restore', 'curr_new', 'net_new'):
    bind(name, [C.c_char_p], P)
for name in ('sim_delete', 'curr_delete', 'net_delete'):
    bind(name, [P], None)
for name in ('sim_state', 'curr_snapshot', 'league_stats', 'league_records'):
    bind(name, [P], C.c_char_p)
for name in ('sim_error', 'curr_error'):
    bind(name, [], C.c_char_p)
bind('sim_step', [P, C.c_char_p, C.c_char_p])
bind('sim_clone', [P], P)
bind('net_act', [P, P, C.c_int, C.c_int], C.c_char_p)
bind('league_add_map', [P, C.c_char_p], None)
bind('league_clear_pool', [P], None)
bind('league_set_actor', [P, F], None)
bind('league_set_external', [P, EXTERNAL], None)
bind('curr_add_start', [P, C.c_char_p])
bind('curr_add_opponent', [P, C.c_char_p])
bind('curr_collect', [P, C.c_int, C.c_int, C.c_ulonglong, C.c_double, C.c_int, I])
bind('league_float', [P, C.c_int], F)
bind('league_int', [P, C.c_int], I)
bind('league_episodes', [P])


def map_text(data):
    return '\n'.join([str(len(data['nodes'])), *[' '.join(map(str, xy + u)) for xy, u in zip(data['nodes'], data['units'])],
                      str(len(data['edges'])), *[' '.join(map(str, e)) for e in data['edges']]])


class Simulator:
    def __init__(self, board=None, snapshot=None):
        self.ptr = LIB.curr_restore(encode(snapshot).encode()) if snapshot is not None else LIB.sim_new(map_text(board).encode())
        if not self.ptr:
            raise RuntimeError(LIB.curr_error().decode())

    def state(self):
        return json.loads(LIB.curr_snapshot(self.ptr))

    def step(self, actions):
        if LIB.sim_step(self.ptr, *[a.encode() for a in actions]):
            raise RuntimeError(LIB.sim_error().decode())

    def close(self):
        if getattr(self, 'ptr', None):
            LIB.sim_delete(self.ptr)
            self.ptr = None

    def __del__(self):
        self.close()


class Network:
    def __init__(self, weights):
        self.ptr = LIB.net_new(str(Path(weights).resolve()).encode())
        assert self.ptr, str(weights)

    def act(self, sim, seat):
        return LIB.net_act(self.ptr, sim.ptr, seat, 2).decode()

    def close(self):
        if getattr(self, 'ptr', None):
            LIB.net_delete(self.ptr)
            self.ptr = None

    def __del__(self):
        self.close()


class Rollout:
    def __init__(self, weights, maps, starts, opponents):
        self.ptr = LIB.curr_new(str(Path(weights).resolve()).encode())
        assert self.ptr, LIB.curr_error().decode()
        for board in maps:
            LIB.league_add_map(self.ptr, map_text(board).encode())
        for index, start in enumerate(starts):
            assert LIB.curr_add_start(self.ptr, encode(start).encode()) == index, LIB.curr_error().decode()
        LIB.league_clear_pool(self.ptr)
        for index, path in enumerate(opponents):
            assert LIB.curr_add_opponent(self.ptr, str(Path(path).resolve()).encode()) == index

    def set_actor(self, actor):
        flat = np.concatenate([v.detach().cpu().numpy().ravel() for v in actor.state_dict().values()]).astype(np.float32)
        LIB.league_set_actor(self.ptr, flat.ctypes.data_as(F))

    def collect(self, schedule, workers, seed, temperature=.7, audit=0):
        schedule = np.ascontiguousarray(schedule, dtype=np.int32)
        assert schedule.ndim == 2 and schedule.shape[1] == 4
        if LIB.curr_collect(self.ptr, len(schedule), workers, seed, temperature, audit, schedule.ctypes.data_as(I)):
            raise RuntimeError(LIB.curr_error().decode())
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
        if getattr(self, 'ptr', None):
            LIB.curr_delete(self.ptr)
            self.ptr = None

    def __del__(self):
        self.close()