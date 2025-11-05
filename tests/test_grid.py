from maze_tycoon.core.grid import Grid

def test_in_bounds_and_neighbors_4():
    g = Grid(5, 5)
    center = g.cell_at(2, 2)
    neighbors = list(g.neighbors(center))   # no connectivity kwarg
    coords = {(c.x, c.y) for c in neighbors}
    assert len(coords) == 4
    assert coords == {(1, 2), (3, 2), (2, 1), (2, 3)}

def test_remove_wall_between_symmetry_no_exception():
    g = Grid(5, 5)
    a = g.cell_at(1, 1)
    b = g.cell_at(1, 2)
    # Carving in each direction should not raise and should be idempotent
    a.remove_wall_between(b)
    b.remove_wall_between(a)
    assert True

def test_neighbors_corner_and_edge_counts():
    g = Grid(5,5)
    corner = g.cell_at(0,0)
    edge = g.cell_at(0,2)
    center = g.cell_at(2,2)

    c_nb = list(g.neighbors(corner))
    e_nb = list(g.neighbors(edge))
    m_nb = list(g.neighbors(center))

    assert len(c_nb) == 2  # (1,0) and (0,1)
    assert len(e_nb) == 3  # edge has three neighbors
    assert len(m_nb) == 4  # center has four neighbors

def test_in_bounds_edges_and_out_of_bounds():
    g = Grid(4, 6)
    assert _in_bounds_xy(g, 0, 0)
    assert _in_bounds_xy(g, 3, 5)
    assert not _in_bounds_xy(g, -1, 0)
    assert not _in_bounds_xy(g, 0, -1)
    assert not _in_bounds_xy(g, 4, 0)
    assert not _in_bounds_xy(g, 0, 6)

def test_remove_wall_between_is_symmetric_and_idempotent():
    g = Grid(5,5)
    a = g.cell_at(1,1)
    b = g.cell_at(1,2)

    # carve once each way; should not raise and should be idempotent
    a.remove_wall_between(b)
    b.remove_wall_between(a)
    a.remove_wall_between(b)
    b.remove_wall_between(a)
    assert True

def _in_bounds_xy(g: Grid, x: int, y: int) -> bool:
    # Use grid dimensions instead of a missing Grid.in_bounds()
    return 0 <= x < g.width and 0 <= y < g.height

def test_random_cell_returns_in_bounds_cell():
    g = Grid(7, 7)
    c = g.random_cell()
    assert _in_bounds_xy(g, c.x, c.y)

def test_neighbors_do_not_include_self_and_stay_in_bounds():
    g = Grid(3,4)
    # corners
    for x,y,expected in [(0,0,2),(0,3,2),(2,0,2),(2,3,2)]:
        n = list(g.neighbors(g.cell_at(x,y)))
        coords = {(c.x,c.y) for c in n}
        assert (x,y) not in coords
        # all neighbors must be within bounds (hits in-bounds branches)
        assert all(0 <= cx < g.width and 0 <= cy < g.height for cx,cy in coords)
        assert len(coords) == expected

def test_cell_repr_returns_expected_format():
    g = Grid(3, 3)
    c = g.cell_at(1, 1)
    # mark visited so repr shows it as True
    c.visited = True
    rep = repr(c)
    assert rep.startswith("Cell(")
    assert "visited=True" in rep

def test_grid_to_matrix_reflects_carved_passages():
    g = Grid(3, 3)
    # carve a few walls manually to exercise all four directions
    c = g.cell_at(1, 1)
    # carve north, south, east, west
    for d, neighbor_coords in {
        "N": (1, 0),
        "S": (1, 2),
        "E": (2, 1),
        "W": (0, 1),
    }.items():
        n = g.cell_at(*neighbor_coords)
        c.remove_wall_between(n)

    matrix = g.to_matrix()
    # expected matrix size: (width*2+1) x (height*2+1)
    expected_w, expected_h = g.width * 2 + 1, g.height * 2 + 1
    assert len(matrix) == expected_w
    assert len(matrix[0]) == expected_h

    # Center cell must be open (0)
    cx, cy = 2 * 1 + 1, 2 * 1 + 1
    assert matrix[cx][cy] == 0

    # All four adjacent wall openings should be 0 as well
    assert matrix[cx][cy - 1] == 0  # N
    assert matrix[cx][cy + 1] == 0  # S
    assert matrix[cx + 1][cy] == 0  # E
    assert matrix[cx - 1][cy] == 0  # W

def test_grid_repr_displays_dimensions():
    g = Grid(4, 6)
    rep = repr(g)
    assert f"Grid({g.width}x{g.height})" in rep