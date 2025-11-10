def test_run_once_smoke():
    from maze_tycoon.game.app import run_once
    cfg = {"maze": {"generator": "dfs_backtracker"}, "search": {"algorithm": "bfs", "connectivity": 4}}
    row = run_once(cfg, width=15, height=15, trial_idx=0, base_seed=42)
    assert isinstance(row, dict)
    assert "path_length" in row and "node_expansions" in row and "runtime_ms" in row

def test_run_trials_with_sink_and_matrix():
    from maze_tycoon.game.app import run_trials
    from maze_tycoon.core.metrics import InMemoryMetricsSink
    cfg = {"maze": {"generator": "prim"}, "search": {"algorithm": "bfs", "connectivity": 4}}
    sink = InMemoryMetricsSink()
    (rows, mat) = run_trials(cfg, width=11, height=11, trials=2, base_seed=7, sink=sink, return_last_matrix=True)
    assert len(rows) == 2 and mat is not None and len(sink) == 2
    avg = sink.aggregate()
    assert set(["path_length", "node_expansions", "runtime_ms"]).issubset(avg.keys())
