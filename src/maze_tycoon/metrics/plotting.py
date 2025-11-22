import os, glob, json, math
from collections import defaultdict
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# CONFIG
# -----------------------------
RESULTS_DIR = r"C:\Learning and Continued Education\Course Studies\Artificial Intelligence\Assignments\Final Project\Maze_Tycoon\results"
OUT_DIR = os.path.join(RESULTS_DIR, "figures")
os.makedirs(OUT_DIR, exist_ok=True)

# Maze Tycoon-ish styling (subtle, readable)
plt.rcParams.update({
    "figure.figsize": (7, 4.5),
    "axes.grid": True,
    "grid.alpha": 0.25,
    "axes.titleweight": "bold",
    "font.size": 11
})

# -----------------------------
# LOAD ALL JSONL FILES
# -----------------------------
def load_jsonl(path):
    rows = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            rows.append(json.loads(line))
    return rows

all_files = sorted(glob.glob(os.path.join(RESULTS_DIR, "*.jsonl")))
assert all_files, f"No .jsonl files found in {RESULTS_DIR}"

datasets = {}  # name -> list[dict]
for fp in all_files:
    name = os.path.splitext(os.path.basename(fp))[0]
    datasets[name] = load_jsonl(fp)

print(f"Loaded {len(datasets)} datasets:")
for k, v in datasets.items():
    print(f"  {k}: {len(v)} rows")

# -----------------------------
# NORMALIZE FIELDS
# -----------------------------
def normalize_row(r):
    # standardize keys
    alg = r.get("algorithm") or r.get("solver") or "?"
    gen = r.get("generator") or r.get("gen") or "?"
    heuristic = r.get("heuristic") or "none"
    path = r.get("path") or []
    visited = r.get("visited") or []
    steps = r.get("steps")
    if steps is None:
        steps = max(0, len(path) - 1)

    return {
        **r,
        "algorithm": alg,
        "generator": gen,
        "heuristic": heuristic,
        "path_length": r.get("path_length", len(path)),
        "visited_count": len(visited),
        "steps": steps,
    }

flat_rows = []
for name, rows in datasets.items():
    for r in rows:
        nr = normalize_row(r)
        nr["dataset"] = name
        flat_rows.append(nr)

df = pd.DataFrame(flat_rows)
df.to_csv(os.path.join(OUT_DIR, "all_results_flat.csv"), index=False)

# -----------------------------
# 2) PATH LENGTH DISTRIBUTIONS
# -----------------------------
def plot_path_distributions(df):
    for (alg, gen), sub in df.groupby(["algorithm", "generator"]):
        vals = sub["path_length"].dropna()
        plt.figure()
        plt.hist(vals, bins=20)
        plt.title(f"Path Length Distribution — {alg} / {gen}")
        plt.xlabel("Path Length")
        plt.ylabel("Frequency")
        out = os.path.join(OUT_DIR, f"path_dist_{alg}_{gen}.png")
        plt.tight_layout()
        plt.savefig(out, dpi=200)
        plt.close()

plot_path_distributions(df)

# -----------------------------
# 3) VISITED-NODE COMPARISONS (boxplot)
# -----------------------------
def plot_visited_comparison(df):
    plt.figure()
    algs = sorted(df["algorithm"].unique())
    data = [df[df["algorithm"] == a]["visited_count"].dropna() for a in algs]
    plt.boxplot(data, labels=algs)
    plt.title("Visited Node Comparison by Algorithm")
    plt.ylabel("# Visited Nodes")
    out = os.path.join(OUT_DIR, "visited_comparison_box.png")
    plt.tight_layout()
    plt.savefig(out, dpi=200)
    plt.close()

plot_visited_comparison(df)

