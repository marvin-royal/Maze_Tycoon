from maze_tycoon.metrics.aggregations import group_mean, percentiles, groupby_agg

ROWS = [
    {"algorithm": "bfs", "generator": "dfs_backtracker", "path_length": 8, "runtime_ms": 5.0, "node_expansions": 20},
    {"algorithm": "bfs", "generator": "dfs_backtracker", "path_length": 6, "runtime_ms": 4.0, "node_expansions": 18},
    {"algorithm": "dijkstra", "generator": "prim", "path_length": 10, "runtime_ms": 12.0, "node_expansions": 40},
    {"algorithm": "dijkstra", "generator": "prim", "path_length": 12, "runtime_ms": 11.0, "node_expansions": 44},
    # a row missing fields shouldn't poison the averages:
    {"algorithm": "bfs", "generator": "prim"},
]

def test_group_mean_by_algorithm():
    res = group_mean(ROWS, by="algorithm")
    # Expect two rows, bfs and dijkstra, with means over existing numeric rows only
    bfs = next(r for r in res if r["algorithm"] == "bfs")
    dij = next(r for r in res if r["algorithm"] == "dijkstra")
    assert bfs["mean_path_length"] == 7.0
    assert bfs["mean_runtime_ms"] == 4.5
    assert dij["mean_path_length"] == 11.0
    assert dij["mean_runtime_ms"] == 11.5

def test_group_mean_multi_by():
    res = group_mean(ROWS, by=["generator", "algorithm"], fields=("path_length",))
    keys = [(r["generator"], r["algorithm"]) for r in res]
    assert ("dfs_backtracker", "bfs") in keys and ("prim", "dijkstra") in keys

def test_percentiles_runtime():
    p = percentiles(ROWS, field="runtime_ms", q=(50, 75, 90))
    # runtime values are [4.0, 5.0, 11.0, 12.0] -> p50=5.0, p75=11.0, p90=12.0 (nearest-rank)
    assert p[50] == 5.0 and p[75] == 11.0 and p[90] == 12.0

def test_groupby_agg_mixed_ops():
    res = groupby_agg(ROWS, by="algorithm", agg={"runtime_ms": "mean", "path_length": "max"})
    bfs = next(r for r in res if r["algorithm"] == "bfs")
    dij = next(r for r in res if r["algorithm"] == "dijkstra")
    assert bfs["mean_runtime_ms"] == 4.5 and bfs["max_path_length"] == 8.0
    assert dij["mean_runtime_ms"] == 11.5 and dij["max_path_length"] == 12.0

def test_empty_inputs_are_graceful():
    assert group_mean([], by="algorithm") == []
    assert percentiles([], field="runtime_ms") == {}
    assert groupby_agg([], by="algorithm", agg={"runtime_ms": "mean"}) == []
