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

### **Algorithms**
- ✅ **BFS** implemented (`algorithms/bfs.py`)  
- ✅ **A\*** implemented with heuristic interface (`algorithms/a_star.py`)  
- ✅ **Heuristics**: Manhattan, Euclidean, and Octile completed (`heuristics/*.py`)

### **Maze Generation**
- ✅ **DFS Backtracker** implemented (`generation/dfs_backtracker.py`)  
- ✅ **Prim’s Algorithm** implemented (`generation/prim.py`)

### **Core Systems**
- ✅ **Grid / Cell architecture** completed (`core/grid.py`)  
- ✅ **ASCII Renderer** implemented (`core/vis.py`)  
- ✅ **YAML Config Loader** implemented (`io/config_loader.py`)

### **Structure**
- ✅ Clean modular package: `algorithms/`, `core/`, `generation/`, `heuristics/`, `game/`, `io/`, `metrics/`

---

## ⏳ In Progress / Not Yet Implemented

| Module | Status | Description |
|:--------|:-------:|:------------|
| `algorithms/dijkstra.py` | ⛔ | Empty — needs priority queue and distance tracking |
| `algorithms/bidirectional_a_star.py` | ⛔ | Empty — needs dual-frontier meeting logic |
| `algorithms/interfaces.py` | ⚠️ | Present, incomplete — standardize solver interface |
| `core/maze.py` | ⛔ | Empty — should handle grid setup, start/goal placement |
| `core/rng.py` | ⛔ | Empty — deterministic RNG utilities missing |
| `core/metrics.py` | ⛔ | Empty — needs dataclass + runtime tracking |
| `game/app.py` | ⛔ | Empty — implement main Pygame loop |
| `game/ui_pygame.py` | ⛔ | Empty — implement UI controls (start/pause, dropdowns) |
| `game/economy.py` | ⛔ | Empty — design coin/upgrade economy |
| `game/pallete.py` | ⚠️ | Empty & misspelled — should be `palette.py` |
| `io/logging.py` | ⛔ | Empty — build CSV / console logging system |
| `io/serialize.py` | ⛔ | Empty — add save/load for maze and results |
| `metrics/aggregations.py` | ⛔ | Empty — build CSV aggregation functions |
| `metrics/plotting.py` | ⛔ | Empty — implement runtime / expansion graphs |

**Missing project files:**
- `README.md`
- `requirements.txt`
- `scripts/run_experiment.py`
- `tests/` directory for algorithm verification

---

## 🔧 Next Immediate Tasks

1. **Complete Algorithm Set**
   - Implement Dijkstra and Bidirectional A\*
   - Finalize interface to unify solver APIs for visualization

2. **Maze & RNG Integration**
   - Build `core/maze.py` to combine generation, seeding, and solver launching
   - Add seeded random generator via `core/rng.py`

3. **Metrics & Experiment Logging**
   - Add `core/metrics.py` dataclass (`nodes_expanded`, `runtime`, `path_length`)
   - Write CSV logger (`io/logging.py`) and serializer (`io/serialize.py`)

4. **Visualization Layer**
   - Implement `game/app.py` for Pygame-based display
   - Add controls (`ui_pygame.py`) and color palette

5. **Economy System**
   - Implement upgrade loop: cost per node, reward per efficiency
   - Add persistence of coins across runs

6. **Analytics & Documentation**
   - Fill `metrics/plotting.py` and `metrics/aggregations.py`
   - Add plots comparing A*, BFS, Dijkstra
   - Write README and setup instructions

---

## 🧠 Testing & Visualization Framework

The project scaffolding supports **reproducible experiments**:

- **Config-Driven Execution** via `io/config_loader.py`
- **Deterministic Seeding** (pending `core/rng.py`)
- **Metrics Logging** (pending `core/metrics.py` + `io/logging.py`)
- **Visualization** already functional in console via `core/vis.py`; next step is real-time rendering in Pygame

**Example (target) command:**
```bash
python scripts/run_experiment.py --config config/experiments/size_sweep.yaml --ascii
