from __future__ import annotations

import time
from enum import Enum, auto
import pygame
import importlib
import random
from collections import deque
from typing import Any, Dict, Tuple, Optional, Callable, List

from maze_tycoon.core.metrics import InMemoryMetricsSink  # optional dependency
# Generators (add more as you implement them)
from maze_tycoon.generation.dfs_backtracker import generate as gen_dfs
from maze_tycoon.generation.prim import generate as gen_prim
from maze_tycoon.io.serialize import write_csv, write_jsonl, append_jsonl
from maze_tycoon.game.gamestate import GameState, load_game_state, save_game_state
from maze_tycoon.game.economy import calculate_reward
from maze_tycoon.game.engine import run_once, run_trials

MIN_MAZE_SIZE = 10
MAX_MAZE_SIZE = 50

ALGORITHMS = ["bfs", "dijkstra", "a_star", "bidirectional_a_star"]
ALGORITHM_LABELS = {
    "bfs": "BFS (Breadth-First Search)",
    "dijkstra": "Dijkstra",
    "a_star": "A* Search",
    "bidirectional_a_star": "Bidirectional A*",
}
MENU_ITEMS = ["Start Run", "Quit"]

class GameMode(Enum):
    MENU = auto()
    RUNNING = auto()
    SUMMARY = auto()
    QUIT = auto()

def choose_maze_size() -> tuple[int, int]:
    """Random cell-space maze size for interactive runs."""
    w = random.randint(MIN_MAZE_SIZE, MAX_MAZE_SIZE)
    h = random.randint(MIN_MAZE_SIZE, MAX_MAZE_SIZE)

    # Optional: enforce odd sizes if you prefer
    if w % 2 == 0:
        w += 1 if w < MAX_MAZE_SIZE else -1
    if h % 2 == 0:
        h += 1 if h < MAX_MAZE_SIZE else -1
    return w, h

def update_and_draw_menu(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    font: pygame.font.Font,
    game_state: GameState,
    selected_algorithm: str,
) -> tuple[GameMode, str]:
    selected_index = 0
    running = True
    algo_index = ALGORITHMS.index(selected_algorithm)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return GameMode.QUIT, selected_algorithm
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(MENU_ITEMS)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(MENU_ITEMS)
                elif event.key == pygame.K_LEFT:
                    algo_index = (algo_index - 1) % len(ALGORITHMS)
                elif event.key == pygame.K_RIGHT:
                    algo_index = (algo_index + 1) % len(ALGORITHMS)
                elif event.key == pygame.K_RETURN:
                    choice = MENU_ITEMS[selected_index]
                    if choice == "Start Run":
                        return GameMode.RUNNING, ALGORITHMS[algo_index]
                    elif choice == "Quit":
                        return GameMode.QUIT, ALGORITHMS[algo_index]

        selected_algorithm = ALGORITHMS[algo_index]

        # ---- drawing ----
        screen.fill((20, 20, 20))

        title = font.render("Maze Tycoon", True, (250, 250, 250))
        screen.blit(title, (40, 40))

        # Show current day/credits
        stats = font.render(
            f"Day: {game_state.day}   Credits: {game_state.credits}",
            True,
            (200, 200, 200),
        )
        screen.blit(stats, (40, 80))

        # Menu items
        base_y = 140
        for i, item in enumerate(MENU_ITEMS):
            color = (240, 240, 240) if i == selected_index else (120, 120, 120)
            text = font.render(item, True, color)
            screen.blit(text, (80, base_y + i * 40))

        # Algorithm selection line
        algo_label = ALGORITHM_LABELS.get(selected_algorithm, selected_algorithm)
        algo_text = font.render(
            f"Algorithm: {algo_label}   (← / → to change)", True, (180, 220, 250)
        )
        screen.blit(algo_text, (80, base_y + 120))

        pygame.display.flip()
        clock.tick(30)

    return GameMode.QUIT, selected_algorithm

