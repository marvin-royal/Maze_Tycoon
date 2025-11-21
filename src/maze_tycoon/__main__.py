from __future__ import annotations
import argparse
import os
import random

from .game.gamestate import (
    GameState,
    load_game_state,
    save_game_state,
    DEFAULT_SAVE_PATH,
)
from .game.menu import run_menu_screen
from .game.run_controller import run_one_game_cycle
from .game.ui_adapter import demo_walk_loop
from .io.logging import init_logging, get_logger


def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument(
        "--mode",
        choices=["menu", "demo", "real"],
        default="menu",
        help="menu = main game loop, demo = L-walk, real = single run (no menu)",
    )

    # Defaults for real/menu runs – you can tune these later or add menus for them
    p.add_argument(
        "-g", "--gen", "--generator",
        default="dfs_backtracker",
        help="Maze generator (e.g. dfs_backtracker, prim)",
    )

    p.add_argument(
        "-a", "--alg", "--algorithm",
        default="bfs",
        help="Search algorithm (e.g. bfs, a_star, dijkstra)",
    )

    p.add_argument(
        "--heuristic",
        default=None,
        help="Heuristic for informed algorithms (e.g. manhattan)",
    )

    p.add_argument(
        "--connectivity",
        type=int,
        default=4,
        help="Grid connectivity (4 or 8)",
    )

    p.add_argument("--width", type=int, default=None, help="Maze width (cells)")
    p.add_argument("--height", type=int, default=None, help="Maze height (cells)")
    p.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Base seed for maze generation (defaults to day or random)",
    )

    return p.parse_args()


def _ensure_gamestate_for_action(action: str) -> GameState:
    """
    Helper used in menu mode: decide how to produce a GameState based on
    menu selection and presence of a save file.
    """
    if action == "start":
        # Always start fresh
        return GameState()

    if action in ("continue", "load"):
        if os.path.exists(DEFAULT_SAVE_PATH):
            return load_game_state()
        # No save yet – fall back to a new game
        return GameState()

    # Fallback – should not hit this in normal flow
    return GameState()


def _choose_seed(args, game_state: GameState) -> int:
    """
    Decide on a seed for this run.

    Priority:
      1. explicit --seed from CLI
      2. random new seed (every run)
    """
    # 1. User explicitly sets a seed from command-line
    if args.seed is not None:
        return args.seed

    # 2. Always generate a fresh random seed for each run
    return random.randint(0, 10_000_000)

def _choose_maze_size(
    args,
    game_state: GameState | None,
    seed: int | None,
) -> tuple[int, int]:
    """
    Choose a maze size in *cell space*.

    - If the user explicitly passed --width/--height, respect that.
    - Otherwise pick a random size between 10 and 50 cells (inclusive).
    """

    MIN_SIZE = 10
    MAX_SIZE = 50

    # If user explicitly set width/height on the CLI, use those.
    if args.width is not None and args.height is not None:
        return args.width, args.height

    # Otherwise, pick random sizes per run.
    # (If you want reproducible sizes, you *can* seed this with `seed`.)
    def pick_dim() -> int:
        n = random.randint(MIN_SIZE, MAX_SIZE)
        # Optional: keep odd dimensions for nicer mazes
        if n % 2 == 0:
            if n == MAX_SIZE:
                n -= 1
            else:
                n += 1
        return n

    width = pick_dim()
    height = pick_dim()
    return width, height

def main() -> None:
    args = parse_args()

    # Initialise logging once for the whole app
    init_logging(mode="game", log_dir="logs")
    app_logger = get_logger("app")
    app_logger.info("Maze Tycoon started (mode=%s)", args.mode)

    # DEMO MODE: Just the looping L-walk, no game state, no menu.
    if args.mode == "demo":
        demo_walk_loop()
        return

    # REAL MODE: One-off run, no menu, but still updates GameState once.
    if args.mode == "real":
        if os.path.exists(DEFAULT_SAVE_PATH):
            game_state = load_game_state()
        else:
            game_state = GameState()

        seed = _choose_seed(args, game_state)

        # Pick maze size for this run
        width, height = _choose_maze_size(args, game_state, seed)

        # Auto-heuristic if not provided
        heuristic = args.heuristic
        if heuristic is None and args.alg in ("a_star", "bidirectional_a_star"):
            heuristic = "manhattan"

        run_one_game_cycle(
            game_state=game_state,
            generator=args.gen,
            algorithm=args.alg,
            heuristic=heuristic,
            connectivity=args.connectivity,
            width=width,
            height=height,
            seed=seed,
            headless=False,
        )
        save_game_state(game_state)
        return

    # MENU MODE (default): menu → run → back to menu in a loop
    game_state: GameState | None = None

    while True:
        action = run_menu_screen()  # "start", "continue", "load", or "quit"

        if action == "quit":
            break

        # Get or create GameState based on menu choice
        game_state = _ensure_gamestate_for_action(action)

        # Decide on seed for this run
        seed = _choose_seed(args, game_state)

        # Decide on maze size (random 40–60, tied to seed)
        width, height = _choose_maze_size(args, game_state, seed)

        # Auto-heuristic if not provided
        heuristic = args.heuristic
        if heuristic is None and args.alg in ("a_star", "bidirectional_a_star"):
            heuristic = "manhattan"

        # 🔁 Run a single full cycle: generate → solve → animate → update GameState
        run_one_game_cycle(
            game_state=game_state,
            generator=args.gen,
            algorithm=args.alg,
            heuristic=heuristic,
            connectivity=args.connectivity,
            width=width,
            height=height,
            seed=seed,
            headless=False,
        )

        save_game_state(game_state)

        # When the maze window closes, the while-loop continues
        # and the menu window will come back on the next iteration.


if __name__ == "__main__":
    main()
