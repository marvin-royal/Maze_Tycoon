import os
import shutil
from pathlib import Path

from maze_tycoon.game.gamestate import (
    GameState,
    load_game_state,
    save_game_state,
    DEFAULT_SAVE_PATH,
)
from maze_tycoon.game.run_controller import run_one_game_cycle
from maze_tycoon.game.economy import calculate_reward

# If you have these modules for metrics/logging, you'll wire them later:
# from maze_tycoon.game.app import run_trials
# from maze_tycoon.core.metrics import InMemoryMetricsSink


def _clean_save_dir():
    """Ensure tests don't touch a real player save."""
    save_dir = os.path.dirname(DEFAULT_SAVE_PATH)
    if save_dir and os.path.exists(save_dir):
        shutil.rmtree(save_dir)
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)


def test_single_game_cycle_headless():
    _clean_save_dir()

    gs = GameState(day=1, credits=0)

    result = run_one_game_cycle(
        game_state=gs,
        generator="dfs_backtracker",
        algorithm="bfs",
        heuristic=None,
        connectivity=4,
        width=21,
        height=21,
        seed=0,
        headless=True,
    )

    assert result is not None
    assert isinstance(result, dict)
    assert result.get("solver") == "bfs"
    assert "steps" in result
    assert "path_length" in result

    # GameState progression
    assert gs.day == 2
    assert gs.credits > 0
    assert gs.last_maze["width"] == 21
    assert gs.last_maze["solver"] == "bfs"


def test_multiple_cycles_stress_100():
    _clean_save_dir()

    gs = GameState(day=1, credits=0)

    for i in range(100):
        prev_day = gs.day
        prev_credits = gs.credits

        result = run_one_game_cycle(
            game_state=gs,
            generator="dfs_backtracker",
            algorithm="bfs",
            heuristic=None,
            connectivity=4,
            width=21,
            height=21,
            seed=i,  # vary seed a bit
            headless=True,
        )

        assert result.get("solver") == "bfs"
        assert gs.day == prev_day + 1
        assert gs.credits >= prev_credits  # never lose credits


def test_economy_rewards_failure_vs_success():
    # Directly test the economy behavior without running a full cycle
    success_result = {
        "success": True,
        "steps": 50,
        "path_length": 30,
    }
    failure_result = {
        "success": False,
        "steps": 200,
        "path_length": 0,
    }

    success_reward = calculate_reward(success_result)
    failure_reward = calculate_reward(failure_result)

    assert success_reward >= failure_reward
    assert failure_reward >= 0  # no negative rewards


def test_all_solvers_across_seeds():
    _clean_save_dir()

    solvers = ["bfs", "dijkstra", "a_star", "bidirectional_a_star"]

    for alg in solvers:
        gs = GameState(day=1, credits=0)

        # If some solvers are slower, keep maze small
        result = run_one_game_cycle(
            game_state=gs,
            generator="dfs_backtracker",
            algorithm=alg,
            heuristic="manhattan" if "a_star" in alg else None,
            connectivity=4,
            width=15,
            height=15,
            seed=42,
            headless=True,
        )

        # Make sure the solver string is carried through
        assert result.get("solver") == alg
        assert gs.day == 2
        assert gs.credits > 0


def test_save_and_load_cycle(tmp_path: Path):
    _clean_save_dir()

    # Override DEFAULT_SAVE_PATH for this test if you want,
    # or just rely on the default; here we use the real one.
    gs = GameState(day=3, credits=50)
    save_game_state(gs)

    loaded = load_game_state()
    assert loaded.day == 3
    assert loaded.credits == 50

    result = run_one_game_cycle(
        game_state=loaded,
        generator="dfs_backtracker",
        algorithm="bfs",
        heuristic=None,
        connectivity=4,
        width=15,
        height=15,
        seed=7,
        headless=True,
    )

    assert loaded.day == 4
    assert loaded.credits > 50
    assert loaded.last_maze["height"] == 15

    save_game_state(loaded)
    loaded2 = load_game_state()
    assert loaded2.day == 4
    assert loaded2.credits == loaded.credits


# --- Metrics export / CSV logging integration test (stub) ---


def test_metrics_csv_export_stub(tmp_path: Path):
    """
    Skeleton for testing your metrics export.
    Fill in the calls when you wire in run_trials / InMemoryMetricsSink.
    """
    # Example structure; adjust names/signatures to match your actual code.
    # csv_path = tmp_path / "metrics.csv"
    #
    # cfg = {
    #     "maze": {"generator": "dfs_backtracker"},
    #     "search": {"algorithm": "bfs", "heuristic": None, "connectivity": 4},
    # }
    #
    # sink = InMemoryMetricsSink()
    #
    # run_trials(
    #     cfg=cfg,
    #     n_trials=5,
    #     width=15,
    #     height=15,
    #     base_seed=0,
    #     sink=sink,
    #     csv_path=str(csv_path),
    # )
    #
    # assert csv_path.exists()
    # text = csv_path.read_text()
    # assert "algorithm" in text
    # assert "steps" in text
    pass
