📘 Maze Tycoon — README
🧩 Overview

Maze Tycoon is an interactive and experimental framework for exploring classical search algorithms inside procedurally generated mazes.
It combines:

Maze generation (DFS Backtracking, Prim’s Algorithm)

Classical pathfinding algorithms (BFS, Dijkstra, A*, Bidirectional A*)

Real-time visualization using pygame

Deterministic experiment pipeline for collecting solver metrics

Batch-mode evaluation for research, benchmarking, and plotting

A persistent tycoon-style progression system

Maze Tycoon supports both interactive gameplay and headless batch experiments, making it useful for education, AI demonstrations, and algorithmic analysis.

📦 Installation
1. Clone the repository
git clone <your-repo-url>
cd Maze_Tycoon

2. Install dependencies

Python 3.9+ recommended.

pip install -r requirements.txt


Dependencies include:

pygame

numpy

pandas

matplotlib

seaborn (optional for extra visuals)

🚀 Running Maze Tycoon

Maze Tycoon supports two main execution modes:

🎮 1. Interactive Gameplay Mode

This mode launches the full UI with menus, algorithm selection, solver animation, and summary screens.

Run:

python -m maze_tycoon.game.app --mode interactive


You will see:

Main Menu

Start / Continue / Load / Quit

Maze Generation Selection

DFS Backtracking

Prim’s Algorithm

Algorithm Selection

BFS, Dijkstra, A*, Bidirectional A*

Real-Time Visualization

Post-Run Summary Screen

Path length

Steps

Visited nodes

Credits earned

All progress persists automatically inside the GameState.

📊 2. Batch Experiment Mode (Headless)

This mode runs many trials automatically and logs results to .jsonl for analysis.

Basic example:
python -m maze_tycoon.game.app --mode batch --alg bfs --gen dfs_backtracker --width 31 --height 31 --trials 50

Common parameters
Flag	Meaning
--mode batch	Enables headless batch mode
--alg	Solver algorithm (bfs, dijkstra, a_star, bidirectional_a_star)
--gen	Maze generator (dfs_backtracker, prim)
--width, --height	Maze dimensions
--trials	Number of trials to run
--heuristic	For A*: manhattan, euclidean, octile
--out	Output file override (optional)
Sample commands (recommended)
A Euclidean, DFS Backtracking*
python -m maze_tycoon.game.app --mode batch \
    --alg a_star --heuristic euclidean \
    --gen dfs_backtracker \
    --width 31 --height 31 \
    --trials 50

Bidirectional A Manhattan, Prim*
python -m maze_tycoon.game.app --mode batch \
    --alg bidirectional_a_star --heuristic manhattan \
    --gen prim \
    --width 31 --height 31 \
    --trials 50


Results export to:

results/results_<alg>_<heuristic>_<gen>_<HxW>_t<trials>.jsonl

📑 Metrics & Output Files

Every trial logs:

path_length

visited_nodes (full set)

node_expansions

runtime_ms

start/goal positions

path (list of grid coordinates)

visited_order (for heatmaps)

metadata (seed, algorithm, generator, maze size)

Stored in .jsonl for streaming large datasets.

📈 Plotting & Analysis

Inside maze_tycoon/metrics/plotting.py, you will find utilities for:

Path length distributions

Visited-node comparisons

Step-count comparisons

Solver heatmaps

Algorithm ranking tables

Maze Tycoon–styled visual figures

To use them:

python -m maze_tycoon.metrics.plotting


Or call individual functions inside the script after configuring:

RESULTS_DIR = "/path/to/results"
OUT_DIR = "/path/to/output/plots"


Generated outputs include .png images placed inside OUT_DIR.

🏗 Project Structure
maze_tycoon/
│
├── algorithms/          # BFS, Dijkstra, A*, Bidirectional A*
├── generation/          # DFS Backtracking + Prim generators
├── heuristics/          # Heuristic functions
├── game/
│    ├── app.py          # Main entry point (interactive + batch)
│    ├── ui_pygame.py    # Visualization / rendering
│    ├── ui_adapter.py   # Data <-> UI interface
│    ├── state.py        # GameState persistence + economy
│    └── engine.py       # Simulation engine & run pipelines
│
├── metrics/
│    ├── plotting.py     # Graphs / heatmaps / summaries
│    └── tables.py       # Rankings + CSV utilities
│
├── io/                  # JSONL/CSV serialization tools
└── results/             # Auto-generated experiment logs

🧪 Reproducibility

Maze Tycoon uses a custom deterministic RNG system:

Every maze, solver, and experiment can be reproduced exactly.

Seeds are stored in each trial’s output record.

🛠 Future Extensions

Ideas already supported by the architecture:

New maze generators (Kruskal, Eller, Wilson’s)

Additional solvers (IDA*, Jump Point Search)

RL-based agents

Upgrade systems / tycoon mechanics

Difficulty scaling across game days

📄 License

(Add your chosen license here — MIT is typical for student projects.)

🎉 Acknowledgments

Maze Tycoon was created as part of a final project for COMP 56600 / 600 — Artificial Intelligence.
