# tests/test_maze.py
import pytest
from maze_tycoon.core.maze import Maze
from maze_tycoon.core.rng import RNG
from maze_tycoon.algorithms.interfaces import Generator, Matrix

class TinyOpenGenerator:
    # Walls on the border; interior open, with one blocked cell to test in_bounds.
    def carve(self, rng: RNG, h: int, w: int) -> Matrix:
        grid: Matrix = [[0]*w for _ in range(h)]
        for r in range(h):
            grid[r][0] = grid[r][w-1] = 1
        for c in range(w):
            grid[0][c] = grid[h-1][c] = 1
        if h > 3 and w > 3:
            grid[2][2] = 1
        return grid

def test_generate_sets_grid_and_default_goal():
    m = Maze(h=7, w=9, start=(1,1), goal=None).generate(TinyOpenGenerator(), RNG(123))
    assert m.grid is not None
    assert m.goal == (m.h - 2, m.w - 2)
    mat = m.to_matrix()
    assert len(mat) == 7 and len(mat[0]) == 9

def test_to_matrix_raises_before_generation():
    m = Maze(h=5, w=5)
    with pytest.raises(ValueError):
        _ = m.to_matrix()

def test_in_bounds_respects_walls_and_interior():
    m = Maze(h=7, w=9).generate(TinyOpenGenerator(), RNG(1))
    assert m.in_bounds(0, 0) is False   # border wall
    assert m.in_bounds(6, 8) is False   # border wall
    assert m.in_bounds(1, 1) is True    # interior open
    assert m.in_bounds(2, 2) is False   # our interior blocker

def test_maze_default_goal_branch():
    # Uses a no-op generator and a real RNG to satisfy Maze.generate(...)
    from maze_tycoon.core.maze import Maze
    from maze_tycoon.core.rng import RNG
    from maze_tycoon.algorithms.interfaces import Matrix

    class DummyGen:
        def carve(self, rng: "RNG", h: int, w: int) -> Matrix:  # type: ignore[name-defined]
            # Open interior with wall borders: 1 = wall, 0 = open
            return [[1]*w] + [[1] + [0]*(w-2) + [1] for _ in range(h-2)] + [[1]*w]

    H, W = 6, 7
    m = Maze(H, W, goal=None)
    m.generate(DummyGen(), RNG(0))   # should assign default goal internally when goal=None
    assert m.goal == (H - 2, W - 2)
