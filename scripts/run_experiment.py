# scripts/run_experiment.py  (refactored)
from __future__ import annotations
import argparse, csv, time
from datetime import datetime
from pathlib import Path

from maze_tycoon.io.config_loader import load_yaml
from maze_tycoon.core.vis import render_ascii
from maze_tycoon.game.app import run_once  # <- use the new engine
from maze_tycoon.core.metrics import InMemoryMetricsSink

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
    out_csv = out_dir / f"{exp}{('-' + tag) if tag else ''}-{stamp}.csv"

    sizes = cfg["maze"]["sizes"]
    trials = int(cfg.get("trials", 1))
    base_seed = int(cfg.get("seed", 0))

    fieldnames = [
        "trial", "width", "height", "seed",
        "generator", "algorithm", "heuristic",
        "path_length", "node_expansions", "runtime_ms",
    ]

    sink = InMemoryMetricsSink()

    with out_csv.open("w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=fieldnames)
        wr.writeheader()

        for w, h in sizes:
            for t in range(trials):
                need_mat = args.ascii_all or (args.ascii and t == 0)
                ret = run_once(cfg, width=w, height=h, trial_idx=t, base_seed=base_seed,
                               return_matrix=need_mat, sink=sink)
                if need_mat:
                    row, mat = ret  # type: ignore[misc]
                    wr.writerow(row)
                    print(f"\n=== {w}x{h} trial {t} seed={row['seed']} gen={row['generator']} alg={row['algorithm']} ===")
                    print(render_ascii(mat))
                else:
                    wr.writerow(ret)  # type: ignore[arg-type]

    # quick summary
    avg = sink.aggregate()
    print(f"[OK] Wrote results to {out_csv}")
    if avg:
        print(f"avg path_length={avg.get('path_length')}, "
              f"expansions={avg.get('node_expansions')}, runtime_ms={avg.get('runtime_ms')}")
    

if __name__ == "__main__":
    main()
