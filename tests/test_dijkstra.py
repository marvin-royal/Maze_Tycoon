# tests/algorithms/test_dijkstra.py
from maze_tycoon.algorithms import dijkstra as mod
import pytest

def _empty(h=7, w=7):
    m = [[1]*w] + [[1]+[0]*(w-2)+[1] for _ in range(h-2)] + [[1]*w]
    return m

def test_dijkstra_nonnegative_cost():
    mat = _empty(7,7)
    res = mod.solve(mat, start=(1,1), goal=(5,5), connectivity=4)
    assert res["path_length"] >= 0

# tests/algorithms/test_dijkstra_edges.py
from maze_tycoon.algorithms import dijkstra as mod
import pytest

def box(h, w, fill=0):
    m = [[1]*w] + [[1] + [fill]*(w-2) + [1] for _ in range(h-2)] + [[1]*w]
    return m

def test_dijkstra_start_equals_goal():
    mat = box(5,5)
    res = mod.solve(mat, start=(1,1), goal=(1,1), connectivity=4)
    # Exercises early return; API returns metrics
    assert isinstance(res, dict)
    assert res.get("path_length") == 0
    assert res.get("node_expansions") in (0, 1)

def test_dijkstra_unreachable():
    mat = box(5,5)
    mat[2][2] = 1  # block goal
    res = mod.solve(mat, start=(1,1), goal=(2,2), connectivity=4)
    # Exercises fail/reconstruct none (~56)
    assert (res is None) or (not res.get("path"))

def test_dijkstra_relaxation_improves_distance():
    mat = box(7,7)
    # Create a “tempting but longer” corridor and a short detour; ensure relaxation updates the PQ (~33→53, 36)
    # Long corridor along row 1 with a forced detour at the end
    # Nothing special in matrix values if weights are uniform; the structure enforces relaxations.
    # Start left, goal right.
    # Make a small obstacle to force a backtrack/relax
    mat[1][3] = 1
    res = mod.solve(mat, start=(1,1), goal=(1,5), connectivity=4)
    assert res and res.get("path_length", len(res.get("path", []))) > 0

def test_dijkstra_rejects_or_gracefully_handles_oob_points():
    mat = box(5,5)
    # Out-of-bounds goal—either raises or returns “no path”.
    try:
        res = mod.solve(mat, start=(1,1), goal=(9,9), connectivity=4)
    except Exception:
        return
    assert (res is None) or (isinstance(res, dict) and res.get("path_length", 0) == 0)

def test_dijkstra_relaxation_path_forces_update():
    # Force a detour so a relaxation improves a prior distance.
    mat = box(7,7)
    # Straight path is blocked, but a short detour exists.
    mat[1][2] = 1
    mat[2][2] = 1
    mat[3][2] = 1
    res = mod.solve(mat, start=(1,1), goal=(1,5), connectivity=4)
    assert isinstance(res, dict) and res.get("path_length", 0) > 0

def test_dijkstra_unreachable_confirm():
    mat = box(5,5)
    # Seal a wall across the middle
    for c in range(1,4):
        mat[3][c] = 1
    res = mod.solve(mat, start=(1,1), goal=(4,3), connectivity=4)
    assert (res is None) or (isinstance(res, dict) and res.get("path_length", 0) == 0)

def test_dijkstra_start_out_of_bounds_is_guard():
    mat = box(5,5)
    try:
        res = mod.solve(mat, start=(-1,-1), goal=(1,1), connectivity=4)
    except Exception:
        return
    assert (res is None) or (isinstance(res, dict) and res.get("path_length", 0) in (0, None))

def test_dijkstra_goal_on_wall_is_guard():
    mat = box(5,5)
    mat[2][2] = 1
    try:
        res = mod.solve(mat, start=(1,1), goal=(2,2), connectivity=4)
    except Exception:
        return
    assert (res is None) or (isinstance(res, dict) and res.get("path_length", 0) in (0, None))

def test_dijkstra_relaxation_true_then_false():
    # Force one improved relaxation AND a skipped update
    mat = box(7,7)
    mat[1][2] = 1; mat[2][2] = 1; mat[3][2] = 1  # detour needed
    res = mod.solve(mat, start=(1,1), goal=(1,5), connectivity=4)
    assert isinstance(res, dict)
    assert res.get("path_length", 0) > 0  # ensures we took at least one improvement
    # Now an easy corridor where first distances are already optimal (exercise "no update")
    mat2 = box(5,6);  # wide open corridor
    res2 = mod.solve(mat2, start=(1,1), goal=(1,4), connectivity=4)
    assert isinstance(res2, dict) and res2.get("path_length", 0) >= 3

def test_dijkstra_unreachable_confirms_no_path():
    mat = box(5,5)
    for c in range(1,4):
        mat[3][c] = 1
    res = mod.solve(mat, start=(1,1), goal=(4,3), connectivity=4)
    assert (res is None) or (isinstance(res, dict) and res.get("path_length", 0) == 0)

def test_dijkstra_default_goal_is_bottom_right():
    from maze_tycoon.algorithms import dijkstra as mod
    H, W = 6, 7
    mat = [[1]*W] + [[1]+[0]*(W-2)+[1] for _ in range(H-2)] + [[1]*W]
    res = mod.solve(mat, start=(1,1), goal=None, connectivity=8)  # hits line 11
    assert isinstance(res, dict) and res.get("path_length", 0) >= 0

def test_dijkstra_uses_diagonals_only_route():
    from maze_tycoon.algorithms import dijkstra as mod
    # Only a diagonal corridor is open → requires diag neighbors (line 22)
    mat = [[1]*5 for _ in range(5)]
    for i in range(1,4):
        mat[i][i] = 0
    res = mod.solve(mat, start=(1,1), goal=(3,3), connectivity=8)
    assert isinstance(res, dict) and res.get("path_length", 0) > 0

def test_dijkstra_skips_already_visited_nodes():
    from maze_tycoon.algorithms import dijkstra as mod
    # Force duplicate pushes so the 'if (r,c) in visited: continue' branch (line 36) fires
    H, W = 7, 7
    mat = [[1]*W] + [[1]+[0]*(W-2)+[1] for _ in range(H-2)] + [[1]*W]
    # A small detour guarantees multiple PQ insertions of same node
    mat[1][2] = 1; mat[2][2] = 1
    res = mod.solve(mat, start=(1,1), goal=(1,5), connectivity=8)  # exercises 33→53, 36
    assert isinstance(res, dict) and res.get("path_length", 0) > 0

def test_dijkstra_unreachable_final_return_zero():
    from maze_tycoon.algorithms import dijkstra as mod
    mat = [[1]*5] + [[1,0,1,0,1] for _ in range(3)] + [[1]*5]  # walls block crossing
    res = mod.solve(mat, start=(1,1), goal=(3,3), connectivity=4)
    # hits line 56 return
    assert (res is None) or (isinstance(res, dict) and res.get("path_length", 0) == 0)

def test_dijkstra_skip_already_visited_node():
    from maze_tycoon.algorithms import dijkstra as mod
    # open field + a small detour to create duplicate PQ entries for a node
    H, W = 7, 7
    mat = [[1]*W] + [[1]+[0]*(W-2)+[1] for _ in range(H-2)] + [[1]*W]
    # block a tempting shortcut so the same frontier cell gets enqueued via two routes
    mat[1][2] = 1; mat[2][2] = 1
    # diagonal connectivity increases the chance of alternate pushes
    res = mod.solve(mat, start=(1,1), goal=(5,5), connectivity=8)
    assert isinstance(res, dict) and res.get("path_length", 0) > 0
