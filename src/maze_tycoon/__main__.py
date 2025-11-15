from __future__ import annotations
import argparse

from .game.ui_adapter import demo_walk_loop, view_real_run_with_pygame


def main() -> None:
    p = argparse.ArgumentParser()

    p.add_argument(
        "--mode",
        choices=["demo", "real"],
        default="demo",
        help="demo = looping L-walk, real = generate+solve and animate",
    )

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

    p.add_argument("--width", type=int, default=21)
    p.add_argument("--height", type=int, default=21)
    p.add_argument("--seed", type=int, default=0)

    args = p.parse_args()

    if args.mode == "demo":
        demo_walk_loop()
        return

    heuristic = args.heuristic
    if heuristic is None and args.alg in ("a_star", "bidirectional_a_star"):
        heuristic = "manhattan"  # or your preferred default

    cfg = {
        "maze": {"generator": args.gen},
        "search": {
            "algorithm": args.alg,
            "heuristic": heuristic,
            "connectivity": args.connectivity,
        },
    }

    view_real_run_with_pygame(
        cfg,
        width=args.width,
        height=args.height,
        base_seed=args.seed,
    )


if __name__ == "__main__":
    main()
