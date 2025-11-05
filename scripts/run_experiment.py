# scripts/run_experiment.py
from __future__ import annotations
import argparse, csv, time
from datetime import datetime
from pathlib import Path
import sys
from importlib import import_module

# --- src layout bootstrap (do this BEFORE importing your package) ---
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# --- now import your package modules ---
from maze_tycoon.io.config_loader import load_yaml
from maze_tycoon.core import Grid
from maze_tycoon.core.vis import render_ascii
from maze_tycoon.generation.dfs_backtracker import generate as carve_dfs
from maze_tycoon.generation.prim import generate as carve_prim

GEN_MAP = {
    "dfs_backtracker": carve_dfs,
    "prim": carve_prim,
}

def _load_algorithm(name: str):
    """Dynamically import maze_tycoon.algorithms.<name> and return its solve()"""
    try:
        mod = import_module(f"maze_tycoon.algorithms.{name}")
    except ModuleNotFoundError as e:
        raise SystemExit(
            f"[error] Algorithm module not found: maze_tycoon.algorithms.{name}\n"
            f"Create src/maze_tycoon/algorithms/{name}.py with a solve(matrix, **kwargs) function."
        ) from e
    if not hasattr(mod, "solve"):
        raise SystemExit(
            f"[error] Algorithm '{name}' has no solve() function.\n"
            f"Define: solve(matrix, start=(1,1), goal=None, heuristic=None, connectivity=4, **kwargs) -> dict"
        )
    return mod.solve

def run_once(cfg, width: int, height: int, trial_idx: int, base_seed: int, *, return_matrix: bool = False):
    # Deterministic per (size, trial)
    seed = (base_seed or 0) + trial_idx + (width * 1000 + height)
    grid = Grid(width, height, seed=seed)

    # Carve maze
    gen_name = cfg["maze"]["generator"]
    if gen_name not in GEN_MAP:
        raise SystemExit(f"[error] Unknown generator '{gen_name}'. Choose one of: {', '.join(GEN_MAP.keys())}")
    GEN_MAP[gen_name](grid)

    # Convert to matrix for algorithms
    mat = grid.to_matrix()

    # Choose algorithm (dynamic import)
    alg_name = cfg["search"]["algorithm"]               # e.g., "bfs", "a_star"
    heuristic = cfg["search"].get("heuristic")          # e.g., "manhattan", "octile", "euclidean" (may be None for BFS)
    connectivity = int(cfg["search"].get("connectivity", 4))  # 4 or 8
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

    row = {
        "trial": trial_idx,
        "width": width,
        "height": height,
        "seed": seed,
        "generator": gen_name,
        "algorithm": alg_name,
        "heuristic": heuristic,
        **metrics,
    }
    return (row, mat) if return_matrix else row

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", "-c", required=True, help="Path to YAML experiment config")
    ap.add_argument("--ascii", action="store_true", help="Print ASCII maze (first trial per size)")
    ap.add_argument("--ascii-all", action="store_true", help="Print ASCII maze for every trial")
    args = ap.parse_args()

    cfg = load_yaml(args.config)
    exp = cfg.get("experiment", "run")
    out_dir = Path(cfg["output"]["dir"]).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    tag = cfg["output"].get("tag", "")
    fname = f"{exp}{('-' + tag) if tag else ''}-{stamp}.csv"
    out_csv = out_dir / fname

    sizes = cfg["maze"]["sizes"]
    trials = int(cfg.get("trials", 1))
    base_seed = cfg.get("seed", 0)

    fieldnames = [
        "trial", "width", "height", "seed",
        "generator", "algorithm", "heuristic",
        "path_length", "node_expansions", "runtime_ms",
    ]
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=fieldnames)
        wr.writeheader()
        for w, h in sizes:
            for t in range(trials):
                need_mat = args.ascii_all or (args.ascii and t == 0)
                ret = run_once(cfg, w, h, t, base_seed, return_matrix=need_mat)
                if need_mat:
                    row, mat = ret
                    wr.writerow(row)
                    print(f"\n=== {w}x{h} trial {t} seed={row['seed']} gen={row['generator']} alg={row['algorithm']} ===")
                    print(render_ascii(mat))
                else:
                    wr.writerow(ret)

    print(f"[OK] Wrote results to {out_csv}")

if __name__ == "__main__":
    main()
