import heapq
from time import perf_counter
from importlib import import_module
from math import sqrt

def _heuristic(name, start, goal):
    # Load maze_tycoon.heuristics.<name>.h
    mod = import_module(f"maze_tycoon.heuristics.{name}")
    return lambda node: mod.h(node, goal)

def solve(matrix, start=(1, 1), goal=None, heuristic="manhattan", connectivity=4, **_):
    H, W = len(matrix), len(matrix[0])
    if goal is None:
        goal = (H - 2, W - 2)

    def is_open(r, c):
        return 0 <= r < H and 0 <= c < W and matrix[r][c] == 0  # 0=open

    neigh4 = ((1,0),(-1,0),(0,1),(0,-1))
    neigh8 = neigh4 + ((1,1),(1,-1),(-1,1),(-1,-1))
    neighbors = neigh8 if connectivity == 8 else neigh4

    h = _heuristic(heuristic, start, goal)

    t0 = perf_counter()
    g = {start: 0.0}
    parent = {start: None}
    pq = [(h(start), 0.0, start)]  # (f, g, node)
    expansions = 0

    visited_order = []
    closed = set()

    while pq:
        f, gcur, (r, c) = heapq.heappop(pq)

        if (r, c) in closed:
            continue
        closed.add((r, c))

        expansions += 1
        visited_order.append((r, c))
        
        if (r, c) == goal:
            break
        for dr, dc in neighbors:
            nr, nc = r + dr, c + dc
            if not is_open(nr, nc):
                continue
            step = sqrt(2) if dr and dc else 1.0
            ng = gcur + step
            if ng < g.get((nr, nc), float("inf")):
                g[(nr, nc)] = ng
                parent[(nr, nc)] = (r, c)
                heapq.heappush(pq, (ng + h((nr, nc)), ng, (nr, nc)))
                
    runtime_ms = (perf_counter() - t0) * 1000.0

    if goal not in parent:
        return {
            "path": [],
            "path_length": 0,
            "node_expansions": expansions,
            "runtime_ms": runtime_ms,
            "visited": list(visited_order)
        }

    # Reconstruct path from goal back to start
    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()

    path_length = max(0, len(path) - 1)

    return {
        "path": path,
        "path_length": path_length,
        "node_expansions": expansions,
        "runtime_ms": runtime_ms,
        "visited": list(visited_order)
    }

