from __future__ import annotations
from typing import Optional, Tuple, List
from maze_tycoon.core import Grid, Cell

def generate(grid: Grid, start: Optional[Tuple[int, int]] = None) -> None:
    """
    Depth-First Search backtracker (recursive backtracking) maze generator.
    Carves passages in-place on the provided Grid.
    """
    # choose a start
    if start is None:
        cur = grid.random_cell()
    else:
        cur = grid.cell_at(*start)

    # prep
    grid.reset_visits()
    cur.visited = True
    stack: List[Cell] = [cur]

    while stack:
        cur = stack[-1]
        unv = grid.unvisited_neighbors(cur)
        if not unv:
            stack.pop()
            continue
        nxt = grid.rng.choice(unv)
        cur.remove_wall_between(nxt)
        nxt.visited = True
        stack.append(nxt)
