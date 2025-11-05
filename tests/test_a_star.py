import math
from importlib import import_module

A_STAR = "src.maze_tycoon.algorithms.a_star"

def empty_maze(h=7, w=7):
    """
    Border walls (1) with open interior (0). Start=(1,1), Goal=(h-2,w-2).
    """
    assert h >= 3 and w >= 3
    mat = [[1] * w]
    for r in range(1, h - 1):
        mat.append([1] + [0] * (w - 2) + [1])
    mat.append([1] * w)
    return mat

def with_barrier(h=7, w=7, col=3):
    """
    Vertical wall through interior that blocks the path from (1,1) to (h-2,w-2).
    """
    m = empty_maze(h, w)
    for r in range(1, h - 1):
        m[r][col] = 1
    return m

def run_astar(matrix, **kwargs):
    mod = import_module(A_STAR)
    return mod.solve(matrix, **kwargs)

def test_open_grid_4_connectivity_manhattan_distance():
    """
    In an open grid with 4-connectivity, the shortest path length equals Manhattan distance.
    Start=(1,1), Goal=(H-2,W-2) -> dx = H-3, dy = W-3
    """
    H, W = 7, 7
    mat = empty_maze(H, W)
    start, goal = (1, 1), (H - 2, W - 2)
    expected = (H - 3) + (W - 3)

    res = run_astar(mat, start=start, goal=goal, heuristic="manhattan", connectivity=4)
    assert res["path_length"] == expected
    assert res["node_expansions"] >= 0
    assert res["runtime_ms"] >= 0.0

def test_open_grid_8_connectivity_chebyshev_steps():
    """
    With 8-connectivity, A* should prefer diagonals; step count equals Chebyshev distance (max(dx,dy)).
    """
    H, W = 7, 7
    mat = empty_maze(H, W)
    start, goal = (1, 1), (H - 2, W - 2)
    dx, dy = (goal[0] - start[0]), (goal[1] - start[1])
    expected_steps = max(dx, dy)  # diagonal steps

    res = run_astar(mat, start=start, goal=goal, heuristic="octile", connectivity=8)
    assert res["path_length"] == expected_steps
    assert res["node_expansions"] >= 0
    assert res["runtime_ms"] >= 0.0

def test_unreachable_returns_zero():
    """
    If the goal is unreachable (barrier), path_length should be 0.
    """
    mat = with_barrier(9, 9, col=4)
    start, goal = (1, 1), (7, 7)

    res = run_astar(mat, start=start, goal=goal, heuristic="manhattan", connectivity=4)
    assert res["path_length"] == 0
    assert res["node_expansions"] >= 0
    assert res["runtime_ms"] >= 0.0

def test_goal_on_wall_returns_zero():
    """
    If the provided goal coordinate is a wall, solver should report no path.
    """
    H, W = 9, 9
    mat = empty_maze(H, W)
    start = (1, 1)
    goal = (5, 5)
    mat[goal[0]][goal[1]] = 1  # make it a wall

    res = run_astar(mat, start=start, goal=goal, heuristic="manhattan", connectivity=4)
    assert res["path_length"] == 0

def test_start_equals_goal_zero_length_path():
    """
    If start == goal, the shortest path length is 0 and the loop should exit quickly.
    """
    mat = empty_maze(7, 7)
    start = goal = (3, 3)  # place both on an open cell
    # ensure it's open:
    assert mat[start[0]][start[1]] == 0

    res = run_astar(mat, start=start, goal=goal, heuristic="manhattan", connectivity=4)
    assert res["path_length"] == 0
    assert res["node_expansions"] >= 1  # at least the pop of the start
    assert res["runtime_ms"] >= 0.0

def test_euclidean_heuristic_admissible_open_grid():
    """
    Using Euclidean heuristic on an open grid should still yield an optimal path length
    identical to the Manhattan-optimal path length for 4-connectivity (counting steps).
    """
    H, W = 7, 7
    mat = empty_maze(H, W)
    start, goal = (1, 1), (H - 2, W - 2)
    expected_manhattan_steps = (H - 3) + (W - 3)

    res_euclid = run_astar(mat, start=start, goal=goal, heuristic="euclidean", connectivity=4)
    assert res_euclid["path_length"] == expected_manhattan_steps

def test_octile_heuristic_with_8_connectivity_matches_chebyshev():
    """
    With 8-connectivity, octile is appropriate. Steps should match Chebyshev distance.
    """
    H, W = 11, 7
    mat = empty_maze(H, W)
    start, goal = (1, 1), (H - 2, W - 2)
    dx, dy = (goal[0] - start[0]), (goal[1] - start[1])
    cheb = max(dx, dy)

    res = run_astar(mat, start=start, goal=goal, heuristic="octile", connectivity=8)
    assert res["path_length"] == cheb

def _empty(h=5, w=5):
    m = [[1]*w]
    for r in range(1, h-1):
        m.append([1] + [0]*(w-2) + [1])
    m.append([1]*w)
    return m

def test_astar_start_equals_goal_zero_steps():
    mod = import_module(A_STAR)
    mat = _empty(7,7)
    start = goal = (3,3)
    res = mod.solve(mat, start=start, goal=goal, heuristic="manhattan", connectivity=4)
    assert res["path_length"] == 0
    assert res["node_expansions"] >= 1

def test_astar_diagonal_preference_connectivity8():
    mod = import_module(A_STAR)
    mat = _empty(7,7)
    start, goal = (1,1), (5,5)
    # With 8-connectivity, shortest **steps** are Chebyshev distance: 4
    res = mod.solve(mat, start=start, goal=goal, heuristic="octile", connectivity=8)
    assert res["path_length"] == 4

def test_astar_infers_default_goal_when_none():
    mod = import_module(A_STAR)
    m = _empty(7,7)
    # don't pass goal → should infer (H-2,W-2)
    res = mod.solve(m, start=(1,1), heuristic="manhattan", connectivity=4)
    # path length equals Manhattan on an open hall: (H-3)+(W-3) = 8
    assert res["path_length"] == 8
    assert res["node_expansions"] >= 1
    assert res["runtime_ms"] >= 0.0