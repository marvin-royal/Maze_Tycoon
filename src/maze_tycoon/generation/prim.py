from __future__ import annotations
from typing import Optional, Tuple, Set, List
from maze_tycoon.core import Grid, Cell

def generate(grid: Grid, start: Optional[Tuple[int, int]] = None) -> None:
    """
    Randomized Prim's algorithm for maze generation.
    Carves passages in-place on the provided Grid.
    """
    grid.reset_visits()

    # pick start
    if start is None:
        start_cell = grid.random_cell()
    else:
        start_cell = grid.cell_at(*start)
    start_cell.visited = True

    visited: Set[Cell] = {start_cell}
    frontier: List[Cell] = []

    def add_frontier(c: Cell):
        for n in grid.neighbors(c):
            if not n.visited and n not in frontier:
                frontier.append(n)

    add_frontier(start_cell)

    while frontier:
        # pick a random frontier cell
        idx = grid.rng.randrange(len(frontier))
        cell = frontier.pop(idx)

        # connect it to a random visited neighbor
        visited_neighbors = [n for n in grid.neighbors(cell) if n.visited]
        if not visited_neighbors:
            # shouldn't really happen, but guard anyway
            continue
        neighbor = grid.rng.choice(visited_neighbors)
        neighbor.remove_wall_between(cell)

        # mark and expand
        cell.visited = True
        visited.add(cell)
        add_frontier(cell)
