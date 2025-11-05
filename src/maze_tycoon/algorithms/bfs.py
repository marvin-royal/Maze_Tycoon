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

    while q:
        r, c = q.popleft()
        expansions += 1
        if (r, c) == goal:
            break
        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr, nc = r + dr, c + dc
            if is_open(nr, nc) and (nr, nc) not in parent:
                parent[(nr, nc)] = (r, c)
                q.append((nr, nc))

    runtime_ms = (perf_counter() - t0) * 1000.0

    if goal not in parent:
        return {"path_length": 0, "node_expansions": expansions, "runtime_ms": runtime_ms}

    steps = 0
    cur = goal
    while cur is not None:
        steps += 1
        cur = parent[cur]

    return {"path_length": steps - 1, "node_expansions": expansions, "runtime_ms": runtime_ms}
