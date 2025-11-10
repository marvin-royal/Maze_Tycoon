from dataclasses import dataclass
from typing import Tuple, List, Optional
from maze_tycoon.core.rng import RNG
from maze_tycoon.algorithms.interfaces import Generator, Matrix

Pos = Tuple[int, int]

@dataclass
class Maze:
    h: int
    w: int
    start: Pos = (1, 1)
    goal: Optional[Pos] = None
    grid: Optional[Matrix] = None  # 0=open, 1=wall

    def generate(self, gen: Generator, rng: RNG) -> "Maze":
        self.grid = gen.carve(rng, self.h, self.w)
        if self.goal is None:
            self.goal = (self.h - 2, self.w - 2)
        return self

    def to_matrix(self) -> Matrix:
        if self.grid is None:
            raise ValueError("Maze not generated yet")
        return self.grid

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < self.h and 0 <= c < self.w and self.grid[r][c] == 0
