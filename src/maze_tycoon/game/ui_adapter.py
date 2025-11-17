"""
Adapters that bridge Maze Tycoon's internal world to the pygame UI.

These helpers make it easy to take a sequence of maze / solver states and
view them using `run_maze_view` from `game.ui_pygame`.
"""
from __future__ import annotations

import random

from typing import (
    Collection,
    Iterable,
    Iterator,
    Optional,
    Sequence,
    Tuple,
    List,
    Set,
)

from collections import deque

from maze_tycoon.game import app as game_app
from maze_tycoon.game.app import run_once

from .ui_pygame import MazeFrame, run_maze_view

Pos = Tuple[int, int]
GridLike = Sequence[Sequence[int]]  # or bool; we normalize below

def _fit_cell_size_to_window(
    rows: int,
    cols: int,
    *,
    base_cell_size: int,
    hud_height: int,
    max_width: Optional[int],
    max_height: Optional[int],
) -> int:
    """
    Given maze dimensions and a desired base cell_size, shrink cell_size
    if needed so that the window (grid + HUD) fits within max_width/height.
    """
    cell_size = base_cell_size

    width = cols * cell_size
    height = rows * cell_size + hud_height

    scale = 1.0

    if max_width is not None and width > max_width:
        scale = min(scale, max_width / width)

    if max_height is not None and height > max_height:
        scale = min(scale, max_height / height)

    if scale < 1.0:
        cell_size = max(1, int(cell_size * scale))

    return cell_size

def iter_frames_from_grids(
    grids: Sequence[Sequence[Sequence[int] | bool]],
    *,
    player_positions: Optional[Sequence[Optional[Pos]]] = None,
    entrance: Optional[Pos] = None,
    exit: Optional[Pos] = None,
    solution_paths: Optional[Sequence[Optional[Collection[Pos]]]] = None,
    visited_cells: Optional[Sequence[Optional[Collection[Pos]]]] = None,
    notes: Optional[Sequence[Optional[str]]] = None,
) -> Iterator[MazeFrame]:
    """
    Turn a sequence of 2D grids into a sequence of MazeFrame objects.

    Each element of `grids` should be a 2D structure (rows x cols) of ints
    or bools:

        0 / False -> floor
        1 / True  -> wall

    Optional per-step sequences may be provided:
        - player_positions[i]: (row, col) for that step
        - solution_paths[i]: collection of (row, col) cells on the "best" path
        - visited_cells[i]: collection of visited cells so far
        - notes[i]: short status string (e.g. solver state)

    If any of the optional sequences are shorter than `grids`, they are
    treated as None for remaining steps.
    """
    n_steps = len(grids)

    def safe_get(seq: Optional[Sequence], idx: int):
        if seq is None:
            return None
        if idx < len(seq):
            return seq[idx]
        return None

    for step_idx in range(n_steps):
        raw_grid = grids[step_idx]
        # Normalize to int grid
        int_grid: list[list[int]] = []
        for row in raw_grid:
            int_row: list[int] = []
            for cell in row:
                if isinstance(cell, bool):
                    int_row.append(1 if cell else 0)
                else:
                    int_row.append(int(cell))
            int_grid.append(int_row)

        frame = MazeFrame(
            grid=int_grid,
            player=safe_get(player_positions, step_idx),
            entrance=entrance,
            exit=exit,
            solution_path=safe_get(solution_paths, step_idx),
            visited=safe_get(visited_cells, step_idx),
            step_index=step_idx,
            note=safe_get(notes, step_idx),
        )
        yield frame


