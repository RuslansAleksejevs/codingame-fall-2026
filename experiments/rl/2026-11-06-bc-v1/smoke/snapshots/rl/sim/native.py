"""ctypes interface: no Python game mechanics in the rollout loop."""
import ctypes
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LIB = ctypes.CDLL(str(ROOT / "code/build/libtryangle.dylib"))
LIB.sim_new.argtypes = [ctypes.c_char_p]
LIB.sim_new.restype = ctypes.c_void_p
LIB.sim_delete.argtypes = [ctypes.c_void_p]
LIB.sim_state.argtypes = [ctypes.c_void_p]
LIB.sim_state.restype = ctypes.c_char_p
LIB.sim_step.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
LIB.sim_error.restype = ctypes.c_char_p

def map_text(data):
    return "\n".join([str(len(data["nodes"])), *[" ".join(map(str, xy + uv)) for xy, uv in zip(data["nodes"], data["units"])], str(len(data["edges"])), *[" ".join(map(str, e)) for e in data["edges"]]])

class Simulator:
    def __init__(self, data):
        self.ptr = LIB.sim_new(map_text(data).encode())
        if not self.ptr:
            raise ValueError("Native map construction failed")
    def state(self):
        return json.loads(LIB.sim_state(self.ptr))
    def step(self, actions):
        if LIB.sim_step(self.ptr, actions[0].encode(), actions[1].encode()):
            raise RuntimeError(LIB.sim_error().decode())
    def close(self):
        if self.ptr:
            LIB.sim_delete(self.ptr)
            self.ptr = None
    def __del__(self):
        self.close()
