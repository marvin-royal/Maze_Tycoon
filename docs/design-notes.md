# Maze Tycoon — MVP Roadmap

**Author:** Marvin Royal  
**Course:** Artificial Intelligence (COMP 6600)  
**Date:** Midterm Progress Report (Updated October 2025)

---

## 🎯 Project Goal

**Maze Tycoon** is an incremental simulation game that visualizes the efficiency of AI search algorithms within procedurally generated mazes.  
The MVP milestone aims to produce a **playable prototype** where:

- Players generate mazes of varying topology  
- Observe **A\*** and other algorithms solve them in real time  
- Earn rewards based on search efficiency  
- Spend coins to upgrade heuristics and algorithmic features  

The project bridges **AI education** and **game design**, transforming pathfinding optimization into an interactive, experiment-driven experience.

---

## 🧩 Development Roadmap (Week-by-Week Plan)

| Week | Focus | Objectives | Deliverables |
|:----:|:------|:------------|:--------------|
| **1** | **Core Systems Finalization** | – Refine `Grid` and `Cell` classes<br>– Add deterministic seeding and RNG controls<br>– Implement serialization for saving/loading mazes | Working grid module; reproducible generation |
| **2** | **Algorithm Integration** | – Implement BFS, Dijkstra, and A* (Manhattan & Euclidean)<br>– Establish metrics tracking (node expansions, runtime, path length)<br>– Validate correctness via `tests/test_search_optimality.py` | Verified pathfinding across generated mazes |
| **3** | **Game Mechanics** | – Implement economy and upgrade systems<br>– Create reward functions tied to search efficiency<br>– Define player progression model | Functional reward and upgrade loop |
| **4** | **Visualization Layer** | – Implement basic Pygame loop (`game/app.py`)<br>– Draw maze grids and animate pathfinding<br>– Integrate color palette and UI components (start/pause, heuristic select) | Playable simulation of algorithmic search |
| **5** | **Evaluation & Analytics** | – Integrate runtime logging and metrics<br>– Produce comparative plots of A*, BFS, Dijkstra performance<br>– Generate figures for report (`metrics/plotting.py`) | Figures + early performance analysis |
| **6** | **Refinement & Documentation** | – Balance gameplay economy<br>– Finalize README, docstrings, and code organization<br>– Prepare midterm report and presentation | MVP demo + full documentation |

---

## ✅ Completed to Date

- Implemented **Grid** and **Cell** core classes  
- Added **DFS Backtracker** and **Prim’s Algorithm** for procedural maze generation  
- Verified **matrix translation** logic and correctness of connectivity  
- Developed **experiment runner (`scripts/run_experiment.py`)** with YAML config support  
- Implemented **ASCII renderer (`core/vis.py`)** for readable maze visualization in console  
- Integrated **CLI flags** for real-time ASCII printing and reproducible experiment output  
- Established **deterministic RNG seeding** for experiment reproducibility  
- Configured **project structure** (`src/` layout), **GitHub workspace**, and **virtual environment**

---

## 🔧 Next Immediate Tasks

1. Integrate **A\*** and baseline algorithms (BFS, Dijkstra) into experiment runner  
2. Connect the **metrics** module to record node expansions, runtime, and path length  
3. Expand YAML experiment schema for heuristic selection and maze variety  
4. Implement **economy loop** (coin cost per node, reward per solution)  
5. Add **Pygame visualization layer** for interactive maze solving and progress display  
6. Finalize **unit tests** for reproducibility and performance validation  

---

## 🧠 Testing & Visualization Framework

Maze Tycoon now includes a repeatable experiment system:

- **Config-Driven Execution** — YAML files in `config/experiments/` define parameters like maze size, algorithm, and trials.  
- **State Reset** — Each trial resets RNG seed, grid state, and logs to guarantee reproducibility.  
- **Logging** — Results are saved as timestamped CSVs in `data/results/`.  
- **Visualization** — The `render_ascii()` utility provides clear console output for visual debugging and qualitative analysis.  

Example command:
```bash
python scripts/run_experiment.py --config config/experiments/size_sweep.yaml --ascii

📈 Long-Term Goals (Post-MVP)

Integrate Bidirectional A* and heuristic upgrades into gameplay loop

Add reinforcement learning agent to adapt heuristic choice based on prior performance

Extend to 3D maze generation and multi-floor pathfinding

Build an analytics dashboard with real-time graphs of node expansions and runtime

Package Maze Tycoon as an interactive AI education toolkit

🗂 Directory Highlights
src/
└── maze_tycoon/
    ├── core/
    │   ├── grid.py          # Maze and cell data structures
    │   ├── vis.py           # ASCII rendering for debugging and analysis
    │   └── __init__.py
    ├── generation/
    │   ├── dfs_backtracker.py
    │   ├── prim.py
    │   └── __init__.py
    ├── algorithms/          # BFS, A*, Dijkstra implementations (in progress)
    ├── game/                # Pygame visualization and UI
    └── metrics/             # Logging and analytics utilities

🧾 Summary

Maze Tycoon has established the foundation for reproducible AI experimentation through procedural maze generation, deterministic seeding, and visualization tools.
The next milestone will transition from infrastructure to algorithmic integration and visual gameplay, demonstrating how heuristic design impacts efficiency, cost, and player progression.