def view_grids_with_pygame(
    grids: Sequence[Sequence[Sequence[int] | bool]],
    *,
    player_positions: Optional[Sequence[Optional[Pos]]] = None,
    entrance: Optional[Pos] = None,
    exit: Optional[Pos] = None,
    solution_paths: Optional[Sequence[Optional[Collection[Pos]]]] = None,
    visited_cells: Optional[Sequence[Optional[Collection[Pos]]]] = None,
    notes: Optional[Sequence[Optional[str]]] = None,
    fps: int = 20,
    cell_size: int = 24,
    hud_height: int = 48,
    window_title: str = "Maze Tycoon Demo",
) -> None:
    """
    Convenience wrapper that builds MazeFrames from raw grids and launches the
    pygame viewer.

    This is ideal for quick demos and experiments where you already have
    a list of grids over time and just want to *see* them.
    """
    frames = iter_frames_from_grids(
        grids,
        player_positions=player_positions,
        entrance=entrance,
        exit=exit,
        solution_paths=solution_paths,
        visited_cells=visited_cells,
        notes=notes,
    )
    run_maze_view(
        frames,
        fps=fps,
        cell_size=cell_size,
        hud_height=hud_height,
        window_title=window_title,
    )

def _bfs_path(
    matrix: Sequence[Sequence[int]],
    start: Pos,
    goal: Pos,
    connectivity: int = 4,
) -> List[Pos]:
    """
    Simple BFS that returns a path from start to goal as a list of (r, c) cells.
    Uses 0=open, 1=wall like the main algorithms.
    This is for visualization only and does not affect metrics.
    """
    H, W = len(matrix), len(matrix[0])
    def is_open(r: int, c: int) -> bool:
        return 0 <= r < H and 0 <= c < W and matrix[r][c] == 0

    if not (is_open(*start) and is_open(*goal)):
        return []

    if connectivity == 8:
        neighbors = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
    else:
        neighbors = [(1,0),(-1,0),(0,1),(0,-1)]

    q = deque([start])
    parent: dict[Pos, Optional[Pos]] = {start: None}

    while q:
        r, c = q.popleft()
        if (r, c) == goal:
            break
        for dr, dc in neighbors:
            nr, nc = r + dr, c + dc
            if is_open(nr, nc) and (nr, nc) not in parent:
                parent[(nr, nc)] = (r, c)
                q.append((nr, nc))

    if goal not in parent:
        return []

    path: List[Pos] = []
    cur: Optional[Pos] = goal
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    return path


def frames_from_matrix_with_path(
    matrix: Sequence[Sequence[int]],
    *,
    start: Pos,
    goal: Pos,
    connectivity: int = 4,
    note_prefix: str = "run",
) -> Iterator[MazeFrame]:
    """
    Convert a 0/1 matrix into an ordered sequence of MazeFrames showing
    a BFS path being walked from `start` to `goal`.

    Includes a short pause at the end of the run for satisfying feedback.
    """
    rows = len(matrix)
    cols = len(matrix[0]) if rows else 0

    int_grid: List[List[int]] = [
        [int(cell) for cell in row] for row in matrix
    ]

    # Compute BFS path
    path = _bfs_path(matrix, start, goal, connectivity=connectivity)

    if not path:
        # If unsolvable, show a single static frame
        yield MazeFrame(
            grid=int_grid,
            player=None,
            entrance=start,
            exit=goal,
            solution_path=None,
            visited=None,
            step_index=0,
            note=f"{note_prefix}: no path",
        )
        return

    solution_cells = set(path)
    visited_so_far: set[Pos] = set()

    # Animate stepping through the path
    for step_idx, pos in enumerate(path):
        visited_so_far.add(pos)
        yield MazeFrame(
            grid=int_grid,
            player=pos,
            entrance=start,
            exit=goal,
            solution_path=solution_cells,
            visited=set(visited_so_far),
            step_index=step_idx,
            note=f"{note_prefix}: step {step_idx}/{len(path)-1}",
        )

    # Add a short pause at the end (10 frames)
    final_step = len(path) - 1
    final_note = f"{note_prefix}: done in {final_step} steps"
    for _ in range(10):
        yield MazeFrame(
            grid=int_grid,
            player=path[-1],
            entrance=start,
            exit=goal,
            solution_path=solution_cells,
            visited=set(visited_so_far),
            step_index=final_step,
            note=final_note,
        )

