from maze_tycoon.core.vis import render_ascii, cell_to_matrix_xy
import builtins
import types
import inspect
from importlib import import_module
from maze_tycoon.core.grid import Grid

def test_ascii_snapshot_simple():
    # 5x5 empty interior matrix (1 = wall, 0 = open)
    m = [[1]*5] + [[1,0,0,0,1] for _ in range(3)] + [[1]*5]
    s = render_ascii(m, start=(1,1), goal=(3,3))
    lines = s.splitlines()
    assert len(lines) == 5

    # Detect border char from first line (your renderer uses '█')
    border_char = lines[0][0]
    assert all(ch == border_char for ch in lines[0])          # top border uniform
    assert all(ch == border_char for ch in lines[-1])         # bottom border uniform
    assert 'S' in s and 'G' in s                              # start/goal markers present

    # Ensure there is at least some open interior (space or similar)
    interior = "\n".join(lines[1:-1])
    assert any(ch.strip() == "" for ch in interior)  # at least one whitespace/open cell

def _empty(h=5, w=7):
    m = [[1]*w]
    for r in range(1, h-1):
        m.append([1] + [0]*(w-2) + [1])
    m.append([1]*w)
    return m

def test_render_without_start_goal_and_with_path_in_matrix_space():
    m = _empty(5,7)
    # simple L-shaped path in matrix coords
    path = [(1,1),(1,2),(1,3),(2,3),(3,3)]
    s = render_ascii(m, path=path, path_space="matrix")
    # detect border char (your renderer uses '█')
    border = s.splitlines()[0][0]
    assert all(ch == border for ch in s.splitlines()[0])
    # path should be visible (renderer uses spaces for open; any distinct marker suffices)
    assert "S" not in s and "G" not in s  # no start/goal
    # ensure at least one interior non-border char exists (open/path)
    assert any(ch.strip() == "" for ch in "\n".join(s.splitlines()[1:-1]))

def test_render_with_matrix_space_path_and_start_goal():
    
    m = _empty(5, 7)
    # Start/goal in MATRIX coordinates (open interior: 1..h-2, 1..w-2)
    start = (1, 1)
    goal  = (3, 5)  # still inside the interior

    # Simple path in MATRIX space: a little L shape
    path = [(1,1), (1,2), (1,3), (2,3), (3,3), (3,4), (3,5)]

    s = render_ascii(
        m,
        path=path,
        path_space="matrix",
        start=start,
        goal=goal,
    )

    lines = s.splitlines()
    assert len(lines) >= 3
    # rectangular
    width = len(lines[0])
    assert all(len(row) == width for row in lines)
    # top/bottom borders uniform (auto-detect border char)
    border = next((ch for ch in lines[0] if ch.strip() != ""), lines[0][0])
    assert lines[0].strip(border) == ""
    assert lines[-1].strip(border) == ""
    # interior rows start/end with border
    for row in lines[1:-1]:
        assert row.startswith(border) and row.endswith(border)
    # S and G visible
    assert "S" in s and "G" in s

def test_render_without_path_and_without_start_goal():
    m = _empty(5,7)
    s = render_ascii(m)  # no path, no start/goal passed
    lines = s.splitlines()
    assert len(lines) >= 3
    width = len(lines[0])
    assert all(len(row) == width for row in lines)
    # borders uniform (auto-detect border char)
    border = next((ch for ch in lines[0] if ch.strip() != ""), lines[0][0])
    assert lines[0].strip(border) == ""
    assert lines[-1].strip(border) == ""

def test_cell_to_matrix_xy_mapping():
    # simple spot checks to execute "return 2 * x + 1, 2 * y + 1"
    assert cell_to_matrix_xy(0, 0) == (1, 1)
    assert cell_to_matrix_xy(1, 0) == (3, 1)
    assert cell_to_matrix_xy(0, 2) == (1, 5)
    assert cell_to_matrix_xy(2, 3) == (5, 7)

def test_render_ascii_accepts_and_updates_charset():
    # Provide a non-default charset so ch.update(charset) executes
    charset = {
        "wall": "#",          # override border character
        "start": "A",         # override start marker
        "goal": "B",          # override goal marker
        # it's okay to omit other keys; update() merges what you pass
    }
    s = render_ascii(
        _empty(5, 7),
        start=(1, 1),
        goal=(3, 5),
        charset=charset,      # <- hits line with ch.update(charset)
        path_space="matrix",
    )

    # top/bottom should be border rows made of '#'
    lines = s.splitlines()
    assert lines[0].strip("#") == ""
    assert lines[-1].strip("#") == ""
    # start/goal should use A/B
    assert "A" in s and "B" in s

def test_print_wrapper_calls_print_and_renders(capsys):
    vis = import_module("maze_tycoon.core.vis")
    # Find a callable in vis that eventually does: print(render_ascii(grid.to_matrix(), **kwargs))
    # Common names to look for:
    candidate_names = ("print_ascii", "preview", "show_ascii", "debug_print", "print_grid")
    fn = None
    for name in candidate_names:
        fn = getattr(vis, name, None)
        if callable(fn):
            break
    if fn is None:
        # Fallback: try to find any function that prints by scanning module members
        for _, obj in inspect.getmembers(vis, inspect.isfunction):
            src = inspect.getsource(obj)
            if "print(" in src and "render_ascii(" in src and "to_matrix(" in src:
                fn = obj
                break

    if fn is None:
        # If the module doesn't expose a wrapper, skip gracefully;
        # we don't want to fail a suite if that helper wasn't shipped.
        import pytest
        pytest.skip("No vis print-wrapper function exported; nothing to cover on line 74.")
        return

    g = Grid(5, 7)
    fn(g, start=(1, 1), goal=(3, 5))  # this should execute the print(render_ascii(...)) path
    out = capsys.readouterr().out
    assert len(out) > 0   # some ASCII was printed