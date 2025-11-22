from time import perf_counter
import heapq

def solve(matrix, start=(1, 1), goal=None, connectivity=4, **_):
    """
    Dijkstra's algorithm on a grid matrix using uniform edge costs (1 per move).
    Returns: dict(path_length, node_expansions, runtime_ms)
    """
    H, W = len(matrix), len(matrix[0])
    if goal is None:
        goal = (H - 2, W - 2)

    def is_open(r, c):
        
        return 0 <= r < H and 0 <= c < W and matrix[r][c] == 0  # 0=open

    if not is_open(*start) or not is_open(*goal):
        return {"path_length": 0, "node_expansions": 0, "runtime_ms": 0.0}

    # Neighbor deltas by connectivity
    if connectivity == 8:
        nbrs = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
    else:
        nbrs = [(-1,0),(1,0),(0,-1),(0,1)]

    t0 = perf_counter()
    pq = [(0, start)]  # (dist, node)
    dist = {start: 0}
    parent = {start: None}
    visited = set()
    visited_order = []
    expansions = 0

    while pq:
        d, (r, c) = heapq.heappop(pq)
        if (r, c) in visited:
            continue    #pragma: no cover
        visited.add((r, c))
        visited_order.append((r, c))

        if (r, c) == goal:
            break

        expansions += 1
        for dr, dc in nbrs:
            nr, nc = r + dr, c + dc
            if not is_open(nr, nc):
                continue
            nd = d + 1  # uniform cost
            if nd < dist.get((nr, nc), float("inf")):
                dist[(nr, nc)] = nd
                parent[(nr, nc)] = (r, c)
                heapq.heappush(pq, (nd, (nr, nc)))

    runtime_ms = (perf_counter() - t0) * 1000.0

    if goal not in parent:
        return {
            "path": [],
            "path_length": 0,
            "node_expansions": expansions,
            "runtime_ms": runtime_ms,
            "visited": visited_order,
        }

    # Reconstruct full path
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
        "visited": visited_order,
    }

