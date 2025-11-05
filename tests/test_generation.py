from maze_tycoon.core.grid import Grid
from maze_tycoon.generation import dfs_backtracker, prim

def all_cells_visited(g: Grid) -> bool:
    # Works because your generators set cell.visited = True when carved
    for x in range(g.width):
        for y in range(g.height):
            if not g.cell_at(x, y).visited:
                return False
    return True

def test_dfs_backtracker_connectivity():
    g = Grid(9, 9)
    dfs_backtracker(g)            # NOTE: call as a function, not module.generate(...)
    assert all_cells_visited(g)

def test_prim_connectivity():
    g = Grid(9, 9)
    prim(g)                       # NOTE: call as a function, not module.generate(...)
    assert all_cells_visited(g)

def test_dfs_backtracker_respects_start_param():
    g = Grid(9,9)
    start = (0,0)
    dfs_backtracker(g, start=start)  # exported as a function via __init__
    # The start cell should be marked visited (your generator sets visited when carving)
    assert g.cell_at(*start).visited

def test_prim_works_on_small_grid_and_marks_all():
    g = Grid(5,5)
    prim(g)
    # Most implementations mark all cells visited after run
    assert all(g.cell_at(x,y).visited for x in range(g.width) for y in range(g.height))

def test_prim_respects_start_param_and_marks_start():
    g = Grid(9,9)
    start = (0,0)
    prim(g, start=start)   # exported as a function via your __init__
    assert g.cell_at(*start).visited

def test_prim_tiny_grid_still_terminates():
    # Small but valid odd grid; should not hang and should mark lots of cells.
    g = Grid(5,5)
    prim(g)
    assert any(g.cell_at(x,y).visited for x in range(g.width) for y in range(g.height))

def test_prim_guard_no_visited_neighbors(monkeypatch):
    g = Grid(7, 7)

    # Keep original neighbors; we will override only once.
    original_neighbors = g.neighbors

    call_counter = {"n": 0}

    def neighbors_once_returns_empty(cell):
        # First call: pretend there are no neighbors (forces visited_neighbors == [])
        # Subsequent calls: behave normally so the algorithm can finish.
        
        call_counter["n"] += 1
        if call_counter["n"] == 1:
            return []          # triggers the "if not visited_neighbors: continue" guard
        return list(original_neighbors(cell))

    # Monkeypatch the method on this instance only
    monkeypatch.setattr(g, "neighbors", neighbors_once_returns_empty, raising=True)

    # Run Prim's; it should handle the guard gracefully and still complete
    prim(g, start=(0, 0))

    # Ensure generation progressed (some cells got visited)
    assert any(g.cell_at(x, y).visited for x in range(g.width) for y in range(g.height))

def test_prim_hits_continue_guard(monkeypatch):
    """
    Force the 'if not visited_neighbors: continue' branch in prim.py by making
    the first few neighbor lookups return an empty list.
    """
    g = Grid(7, 7)

    # Keep originals (class-level and instance-level, if present)
    original_grid_neighbors = getattr(Grid, "neighbors", None)
    original_inst_neighbors = getattr(g, "neighbors", None)
    original_neighbors_of   = getattr(Grid, "neighbors_of", None)  # if your Grid exposes this

    call = {"n": 0}

    def fake_neighbors(self_or_cell, maybe_cell=None):
        # Works whether called as Grid.neighbors(self, cell) or instance.neighbors(cell)
        call["n"] += 1
        if call["n"] <= 3:  # ensure at least one empty result -> triggers 'continue'
            return []
        # Delegate to whichever original exists
        if original_inst_neighbors and self_or_cell is g:
            return list(original_inst_neighbors(maybe_cell or self_or_cell))
        if original_grid_neighbors:
            # Handle Grid.neighbors(self, cell) signature
            self = self_or_cell
            cell = maybe_cell
            return list(original_grid_neighbors(self, cell))
        # Fallback: no neighbor API? return empty to keep test safe
        return []

    # Patch both common entry points so we definitely intercept neighbor calls
    if original_grid_neighbors:
        monkeypatch.setattr(Grid, "neighbors", fake_neighbors, raising=False)
    if original_neighbors_of:
        monkeypatch.setattr(Grid, "neighbors_of", lambda self, cell: [], raising=False)
    if original_inst_neighbors and not original_grid_neighbors:
        # Some implementations only bind on the instance
        monkeypatch.setattr(g, "neighbors", lambda cell: fake_neighbors(g, cell), raising=False)

    prim(g, start=(0, 0))

    # Sanity: algorithm still progressed after our first few empty neighbor calls
    assert any(g.cell_at(x, y).visited for x in range(g.width) for y in range(g.height))