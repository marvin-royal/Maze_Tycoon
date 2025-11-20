# game/gamestate.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any
import json
import os

DEFAULT_SAVE_PATH = "saves/game_state.json"


@dataclass
class GameState:
    # Overall player progression
    day: int = 1
    credits: int = 0

    # Unlockables (future upgrades)
    unlocked_solvers: Dict[str, bool] = field(
        default_factory=lambda: {
            "bfs": True,
            "dijkstra": False,
            "a_star": False,
            "bidirectional_a_star": False,
        }
    )

    # Track last run details for "Continue/Replay"
    last_maze: Dict[str, Any] = field(
        default_factory=lambda: {
            "width": 20,
            "height": 20,
            "solver": "bfs",
            "seed": None,
            "result": None,
        }
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "day": self.day,
            "credits": self.credits,
            "unlocked_solvers": self.unlocked_solvers,
            "last_maze": self.last_maze,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "GameState":
        return GameState(
            day=data.get("day", 1),
            credits=data.get("credits", 0),
            unlocked_solvers=data.get("unlocked_solvers", {}),
            last_maze=data.get("last_maze", {}),
        )


def save_game_state(game_state: GameState, path: str = DEFAULT_SAVE_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(game_state.to_dict(), f, indent=4)


def load_game_state(path: str = DEFAULT_SAVE_PATH) -> GameState:
    if not os.path.exists(path):
        return GameState()
    with open(path, "r") as f:
        data = json.load(f)
        return GameState.from_dict(data)
