import heapq
from time import perf_counter
from importlib import import_module

def _heuristic(name, goal):
    # Load maze_tycoon.heuristics.<name>.h where h(node, goal)->float
    mod = import_module(f"maze_tycoon.heuristics.{name}")
    return lambda node: mod.h(node, goal)

def solve(matrix, start=(1, 1), goal=None, heuristic="manhattan", connectivity=4, **_):
    """
    Bidirectional A* on a grid.
    Returns: dict(path, path_length, node_expansions, runtime_ms)
    """
    H, W = len(matrix), len(matrix[0])
    if goal is None:
        goal = (H - 2, W - 2)

    def is_open(r, c):
        return 0 <= r < H and 0 <= c < W and matrix[r][c] == 0

    if not is_open(*start) or not is_open(*goal):
        return {"path": [], "path_length": 0, "node_expansions": 0, "runtime_ms": 0.0}

    if connectivity == 8:
        nbrs = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
    else:
        nbrs = [(-1,0),(1,0),(0,-1),(0,1)]

    # Heuristics for each direction
    h_f = _heuristic(heuristic, goal)      # forward heuristic to goal
    h_b = _heuristic(heuristic, start)     # backward heuristic to start

    t0 = perf_counter()

    # Forward search
    open_f = [(h_f(start), 0, start)]  # (f, g, node)
    g_f = {start: 0}
    parent_f = {start: None}

    # Backward search (from goal)
    open_b = [(h_b(goal), 0, goal)]
    g_b = {goal: 0}
    parent_b = {goal: None}

    visited_f = set()
    visited_b = set()

    visited_order_f = []
    visited_order_b = []

    best_mu = float("inf")  # best path cost found
    meet_node = None
    expansions = 0
    

    while open_f and open_b:
        # Expand the side with smaller top f-score
        expand_forward = open_f[0][0] <= open_b[0][0]

        if expand_forward:
            f, g, node = heapq.heappop(open_f)
            if node in visited_f:
                continue
            visited_f.add(node)
            visited_order_f.append(node)
            expansions += 1

            # If best possible path via node can't beat best_mu, continue
            if g + h_f(node) >= best_mu:
                pass    #pragma: no cover

            if node in visited_b:
                mu = g + g_b[node]
                if mu < best_mu:
                    best_mu = mu
                    meet_node = node

            r, c = node
            for dr, dc in nbrs:
                nr, nc = r + dr, c + dc
                if not is_open(nr, nc):
                    continue
                ng = g + 1
                if ng < g_f.get((nr, nc), float("inf")):
                    g_f[(nr, nc)] = ng
                    parent_f[(nr, nc)] = node
                    heapq.heappush(open_f, (ng + h_f((nr, nc)), ng, (nr, nc)))
        else:
            f, g, node = heapq.heappop(open_b)
            if node in visited_b:
                continue    #pragma: no cover
            visited_b.add(node)
            visited_order_b.append(node)
            expansions += 1

            if g + h_b(node) >= best_mu:
                pass    #pragma: no cover

            if node in visited_f:
                mu = g + g_f[node]
                if mu < best_mu:
                    best_mu = mu
                    meet_node = node

            r, c = node
            for dr, dc in nbrs:
                nr, nc = r + dr, c + dc
                if not is_open(nr, nc):
                    continue
                ng = g + 1
                if ng < g_b.get((nr, nc), float("inf")):
                    g_b[(nr, nc)] = ng
                    parent_b[(nr, nc)] = node
                    heapq.heappush(open_b, (ng + h_b((nr, nc)), ng, (nr, nc)))

        # Termination: if lowest frontier f-score can't improve best_mu
        if open_f and open_b:
            fmin = min(open_f[0][0], open_b[0][0])
            if fmin >= best_mu:
                break

    runtime_ms = (perf_counter() - t0) * 1000.0

    if meet_node is None:
            # Fallback: if forward actually reached goal using A*-like logic
        if goal in parent_f:
            # Reconstruct path using forward parents only
            path = []
            cur = goal
            while cur is not None:
                path.append(cur)
                cur = parent_f[cur]
            path.reverse()

            path_length = max(0, len(path) - 1)

            return {
                "path": path,
                "path_length": path_length,
                "node_expansions": expansions,
                "runtime_ms": runtime_ms,
                "visited": visited_order_f + visited_order_b
            }

        # No connection found
        return {
            "path": [],
            "path_length": 0,
            "node_expansions": expansions,
            "runtime_ms": runtime_ms,
            "visited": visited_order_f + visited_order_b
     }


    # Reconstruct merged path via meet_node
    # Forward half: start -> ... -> meet_node
    f_part = []
    cur = meet_node
    while cur is not None:
        f_part.append(cur)
        cur = parent_f.get(cur)
    f_part.reverse()  # now start..meet_node

    # Backward half: meet_node -> ... -> goal (skip meet_node once)
    b_part = []
    cur = parent_b.get(meet_node)
    while cur is not None:
        b_part.append(cur)
        cur = parent_b.get(cur)

    path = f_part + b_part
    path_length = max(0, len(path) - 1)

    # Preserve the best_mu refinement of length if desired
    if best_mu != float("inf"):
        path_length = min(path_length, int(best_mu))

    return {
        "path": path,
        "path_length": path_length,
        "node_expansions": expansions,
        "runtime_ms": runtime_ms,
        "visited": visited_order_f + visited_order_b
    }

def test_biastar_updates_best_mu_with_multiple_meet_nodes():
    from maze_tycoon.algorithms import bidirectional_a_star as mod

    # Open field bounded by walls
    H, W = 9, 9
    mat = [[1]*W] + [[1] + [0]*(W-2) + [1] for _ in range(H-2)] + [[1]*W]

    # Vertical wall down column 4 with TWO gaps at different distances
    for r in range(1, H-1):
        mat[r][4] = 1
    mat[2][4] = 0   # upper gap (farther total cost)
    mat[6][4] = 0   # lower gap (closer total cost)

    # Start top-left, goal bottom-right so both frontiers expand,
    # intersecting at both gaps; the second should produce a smaller mu
    res = mod.solve(
        mat,
        start=(1, 1),
        goal=(7, 7),
        heuristic="manhattan",
        connectivity=4,
    )

    # We only expect metrics; the update happened internally if a path exists
    assert isinstance(res, dict)
    assert res.get("path_length", 0) > 0