def update_and_draw_summary(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    font: pygame.font.Font,
    game_state: GameState,
    run_result: Dict[str, Any],
) -> GameMode:
    """
    Simple post-run summary screen that stays in the same window.
    """
    # Extract a few convenient fields
    alg = run_result.get("algorithm", "?")
    width = run_result.get("width", "?")
    height = run_result.get("height", "?")
    seed = run_result.get("seed", "?")
    path_len = run_result.get("path_length", "?")
    steps = run_result.get("steps", "?")
    reward = run_result.get("reward", 0)
    credits_before = run_result.get("credits_before", game_state.credits - reward)
    credits_after = run_result.get("credits_after", game_state.credits)

    if not pygame.get_init():
        pygame.init()
    if not pygame.display.get_init():
        pygame.display.init()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return GameMode.QUIT
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                    return GameMode.MENU

        screen.fill((10, 10, 10))

        lines = [
            "Run Summary",
            "",
            f"Algorithm: {alg}",
            f"Maze: {width} x {height}",
            f"Seed: {seed}",
            f"Path length: {path_len}",
            f"Steps: {steps}",
            "",
            f"Reward: {reward}",
            f"Credits: {credits_before} → {credits_after}",
            "",
            "Press Enter to return to menu",
        ]

        y = 60
        for i, line in enumerate(lines):
            color = (240, 240, 240) if i <= 1 else (200, 200, 200)
            text = font.render(line, True, color)
            screen.blit(text, (60, y))
            y += 32

        pygame.display.flip()
        clock.tick(30)

def choose_heuristic(algorithm: str, default: Optional[str] = None) -> Optional[str]:
    """
    For algorithms that like a heuristic (A*, bidirectional A*),
    pick a sensible default if none is set.
    """
    if default is not None:
        return default
    if algorithm in ("a_star", "bidirectional_a_star"):
        return "manhattan"
    return None

def run_interactive_game() -> None:
    """
    Main interactive game loop for Maze Tycoon using a single pygame window.

    Modes:
      - MENU:    choose action + algorithm
      - RUNNING: perform one maze run (headless for now)
      - SUMMARY: show results, then go back to menu
    """
    pygame.init()
    screen = pygame.display.set_mode((900, 600))
    pygame.display.set_caption("Maze Tycoon")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 24)

    # Load or create GameState
    try:
        game_state = load_game_state()
    except Exception:
        game_state = GameState()

    selected_algorithm = "bfs"
    current_mode = GameMode.MENU
    last_run_result: Optional[Dict[str, Any]] = None
    running = True

    while running:
        if current_mode == GameMode.MENU:
            current_mode, selected_algorithm = update_and_draw_menu(
                screen,
                clock,
                font,
                game_state,
                selected_algorithm,
            )

        elif current_mode == GameMode.RUNNING:
            width, height = choose_maze_size()
            seed = random.randint(0, 10_000_000)
            heuristic = choose_heuristic(selected_algorithm)
            credits_before = game_state.credits

            # --- Build cfg exactly like run_controller does ---
            cfg = {
                "maze": {"generator": "dfs_backtracker"},
                "search": {
                    "algorithm": selected_algorithm,
                    "heuristic": heuristic,
                    "connectivity": 4,
                },
            }

            # --- Animated run through ui_adapter ---
            from maze_tycoon.game.ui_adapter import view_real_run_with_pygame
            run_result = view_real_run_with_pygame(
                cfg=cfg,
                game_state=game_state,
                width=width,
                height=height,
                base_seed=seed,
                headless=False,   # this enables animation
            )

            screen = pygame.display.get_surface() or screen

            # --- Apply game rules yourself here ---
            from maze_tycoon.game.economy import calculate_reward
            reward = calculate_reward(run_result)

            game_state.day += 1
            game_state.credits += reward

            last_run_result = {
                **run_result,
                "reward": reward,
                "credits_before": credits_before,
                "credits_after": game_state.credits,
                "width": width,
                "height": height,
                "seed": seed,
                "algorithm": selected_algorithm,
            }

            current_mode = GameMode.SUMMARY


        elif current_mode == GameMode.SUMMARY:
            if last_run_result is None:
                current_mode = GameMode.MENU
            else:
                mode_after = update_and_draw_summary(
                    screen,
                    clock,
                    font,
                    game_state,
                    last_run_result,
                )
                current_mode = mode_after

        elif current_mode == GameMode.QUIT:
            running = False

        # Persist game state occasionally (you can make this smarter)
        save_game_state(game_state)

    pygame.quit()


