from __future__ import annotations
import time
import importlib
from typing import Any, Dict, Tuple, Optional, Callable, List

from maze_tycoon.core.grid import Grid
from maze_tycoon.core.metrics import InMemoryMetricsSink  # optional dependency
# Generators (add more as you implement them)
from maze_tycoon.generation.dfs_backtracker import generate as gen_dfs
from maze_tycoon.generation.prim import generate as gen_prim
from maze_tycoon.io.serialize import write_csv, write_jsonl, append_jsonl

# Simple registry (generator name -> function(Grid) -> None)
GEN_MAP: Dict[str, Callable[[Grid], None]] = {
    "dfs_backtracker": gen_dfs,
    "prim": gen_prim,
}


def _load_algorithm(name: str) -> Callable[..., Dict[str, Any]]:
    """
    Dynamically load an algorithm module and return its 'solve' callable.
    Ex: name='bfs' -> maze_tycoon.algorithms.bfs.solve(...)
    """
    mod = importlib.import_module(f"maze_tycoon.algorithms.{name}")
    solve = getattr(mod, "solve", None)
    if solve is None:
        raise SystemExit(f"[error] Algorithm '{name}' has no 'solve' function.")
    return solve


def run_once(
    cfg: Dict[str, Any],
    width: int,
    height: int,
    trial_idx: int,
    base_seed: int,
    *,
    return_matrix: bool = False,
    sink: Optional[InMemoryMetricsSink] = None,
) -> Dict[str, Any] | Tuple[Dict[str, Any], List[List[int]]]:
    """
    One end-to-end trial:
      1) Build Grid with deterministic seed
      2) Carve maze using chosen generator
      3) Solve with chosen algorithm (+ heuristic, connectivity)
      4) Normalize metrics and return a summary row
      5) Optionally record to a metrics sink
      6) Optionally return the matrix

    cfg shape (example):
      {
        "maze":   {"generator": "dfs_backtracker"},
        "search": {"algorithm": "bfs", "heuristic": "manhattan", "connectivity": 4}
      }
    """
    # Deterministic per (size, trial)
    seed = (base_seed or 0) + trial_idx + (width * 1000 + height)
    grid = Grid(width, height, seed=seed)

    # Carve maze
    gen_name = cfg["maze"]["generator"]
    gen_fn = GEN_MAP.get(gen_name)
    if gen_fn is None:
        raise SystemExit(f"[error] Unknown generator '{gen_name}'. Choose one of: {', '.join(GEN_MAP.keys())}")
    gen_fn(grid)

    # Convert to matrix for algorithms
    mat = grid.to_matrix()

    # Choose algorithm (dynamic import)
    search = cfg["search"]
    alg_name: str = search["algorithm"]                 # e.g. "bfs", "a_star"
    heuristic: Optional[str] = search.get("heuristic")  # may be None (e.g. BFS)
    connectivity: int = int(search.get("connectivity", 4))  # 4 or 8
    solve = _load_algorithm(alg_name)

    # Run algorithm
    start = (1, 1)
    goal = (len(mat) - 2, len(mat[0]) - 2)
    t0 = time.perf_counter()
    metrics = solve(
        mat,
        start=start,
        goal=goal,
        heuristic=heuristic,
        connectivity=connectivity,
    )
    dt_ms = (time.perf_counter() - t0) * 1000.0

    # Normalize metrics and ensure runtime present
    metrics = metrics or {}
    if metrics.get("runtime_ms") in (None, 0):
        metrics["runtime_ms"] = dt_ms
    metrics.setdefault("path_length", 0)
    metrics.setdefault("node_expansions", 0)

    row: Dict[str, Any] = {
        "trial": trial_idx,
        "width": width,
        "height": height,
        "seed": seed,
        "generator": gen_name,
        "algorithm": alg_name,
        "heuristic": heuristic,
        **metrics,
    }

    # optional metrics sink
    if sink is not None:
        sink.record_trial(row)

    return (row, mat) if return_matrix else row


def run_trials(
    cfg: Dict[str, Any],
    *,
    width: int,
    height: int,
    trials: int,
    base_seed: int = 0,
    sink: Optional[InMemoryMetricsSink] = None,
    return_last_matrix: bool = False,
):
    """
    Convenience orchestration for multiple trials.
    Returns (rows [, last_matrix_if_requested])
    """
    rows: List[Dict[str, Any]] = []
    last_matrix: Optional[List[List[int]]] = None
    for i in range(trials):
        result = run_once(cfg, width, height, i, base_seed, return_matrix=return_last_matrix, sink=sink)
        if return_last_matrix:
            row, last_matrix = result  # type: ignore[assignment]
            rows.append(row)
        else:
            rows.append(result)  # type: ignore[arg-type]
    return (rows, last_matrix) if return_last_matrix else rows


if __name__ == "__main__":
    import json, argparse, os
    p = argparse.ArgumentParser()
    p.add_argument("--gen", default="dfs_backtracker", choices=list(GEN_MAP.keys()))
    p.add_argument("--alg", default="bfs")
    p.add_argument("--heuristic", default=None)
    p.add_argument("--connectivity", type=int, default=4, choices=[4, 8])

    p.add_argument("--width", type=int, default=21)
    p.add_argument("--height", type=int, default=21)
    p.add_argument("--trials", type=int, default=1)
    p.add_argument("--seed", type=int, default=0)

    # ASCII preview
    p.add_argument("--ascii", action="store_true", help="Print ASCII maze for the first trial")
    p.add_argument("--ascii-all", action="store_true", help="Print ASCII maze for every trial")

    # NEW: outputs
    p.add_argument("--csv", type=str, default=None, help="Write rows to CSV at this path")
    p.add_argument("--jsonl", type=str, default=None, help="Write rows to JSONL at this path")
    p.add_argument("--append", action="store_true", help="Append to CSV/JSONL if they already exist")

    args = p.parse_args()

    cfg = {
        "maze": {"generator": args.gen},
        "search": {"algorithm": args.alg, "heuristic": args.heuristic, "connectivity": args.connectivity},
    }

    # Run trials
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
            print(f"\n=== {row['width']}x{row['height']} trial {row['trial']} seed={row['seed']} "
                  f"gen={row['generator']} alg={row['algorithm']} ===")
            # Use last_matrix for the last trial; otherwise re-run minimal render per trial if needed.
            # For simplicity here, show the last captured matrix if present:
            if last_matrix is not None:
                print(render_ascii(last_matrix))

    # NEW: outputs
    if args.csv:
        write_csv(rows, args.csv, append=args.append)
        print(f"[csv] wrote {len(rows)} row(s) to {os.path.abspath(args.csv)}" + (" (append)" if args.append else ""))

    if args.jsonl:
        if args.append:
            append_jsonl(rows, args.jsonl)
        else:
            write_jsonl(rows, args.jsonl)
        print(f"[jsonl] wrote {len(rows)} row(s) to {os.path.abspath(args.jsonl)}" + (" (append)" if args.append else ""))

    # Quick summary
    avg = sink.aggregate()
    if avg:
        print(json.dumps({"avg": avg}, indent=2))
