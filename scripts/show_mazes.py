# scripts/show_mazes.py
import sys
from pathlib import Path

# add project root to path if running from repo root
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

print(f"[bootstrap] added to sys.path: {SRC}")

from maze_tycoon.core.grid import Grid
from maze_tycoon.generation.dfs_backtracker import generate as gen_dfs
from maze_tycoon.generation.prim import generate as gen_prim
from maze_tycoon.core.vis import render_ascii

GENS  = [("dfs_backtracker", gen_dfs), ("prim", gen_prim)]
SIZES = [10, 15, 20]             # your logical n; final dims often ~ (2n+1)
TRIALS = 2                       # how many distinct mazes per (gen,size)
BASE_SEED = 12345

for gi, (gname, gfunc) in enumerate(GENS):
    for si, n in enumerate(SIZES):
        for t in range(TRIALS):
            seed = BASE_SEED + gi*10_000 + si*1_000 + t
            grid = Grid(n, n, seed=seed)
            gfunc(grid)
            mat = grid.to_matrix()
            H, W = len(mat), len(mat[0])
            print(f"\n=== {gname} | n={n} (~{H}x{W}) | seed={seed} ===")
            print(render_ascii(mat))