# -----------------------------
# 4) STEP-COUNT COMPARISONS (boxplot)
# -----------------------------
def plot_step_comparison(df):
    plt.figure()
    algs = sorted(df["algorithm"].unique())
    data = [df[df["algorithm"] == a]["steps"].dropna() for a in algs]
    plt.boxplot(data, labels=algs)
    plt.title("Step Count Comparison by Algorithm")
    plt.ylabel("# Steps")
    out = os.path.join(OUT_DIR, "steps_comparison_box.png")
    plt.tight_layout()
    plt.savefig(out, dpi=200)
    plt.close()

plot_step_comparison(df)

# -----------------------------
# 5) SOLVER HEATMAPS (visited frequency)
# -----------------------------
def make_heatmap_for_dataset(rows, title, out_path):
    # pick first row for dimensions
    r0 = rows[0]
    H = r0.get("height")
    W = r0.get("width")
    if H is None or W is None:
        print(f"Skipping heatmap {title}: no H/W in rows")
        return

    heat = np.zeros((H, W), dtype=np.float32)
    for r in rows:
        for (y, x) in r.get("visited", []):
            if 0 <= y < H and 0 <= x < W:
                heat[y, x] += 1

    plt.figure()
    plt.imshow(heat, interpolation="nearest")
    plt.title(title)
    plt.colorbar(label="Visit Frequency")
    plt.tight_layout()
    plt.savefig(out_path, dpi=220)
    plt.close()

for name, rows in datasets.items():
    # group by algorithm inside each dataset
    by_alg = defaultdict(list)
    for r in rows:
        by_alg[normalize_row(r)["algorithm"]].append(r)

    for alg, alg_rows in by_alg.items():
        out = os.path.join(OUT_DIR, f"heatmap_{name}_{alg}.png")
        make_heatmap_for_dataset(
            alg_rows,
            title=f"Visited Heatmap — {alg} ({name})",
            out_path=out
        )

# -----------------------------
# 6) ALGORITHM RANKING TABLES
# -----------------------------
def make_ranking_table(df):
    summary = (
        df.groupby(["algorithm"])
          .agg(
              avg_path=("path_length", "mean"),
              avg_visited=("visited_count", "mean"),
              avg_steps=("steps", "mean"),
              success_rate=("success", "mean") if "success" in df.columns else ("path_length","count")
          )
          .reset_index()
    )

    # lower is better for path/visited/steps
    summary["rank_path"] = summary["avg_path"].rank(method="min")
    summary["rank_visited"] = summary["avg_visited"].rank(method="min")
    summary["rank_steps"] = summary["avg_steps"].rank(method="min")

    summary["overall_rank"] = (
        summary["rank_path"]
        + summary["rank_visited"]
        + summary["rank_steps"]
    ).rank(method="min")

    summary = summary.sort_values("overall_rank")
    return summary

ranking = make_ranking_table(df)
ranking.to_csv(os.path.join(OUT_DIR, "algorithm_ranking.csv"), index=False)
print("\nAlgorithm Ranking:")
print(ranking)

# -----------------------------
# 7) MAZE TYCOON–STYLED FIGURES (combined overview)
# -----------------------------
def make_overview_figure(df):
    algs = sorted(df["algorithm"].unique())
    metrics = ["path_length", "visited_count", "steps"]

    means = df.groupby("algorithm")[metrics].mean().reindex(algs)

    plt.figure(figsize=(8, 5))
    x = np.arange(len(algs))
    width = 0.25

    plt.bar(x - width, means["path_length"], width, label="Avg Path Length")
    plt.bar(x, means["visited_count"], width, label="Avg Visited Nodes")
    plt.bar(x + width, means["steps"], width, label="Avg Steps")

    plt.xticks(x, algs, rotation=15)
    plt.title("Maze Tycoon Solver Performance Overview")
    plt.legend()
    plt.tight_layout()
    out = os.path.join(OUT_DIR, "maze_tycoon_overview.png")
    plt.savefig(out, dpi=220)
    plt.close()

make_overview_figure(df)

print(f"\nAll figures saved to: {OUT_DIR}")