if __name__ == "__main__":
    import json, argparse, os
    p = argparse.ArgumentParser()
    p.add_argument("--gen", default="dfs_backtracker", choices=list("dfs_backtracker prim".split()))
    p.add_argument("--alg", default="bfs")
    p.add_argument("--heuristic", default=None)
    p.add_argument("--connectivity", type=int, default=4, choices=[4, 8])

    p.add_argument("--width", type=int, default=21)
    p.add_argument("--height", type=int, default=21)
    p.add_argument("--trials", type=int, default=1)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument(
        "--mode",
        choices=["batch", "interactive"],
        default="batch",
        help="batch = run trials/headless (default), interactive = single-window game loop",
    )

    # ASCII preview
    p.add_argument("--ascii", action="store_true", help="Print ASCII maze for the first trial")
    p.add_argument("--ascii-all", action="store_true", help="Print ASCII maze for every trial")

    # NEW: outputs
    p.add_argument("--csv", type=str, default=None, help="Write rows to CSV at this path")
    p.add_argument("--jsonl", type=str, default=None, help="Write rows to JSONL at this path")
    p.add_argument("--append", action="store_true", help="Append to CSV/JSONL if they already exist")

    args = p.parse_args()

    if args.mode == "interactive":
        run_interactive_game()
        raise SystemExit(0)

    # ---- batch (headless) mode ----
    cfg = {
        "maze": {"generator": args.gen},
        "search": {
            "algorithm": args.alg,
            "heuristic": args.heuristic,
            "connectivity": args.connectivity,
        },
    }

    from maze_tycoon.core.metrics import InMemoryMetricsSink
    sink = InMemoryMetricsSink()
    rows = run_trials(
        cfg,
        width=args.width,
        height=args.height,
        trials=args.trials,
        base_seed=args.seed,
        sink=sink,
        return_last_matrix=args.ascii or args.ascii_all,
    )

    # Unpack matrix if requested for ASCII display
    last_matrix = None
    if isinstance(rows, tuple):
        rows, last_matrix = rows  # rows: list[dict], last_matrix: list[list[int]]

    # ASCII printing
    if args.ascii or args.ascii_all:
        from maze_tycoon.core.vis import render_ascii
        for i, row in enumerate(rows):
            if args.ascii and i > 0:
                break
            print(
                f"\n=== {row['width']}x{row['height']} trial {row['trial']} seed={row['seed']} "
                f"gen={row['generator']} alg={row['algorithm']} ==="
            )
            if last_matrix is not None:
                print(render_ascii(last_matrix))

    # Outputs
    if args.csv:
        write_csv(rows, args.csv, append=args.append)
        print(
            f"[csv] wrote {len(rows)} row(s) to {os.path.abspath(args.csv)}"
            + (" (append)" if args.append else "")
        )

    if args.jsonl:
        if args.append:
            append_jsonl(rows, args.jsonl)
        else:
            write_jsonl(rows, args.jsonl)
        print(
            f"[jsonl] wrote {len(rows)} row(s) to {os.path.abspath(args.jsonl)}"
            + (" (append)" if args.append else "")
        )

    # Quick summary
    avg = sink.aggregate()
    if avg:
        print(json.dumps({"avg": avg}, indent=2))
