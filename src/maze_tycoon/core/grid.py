"""
grid.py
Core grid and cell structures for Maze Tycoon.
Handles maze representation, coordinate utilities, and basic operations.
"""

from __future__ import annotations
import random
from typing import List, Tuple, Optional, Dict


class Cell:
    """Represents a single cell in the maze grid."""

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        # Walls initially exist in all directions (for maze generation)
        self.walls: Dict[str, bool] = {
            "N": True,
            "S": True,
            "E": True,
            "W": True
        }
        self.visited: bool = False
        self.cost: float = 1.0  # cost to traverse (can be extended later)

    def neighbors_coords(self, grid_size: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Returns valid neighbor coordinates (not considering walls)."""
        max_x, max_y = grid_size
        candidates = [
            (self.x, self.y - 1),  # N
            (self.x, self.y + 1),  # S
            (self.x + 1, self.y),  # E
            (self.x - 1, self.y)   # W
        ]
        return [
            (x, y)
            for x, y in candidates
            if 0 <= x < max_x and 0 <= y < max_y
        ]

    def remove_wall_between(self, other: Cell) -> None:
        """Removes the wall between this cell and another cell (bidirectional)."""
        dx = other.x - self.x
        dy = other.y - self.y

        if dx == 1:   # other is East
            self.walls["E"] = False
            other.walls["W"] = False
        elif dx == -1:  # other is West
            self.walls["W"] = False
            other.walls["E"] = False
        elif dy == 1:   # other is South
            self.walls["S"] = False
            other.walls["N"] = False
        elif dy == -1:  # other is North    # pragma: no cover
            self.walls["N"] = False
            other.walls["S"] = False

    def __repr__(self):
        return f"Cell({self.x}, {self.y}, visited={self.visited})"


class Grid:
    """2D grid structure for maze generation and search."""

    def __init__(self, width: int, height: int, seed: Optional[int] = None):
        self.width = width
        self.height = height
        self.rng = random.Random(seed)
        self.grid: List[List[Cell]] = [
            [Cell(x, y) for y in range(height)]
            for x in range(width)
        ]

    def cell_at(self, x: int, y: int) -> Cell:
        """Returns the cell at given coordinates."""
        return self.grid[x][y]

    def random_cell(self) -> Cell:
        """Returns a random cell from the grid."""
        return self.cell_at(
            self.rng.randrange(self.width),
            self.rng.randrange(self.height)
        )

    def neighbors(self, cell: Cell) -> List[Cell]:
        """Returns all valid neighboring cells (without wall checks)."""
        return [
            self.cell_at(nx, ny)
            for nx, ny in cell.neighbors_coords((self.width, self.height))
        ]

    def unvisited_neighbors(self, cell: Cell) -> List[Cell]:
        """Returns unvisited neighboring cells."""
        return [n for n in self.neighbors(cell) if not n.visited]

    def reset_visits(self) -> None:
        """Marks all cells as unvisited."""
        for col in self.grid:
            for cell in col:
                cell.visited = False

    def to_matrix(self) -> List[List[int]]:
        """
        Converts maze into a 2D matrix representation.
        1 = wall, 0 = open path.
        Used by pathfinding algorithms.
        """
        mat_w, mat_h = self.width * 2 + 1, self.height * 2 + 1
        matrix = [[1 for _ in range(mat_h)] for _ in range(mat_w)]

        for x in range(self.width):
            for y in range(self.height):
                cx, cy = 2 * x + 1, 2 * y + 1
                matrix[cx][cy] = 0
                cell = self.cell_at(x, y)
                if not cell.walls["N"]:
                    matrix[cx][cy - 1] = 0
                if not cell.walls["S"]:
                    matrix[cx][cy + 1] = 0
                if not cell.walls["E"]:
                    matrix[cx + 1][cy] = 0
                if not cell.walls["W"]:
                    matrix[cx - 1][cy] = 0
        return matrix

    def __repr__(self):
        return f"Grid({self.width}x{self.height})"
