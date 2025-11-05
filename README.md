Notes to self - Relevant Commands

🧩 Project Setup / Imports
# 1️⃣  Set Python path so the src/ folder is visible to imports
$env:PYTHONPATH = "src"

# 2️⃣  Test that imports work
python -c "import maze_tycoon, sys; print('OK:', maze_tycoon.__file__)"

🧱 Running Maze Generators
# 3️⃣  Run the ASCII maze visualizer
python scripts\show_mazes.py

# 4️⃣  (Optional) run as module if you prefer
python -m scripts.show_mazes

🧠 Running Experiments (CSV + Pathfinding)
# 5️⃣  BFS baseline run with ASCII output for first maze of each size
python scripts\run_experiment.py -c configs\bfs.yml --ascii

# 6️⃣  A* Manhattan heuristic (4-connected)
python scripts\run_experiment.py -c configs\astar_manhattan.yml

# 7️⃣  A* Octile heuristic (8-connected)
python scripts\run_experiment.py -c configs\astar_octile.yml

📦 Check Algorithm Modules Exist
# 8️⃣  Confirm that bfs and a_star modules load and have solve()
$env:PYTHONPATH = "src"
python -c "import importlib; print('bfs:', hasattr(importlib.import_module('maze_tycoon.algorithms.bfs'),'solve')); print('a_star:', hasattr(importlib.import_module('maze_tycoon.algorithms.a_star'),'solve'))"

🧮 Aggregate Results (Heuristic Scaling Summary)
# 9️⃣  Quick summary table across all CSVs
$env:PYTHONPATH="src"
python - << 'PY'
import glob, csv, statistics as st
rows=[]
for fp in glob.glob("outputs/*.csv"):
    with open(fp, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            r['width']=int(r['width']); r['height']=int(r['height'])
            r['node_expansions']=int(float(r['node_expansions']))
            r['runtime_ms']=float(r['runtime_ms'])
            r['path_length']=int(float(r['path_length']))
            rows.append(r)

from collections import defaultdict
g=defaultdict(list)
for r in rows:
    key=(r['generator'], f"{r['width']}x{r['height']}", r['algorithm'], r['heuristic'] or "-")
    g[key].append(r)

print("generator,size,algorithm,heuristic,avg_expansions,avg_runtime_ms,avg_path_len,n")
for k, grp in sorted(g.items()):
    ae=st.mean(r['node_expansions'] for r in grp)
    ar=st.mean(r['runtime_ms'] for r in grp)
    ap=st.mean(r['path_length'] for r in grp)
    print(",".join(map(str, [*k, int(ae), f'{ar:.2f}', int(ap), len(grp)])))
PY

🔍 Debugging Imports or Seeds
# 10️⃣  Find any hardcoded random seeds (e.g., "random.Random(42)")
findstr /S /N /I "random.Random(" src\maze_tycoon\generation\*.py
findstr /S /N /I "np.random.seed" src\maze_tycoon\generation\*.py

🗂️ Confirm File Structure (Top 3 Levels)
# 11️⃣  Show layout to verify src and scripts folders
tree -a -L 3

🧼 Reset / Re-run Environment
# 12️⃣  Clear and recreate outputs folder if needed
Remove-Item outputs -Recurse -Force
mkdir outputs
