# tests/test_interfaces.py
from typing import Tuple
from maze_tycoon.algorithms.interfaces import Generator, Solver, Renderer, MetricsSink, Matrix
from maze_tycoon.core.rng import RNG

Pos = Tuple[int, int]

class DummyGen:
    def carve(self, rng: RNG, h: int, w: int) -> Matrix:
        return [[0]*w for _ in range(h)]

class DummySolver:
    def solve(self, grid: Matrix, start: Pos, goal: Pos, *, connectivity: int = 4, return_path: bool = False):
        return {"found": True, "path_length": 0, "node_expansions": 0, "visited": 1,
                "queue_peak": 1, "runtime_ms": 0.0, "path": [(0,0)] if return_path else None}

class DummyRenderer:
    def draw(self, grid: Matrix, player: Pos, goal: Pos, overlay=None) -> None:
        pass

class DummyMetrics:
    def log_event(self, name: str, **fields): pass
    def flush(self): pass

def test_protocol_duck_typing_smoke():
    g: Generator = DummyGen()
    s: Solver = DummySolver()
    r: Renderer = DummyRenderer()
    m: MetricsSink = DummyMetrics()
    grid = g.carve(RNG(42), 3, 3)
    assert len(grid) == 3 and len(grid[0]) == 3
    out = s.solve(grid, (0,0), (2,2), connectivity=4, return_path=True)
    assert out["found"] is True and isinstance(out["path"], list)
    r.draw(grid, (0,0), (2,2), overlay=out["path"])
    m.log_event("solver_done", **out); m.flush()
