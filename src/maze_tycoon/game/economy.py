# game/economy.py
from __future__ import annotations
from typing import Mapping, Any


def calculate_reward(run_result: Mapping[str, Any]) -> int:
    """
    Compute credits earned from a single maze run.

    Robust against missing / None values in run_result.
    Expected (but not required) keys:
      - success: bool
      - steps: int
      - path_length: int
    """

    # Success flag: default to True if missing
    success = bool(run_result.get("success", True))

    # Safely coerce steps to an int, defaulting to 0
    steps_raw = run_result.get("steps")
    try:
        steps = int(steps_raw) if steps_raw is not None else 0
    except (TypeError, ValueError):
        steps = 0

    # Safely coerce path_length to an int, defaulting to 0
    path_len_raw = run_result.get("path_length")
    try:
        path_length = int(path_len_raw) if path_len_raw is not None else 0
    except (TypeError, ValueError):
        path_length = 0

    # Simple model:
    # - failed run: small pity reward
    # - successful run: base + bonuses that decay with more steps/longer path
    if not success:
        return 2  # small pity reward, but never negative

    base = 10

    # Fewer steps → larger bonus, but clamp so we never go negative
    # If steps == 0 (unknown), this just gives a big bonus, which is fine for now.
    steps_term = max(1, 50 - steps // 2)

    # Shorter path → bonus; again clamped
    path_term = max(1, 30 - path_length)

    reward = base + steps_term + path_term
    return max(0, reward)
