# scripts/run_experiment.py
from __future__ import annotations
import argparse, csv, time
from datetime import datetime
from pathlib import Path
import sys

# --- src layout bootstrap (do this BEFORE importing your package) ---
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# --- now import your package modules ---
from maze_tycoon.io.config_loader import load_yaml
from maze_tycoon.core import Grid
from maze_tycoon.core.vis import render_ascii         # <- import from core.vis
from maze_tycoon.generation.dfs_backtracker import generate as carve_dfs
from maze_tycoon.generation.prim import generate as carve_prim

# Optional: stub BFS until your real BFS/A* is wired
def stub_bfs(matrix, start=(1, 1), goal=None):
    return {"path_length": 0, "node_expansions": 0, "runtime_ms": 0.0}

GEN_MAP = {
    "dfs_backtracker": carve_dfs,
    "prim": carve_prim,
}

def run_once(cfg, width: int, height: int, trial_idx: int, base_seed: int, *, return_matrix: bool = False):
    # Deterministic per (size, trial)
    seed = (base_seed or 0) + trial_idx + (width * 1000 + height)
    grid = Grid(width, height, seed=seed)

    # Carve maze
    gen = GEN_MAP[cfg["maze"]["generator"]]
    gen(grid)

    # Convert to matrix for algorithms
    mat = grid.to_matrix()

    # Choose algorithm
    alg = cfg["search"]["algorithm"]
    t0 = time.perf_counter()
    if alg == "bfs":
        metrics = stub_bfs(mat)  # replace with real BFS
    else:
        metrics = {"path_length": None, "node_expansions": None, "runtime_ms": None}

    dt_ms = (time.perf_counter() - t0) * 1000.0
    if metrics.get("runtime_ms") in (None, 0):
        metrics["runtime_ms"] = dt_ms

    row = {
        "trial": trial_idx,
        "width": width,
        "height": height,
        "seed": seed,
        "generator": cfg["maze"]["generator"],
        "algorithm": alg,
        "heuristic": cfg["search"].get("heuristic"),
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
                    print(f"\n=== {w}x{h} trial {t} seed={row['seed']} gen={row['generator']} ===")
                    print(render_ascii(mat))
                else:
                    wr.writerow(ret)

    print(f"[OK] Wrote results to {out_csv}")

if __name__ == "__main__":
    main()