def _distance_map_from_goal(
    matrix: Sequence[Sequence[int]],
    goal: Pos,
    connectivity: int = 4,
) -> list[list[Optional[int]]]:
    """
    BFS from the goal to compute shortest-path distance (in steps)
    to every reachable floor cell. Walls get None.
    """
    rows = len(matrix)
    cols = len(matrix[0]) if rows else 0

    dist: list[list[Optional[int]]] = [[None for _ in range(cols)] for _ in range(rows)]

    def is_open(r: int, c: int) -> bool:
        return 0 <= r < rows and 0 <= c < cols and matrix[r][c] == 0

    if not is_open(*goal):
        return dist

    if connectivity == 8:
        neighbors = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
    else:
        neighbors = [(1,0),(-1,0),(0,1),(0,-1)]

    q = deque([goal])
    dist[goal[0]][goal[1]] = 0

    while q:
        r, c = q.popleft()
        d = dist[r][c]
        assert d is not None
        for dr, dc in neighbors:
            nr, nc = r + dr, c + dc
            if is_open(nr, nc) and dist[nr][nc] is None:
                dist[nr][nc] = d + 1
                q.append((nr, nc))

    return dist


def pick_spawn_far_from_goal(
    matrix: Sequence[Sequence[int]],
    goal: Pos,
    *,
    connectivity: int = 4,
    min_steps: int = 8,
    max_tries: int = 1000,
) -> Pos:
    """
    Choose a random floor cell that:
      - is reachable from goal
      - is at least `min_steps` away by shortest path
      - is not equal to goal

    Falls back (gracefully) to any reachable cell, and ultimately to (1, 1)
    if things are weird.
    """
    dist = _distance_map_from_goal(matrix, goal, connectivity=connectivity)
    rows = len(matrix)
    cols = len(matrix[0]) if rows else 0

    far_cells: list[Pos] = []
    reachable_floor: list[Pos] = []

    for r in range(rows):
        for c in range(cols):
            if matrix[r][c] != 0:
                continue
            d = dist[r][c]
            if d is None:
                continue
            reachable_floor.append((r, c))
            if d >= min_steps and (r, c) != goal:
                far_cells.append((r, c))

    rng = random.Random()

    # Prefer far cells
    if far_cells:
        return rng.choice(far_cells)

    # If no far cells, but some reachable floors, pick any non-goal
    if reachable_floor:
        candidates = [p for p in reachable_floor if p != goal] or reachable_floor
        return rng.choice(candidates)

    # Ultimate fallback
    return (1, 1)


def iter_demo_walk_frames(
    rows: int = 10,
    cols: int = 10,
) -> Iterator[MazeFrame]:
    """Yield frames for an infinite L-shaped walk around the border."""
    # Prebuild static grid with border walls
    grid: List[List[int]] = [[0 for _ in range(cols)] for _ in range(rows)]
    for rr in range(rows):
        grid[rr][0] = 1
        grid[rr][cols - 1] = 1
    for cc in range(cols):
        grid[0][cc] = 1
        grid[rows - 1][cc] = 1

    # L-shaped path from top-left inside corner to bottom-right inside corner
    # We keep the path inside the border so we see the player move.
    path: List[Pos] = []
    for c in range(1, cols - 1):
        path.append((1, c))
    for r in range(2, rows - 1):
        path.append((r, cols - 2))

    entrance = path[0]
    exit_ = path[-1]
    solution_cells: Set[Pos] = set(path)

    global_step = 0
    lap = 0

    while True:
        lap += 1
        visited: Set[Pos] = set()
        for step_idx, pos in enumerate(path):
            visited.add(pos)

            frame = MazeFrame(
                grid=grid,
                player=pos,
                entrance=entrance,
                exit=exit_,
                solution_path=solution_cells,
                visited=set(visited),
                step_index=global_step,
                note=f"Lap {lap}, step {step_idx}",
            )
            yield frame
            global_step += 1


def demo_walk_loop() -> None:
    """Run the infinite demo walk until the window is closed."""
    frames = iter_demo_walk_frames(rows=10, cols=10)
    run_maze_view(
        frames,
        fps=15,
        cell_size=32,
        hud_height=48,
        window_title="Maze Tycoon Demo Walk (Looping)",
    )

