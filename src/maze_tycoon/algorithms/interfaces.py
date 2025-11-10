from typing import Protocol, Iterable, Tuple, Dict, Any, Optional, List
from maze_tycoon.core.rng import RNG

Pos = Tuple[int, int]
Matrix = List[List[int]]

class Generator(Protocol):
    def carve(self, rng: "RNG", h: int, w: int) -> Matrix: ... # pragma: no cover

class Solver(Protocol):
    def solve(self, grid: Matrix, start: Pos, goal: Pos, *, # pragma: no cover
              connectivity: int = 4, return_path: bool = False) -> Dict[str, Any]: ...

class Renderer(Protocol):
    def draw(self, grid: Matrix, player: Pos, goal: Pos,    # pragma: no cover
             overlay: Optional[Iterable[Pos]] = None) -> None: ...

class MetricsSink(Protocol):
    def log_event(self, name: str, **fields: Any) -> None: ...  # pragma: no cover
    def flush(self) -> None: ...    # pragma: no cover
