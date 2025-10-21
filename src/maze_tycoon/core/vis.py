# src/maze_tycoon/core/vis.py
from __future__ import annotations
from typing import Iterable, List, Tuple, Optional, Dict

# Convert cell-space (x,y) -> matrix-space (mx,my)
def cell_to_matrix_xy(x: int, y: int) -> Tuple[int, int]:
    return 2 * x + 1, 2 * y + 1

def render_ascii(
    matrix: List[List[int]],
    *,
    path: Optional[Iterable[Tuple[int, int]]] = None,
    path_space: str = "matrix",  # "matrix" or "cell"
    start: Optional[Tuple[int, int]] = None,  # same space as `path_space` if provided
    goal: Optional[Tuple[int, int]] = None,   # same space as `path_space` if provided
    charset: Optional[Dict[str, str]] = None,
) -> str:
    """
    Render the 0/1 maze `matrix` to an ASCII string.
    - matrix: 0 = open, 1 = wall (shape: [width][height])
    - path:   sequence of coordinates (either in matrix-space or cell-space)
    - start, goal: show S and G markers
    - path_space: "matrix" if the coordinates are matrix indices, "cell" if (cell x,y)
    - charset: customize characters (defaults below)
    """
    # Defaults look nice in most terminals (including Windows).
    ch = {
        "wall": "█",
        "open": " ",
        "path": "·",
        "start": "S",
        "goal": "G",
    }
    if charset:
        ch.update(charset)

    W, H = len(matrix), len(matrix[0])  # matrix is indexed [x][y]

    # Build a character buffer we can paint onto
    buf = [[ch["wall"] if matrix[x][y] == 1 else ch["open"] for x in range(W)] for y in range(H)]

    def to_matrix_xy(p: Tuple[int, int]) -> Tuple[int, int]:
        return p if path_space == "matrix" else cell_to_matrix_xy(*p)

    # Overlay the path (if provided)
    if path:
        pts = [to_matrix_xy(p) for p in path]
        for i, (mx, my) in enumerate(pts):
            if 0 <= mx < W and 0 <= my < H:
                # endpoints will be S/G if provided; otherwise draw path
                buf[my][mx] = ch["path"]
            # also draw the "between" step if consecutive points are adjacent
            if i > 0:
                px, py = pts[i - 1]
                bx, by = (mx + px) // 2, (my + py) // 2
                if 0 <= bx < W and 0 <= by < H:
                    if buf[by][bx] != ch["start"] and buf[by][bx] != ch["goal"]:
                        buf[by][bx] = ch["path"]

    # Overlay start/goal (if provided)
    if start:
        sx, sy = to_matrix_xy(start)
        if 0 <= sx < W and 0 <= sy < H:
            buf[sy][sx] = ch["start"]
    if goal:
        gx, gy = to_matrix_xy(goal)
        if 0 <= gx < W and 0 <= gy < H:
            buf[gy][gx] = ch["goal"]

    # Join rows to a single string (iterate y first to print row-major)
    return "\n".join("".join(row) for row in buf)

def print_grid_ascii(grid, **kwargs):
    print(render_ascii(grid.to_matrix(), **kwargs))