def demo_walk() -> None:
    """Little L-shaped demo walk for pure enjoyment."""
    rows, cols = 10, 10

    grids: list[list[list[int]]] = []
    player_positions: list[Pos] = []
    notes: list[str] = []

    path: list[Pos] = []

    # Simple L-shaped path from (0, 0) to (9, 9)
    for c in range(cols):
        path.append((0, c))
    for r in range(1, rows):
        path.append((r, cols - 1))

    for step_idx, (r, c) in enumerate(path):
        # Empty floor, with border walls
        grid = [[0 for _ in range(cols)] for _ in range(rows)]
        for rr in range(rows):
            grid[rr][0] = 1
            grid[rr][cols - 1] = 1
        for cc in range(cols):
            grid[0][cc] = 1
            grid[rows - 1][cc] = 1

        grids.append(grid)
        player_positions.append((r, c))
        notes.append(f"Demo step {step_idx}")

    view_grids_with_pygame(
        grids,
        player_positions=player_positions,
        entrance=path[0],
        exit=path[-1],
        solution_paths=[set(path)] * len(grids),
        visited_cells=[set(path[:i + 1]) for i in range(len(path))],
        notes=notes,
        fps=15,
        cell_size=32,
        window_title="Maze Tycoon Demo Walk",
    )

def frames_from_path(
    matrix: Sequence[Sequence[int]],
    path: Sequence[Pos],
    *,
    note_prefix: str = "run",
) -> Iterator[MazeFrame]:
    """
    Turn a known path (sequence of cells) into MazeFrames.
    """
    if not path:
        rows = len(matrix)
        cols = len(matrix[0]) if rows else 0
        return
        yield  # pragma: no cover, just to make it an iterator

    int_grid: list[list[int]] = [[int(cell) for cell in row] for row in matrix]
    solution_cells = set(path)
    visited: set[Pos] = set()

    start = path[0]
    goal = path[-1]

    for step_idx, pos in enumerate(path):
        visited.add(pos)
        yield MazeFrame(
            grid=int_grid,
            player=pos,
            entrance=start,
            exit=goal,
            solution_path=solution_cells,
            visited=set(visited),
            step_index=step_idx,
            note=f"{note_prefix}: step {step_idx}/{len(path)-1}",
        )

def view_real_run_with_pygame(
    cfg: dict,
    *,
    width: int,
    height: int,
    trial_idx: int = 0,
    base_seed: int = 0,
    fps: int = 20,
    cell_size: int = 24,
    hud_height: int = 48,
    max_window_width: Optional[int] = 1280,
    max_window_height: Optional[int] = 720,
) -> None:
    """
    Run a *real* Maze Tycoon trial using game.app.run_once,
    then visualize the resulting matrix with a BFS-based animation.
    """
    result = run_once(
        cfg,
        width=width,
        height=height,
        trial_idx=trial_idx,
        base_seed=base_seed,
        return_matrix=True,
        sink=None,
    )

    row, matrix = result  # (row_dict, matrix)

    search = cfg["search"]
    connectivity = int(search.get("connectivity", 4))
    algo = row.get("algorithm", search["algorithm"])
    heuristic = row.get("heuristic") or search.get("heuristic")

    note_prefix = f"{algo}" + (f" ({heuristic})" if heuristic else "")

    rows = len(matrix)
    cols = len(matrix[0]) if rows else 0

    # 🔹 Adjust cell_size so the window stays within bounds
    if max_window_width is not None or max_window_height is not None:
        cell_size = _fit_cell_size_to_window(
            rows,
            cols,
            base_cell_size=cell_size,
            hud_height=hud_height,
            max_width=max_window_width,
            max_height=max_window_height,
        )

    path = row.get("path", [])

    if path:
        frames = frames_from_path(matrix, path, note_prefix=note_prefix)
    else:
        goal: Pos = (rows - 2, cols - 2)
    
        start: Pos = pick_spawn_far_from_goal(matrix, goal, connectivity=connectivity, min_steps=8)

        frames = frames_from_matrix_with_path(
            matrix,
            start=start,
            goal=goal,
            connectivity=connectivity,
            note_prefix=note_prefix,
        )

    run_maze_view(
        frames,
        fps=fps,
        cell_size=cell_size,
        hud_height=hud_height,
        window_title="Maze Tycoon Real Run",
    )

if __name__ == "__main__":
    demo_walk()