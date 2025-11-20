from __future__ import annotations
from typing import Optional, Dict, Any

from .gamestate import GameState
from .economy import calculate_reward  # (You will create this)
from .ui_adapter import view_real_run_with_pygame


def run_one_game_cycle(
    game_state: GameState,
    generator: str,
    algorithm: str,
    heuristic: Optional[str],
    connectivity: int,
    width: int,
    height: int,
    seed: Optional[int],
    headless: bool = False,
) -> Dict[str, Any]:
    """
    Runs a single generate → solve → animate cycle.
    Updates GameState with reward, last run info, etc.
    Returns the run_result dict produced by the solver/pygame loop.
    """

    # Build solver + maze config
    cfg = {
        "maze": {"generator": generator},
        "search": {
            "algorithm": algorithm,
            "heuristic": heuristic,
            "connectivity": connectivity,
        },
    }

    # Run the actual maze generation & visualization
    run_result = view_real_run_with_pygame(
        game_state=game_state,
        cfg=cfg,
        width=width,
        height=height,
        base_seed=seed,
        headless=headless,
    )

    # Compute economy reward for this run
    reward = calculate_reward(run_result)

    # Update GameState with progression
    game_state.day += 1
    game_state.credits += reward

    # Record details of this run
    game_state.last_maze = {
        "width": width,
        "height": height,
        "solver": algorithm,
        "seed": seed,
        "result": run_result,
    }

    return run_result
