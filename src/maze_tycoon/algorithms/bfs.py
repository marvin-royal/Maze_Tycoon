from collections import deque
from time import perf_counter

def solve(matrix, start=(1, 1), goal=None, **_):
    H, W = len(matrix), len(matrix[0])
    if goal is None:
        goal = (H - 2, W - 2)

    def is_open(r, c):
        return 0 <= r < H and 0 <= c < W and matrix[r][c] == 0  # 0=open

    t0 = perf_counter()
    q = deque([start])
    parent = {start: None}
    expansions = 0

    visited_order = []
    closed = set()

    while q:
        r, c = q.popleft()

        if (r, c) in closed:
            continue
        closed.add((r, c))

        expansions += 1
        visited_order.append((r, c))

        if (r, c) == goal:
            break
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if is_open(nr, nc) and (nr, nc) not in parent:
                parent[(nr, nc)] = (r, c)
                q.append((nr, nc))

    runtime_ms = (perf_counter() - t0) * 1000.0

    if goal not in parent:
        return {
            "path": [],
            "path_length": 0,
            "node_expansions": expansions,
            "runtime_ms": runtime_ms,
            "visited": list(visited_order),
        }

    # Reconstruct path once
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
        "visited": list(visited_order),
    }
