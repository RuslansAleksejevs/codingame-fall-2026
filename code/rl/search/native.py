"""Python access to isolated simultaneous-search experiments."""
import ctypes as C
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LIB = C.CDLL(str(ROOT / 'code/build/libtryangle_search.dylib'))
LIB.search_new.argtypes = [C.c_char_p] * 5 + [C.c_int, C.c_int, C.c_double]
LIB.search_new.restype = C.c_void_p
LIB.search_delete.argtypes = [C.c_void_p]
LIB.search_act.argtypes = [C.c_void_p, C.c_void_p, C.c_int]
LIB.search_act.restype = C.c_char_p
LIB.search_info.argtypes = [C.c_void_p]
LIB.search_info.restype = C.c_char_p
LIB.search_error.restype = C.c_char_p
LIB.search_value.argtypes = [C.c_void_p, C.c_void_p, C.c_int]
LIB.search_value.restype = C.c_double


class Search:
    def __init__(self, actor, critic, opponents, depth=2, candidates=4, budget_ms=30):
        assert len(opponents) == 3
        self.ptr = LIB.search_new(*[str(Path(p).resolve()).encode() for p in [actor, critic, *opponents]], depth, candidates, budget_ms)
        if not self.ptr:
            raise RuntimeError(LIB.search_error().decode())

    def act(self, sim, player):
        result = LIB.search_act(self.ptr, sim.ptr, player)
        if result is None:
            raise RuntimeError(LIB.search_error().decode())
        return result.decode(), json.loads(LIB.search_info(self.ptr))

    def value(self, sim, player):
        return LIB.search_value(self.ptr, sim.ptr, player)

    def close(self):
        if self.ptr:
            LIB.search_delete(self.ptr)
            self.ptr = None

    def __del__(self):
        self.close()