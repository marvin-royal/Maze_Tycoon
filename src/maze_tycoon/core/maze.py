from dataclasses import dataclass
from typing import Tuple, List, Optional
from maze_tycoon.core.rng import RNG
from maze_tycoon.algorithms.interfaces import Generator, Matrix

Pos = Tuple[int, int]

def pick_random_goal_from_matrix(
    matrix: Matrix,
    rng: RNG,
    *,
    start: Pos = (1, 1),
) -> Pos:
    """
    Choose a random open goal cell in matrix space.

    - Only uses tiles where matrix[r][c] == 0 (floor).
    - Avoids the start tile itself.
    - Biases toward cells far from the start (by Manhattan distance).
    - Deterministic given the RNG (and thus the seed).
    """
    rows = len(matrix)
    cols = len(matrix[0]) if rows else 0

    # Collect all open cells except the start
    open_cells: List[Pos] = [
        (r, c)
        for r in range(rows)
        for c in range(cols)
        if matrix[r][c] == 0 and (r, c) != start
    ]

    # Fallback: keep the classic "bottom-right inner" if something is weird
    if not open_cells:
        if rows >= 3 and cols >= 3:
            return (rows - 2, cols - 2)
        return (1, 1)

    start_r, start_c = start

    # Manhattan distances from start
    dists = [abs(r - start_r) + abs(c - start_c) for (r, c) in open_cells]
    max_dist = max(dists)
    threshold = max_dist * 7 // 10  # 70% of max distance

    far_cells = [
        pos for pos, d in zip(open_cells, dists)
        if d >= threshold
    ]

    candidates = far_cells or open_cells
    return rng.choice(candidates)

@dataclass
class Maze:
    h: int
    w: int
    start: Pos = (1, 1)
    goal: Optional[Pos] = None
    grid: Optional[Matrix] = None  # 0=open, 1=wall

    def generate(self, gen: Generator, rng: RNG) -> "Maze":
        """
        Generate the maze grid and choose a goal position.

        - Uses the provided Generator to carve the maze.
        - If no goal was preset, picks a random open cell,
          biased toward being far from the start.
        """
        self.grid = gen.carve(rng, self.h, self.w)

        if self.goal is None:
            if self.grid is None:
                raise ValueError("Maze grid not carved")
            self.goal = pick_random_goal_from_matrix(
                self.grid,
                rng,
                start=self.start,
            )

        return self

    def to_matrix(self) -> Matrix:
        if self.grid is None:
            raise ValueError("Maze not generated yet")
        return self.grid

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < self.h and 0 <= c < self.w and self.grid[r][c] == 0
