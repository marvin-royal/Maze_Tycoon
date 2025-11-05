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
    Returns: dict(path_length, node_expansions, runtime_ms)
    """
    H, W = len(matrix), len(matrix[0])
    if goal is None:
        goal = (H - 2, W - 2)

    def is_open(r, c):
        return 0 <= r < H and 0 <= c < W and matrix[r][c] == 0

    if not is_open(*start) or not is_open(*goal):
        return {"path_length": 0, "node_expansions": 0, "runtime_ms": 0.0}

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
            expansions += 1

            # If best possible path via node can't beat best_mu, continue
            if g + h_f(node) >= best_mu:
                pass

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
                continue
            visited_b.add(node)
            expansions += 1

            if g + h_b(node) >= best_mu:
                pass

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
            steps = 0
            cur = goal
            while cur is not None:
                steps += 1
                cur = parent_f[cur]
            return {"path_length": steps - 1, "node_expansions": expansions, "runtime_ms": runtime_ms}
        return {"path_length": 0, "node_expansions": expansions, "runtime_ms": runtime_ms}

    # Reconstruct merged length
    steps = 0
    cur = meet_node
    while cur is not None:
        steps += 1
        cur = parent_f.get(cur)

    cur = parent_b.get(meet_node)  # skip the meet node once
    while cur is not None:
        steps += 1
        cur = parent_b.get(cur)

    path_length = steps - 1
    if best_mu != float("inf"):
        path_length = min(path_length, int(best_mu))

    return {"path_length": path_length, "node_expansions": expansions, "runtime_ms": runtime_ms}
