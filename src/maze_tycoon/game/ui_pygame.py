"""
pygame-based visualisation for Maze Tycoon.

This module provides a small, self-contained viewer that can render a stream
of MazeFrame objects. It is intentionally decoupled from the rest of the game
logic so that you can reuse it with different maze / solver implementations.

Typical use:

    from game.ui_pygame import MazeFrame, run_maze_view

    frames = (MazeFrame.from_bool_grid(grid, player_pos=player, ...) for ...)
    run_maze_view(frames, fps=30)

Close the window or press ESC to exit.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Collection, Iterable, Optional, Sequence, Tuple, TYPE_CHECKING

from .palette import color

# pygame is an optional dependency; we import lazily to keep tests happy.
try:  # pragma: no cover - import guard
    import pygame  # type: ignore
except ImportError:  # pragma: no cover - handled at runtime
    pygame = None  # type: ignore

if TYPE_CHECKING:
    import pygame as _pygame
    Surface = _pygame.Surface
    Font = _pygame.font.Font
else:
    Surface = Any
    Font = Any

GridLike = Sequence[Sequence[int]]
Pos = Tuple[int, int]


@dataclass
class MazeFrame:
    """
    A snapshot of the maze at a single point in time.

    grid:
        2D array-like [row][col]. Convention: 0 = floor, 1 = wall.
        This mirrors common ASCII representations and keeps the viewer simple.
    player:
        (row, col) of the player/agent, if any.
    entrance / exit:
        (row, col) positions for visual markers, if desired.
    solution_path:
        Cells that belong to the "best" path (e.g., solver result).
    visited:
        Cells visited by the solver/agent so far.
    step_index:
        Optional step counter for display in the HUD.
    note:
        Optional short message for the HUD (e.g., solver state).
    """

    grid: GridLike
    player: Optional[Pos] = None
    entrance: Optional[Pos] = None
    exit: Optional[Pos] = None
    solution_path: Optional[Collection[Pos]] = None
    visited: Optional[Collection[Pos]] = None
    step_index: Optional[int] = None
    note: str | None = None

    @property
    def rows(self) -> int:
        return len(self.grid)

    @property
    def cols(self) -> int:
        return len(self.grid[0]) if self.grid else 0

    @classmethod
    def from_bool_grid(
        cls,
        grid: Sequence[Sequence[bool]],
        *,
        player: Optional[Pos] = None,
        entrance: Optional[Pos] = None,
        exit: Optional[Pos] = None,
        solution_path: Optional[Collection[Pos]] = None,
        visited: Optional[Collection[Pos]] = None,
        step_index: Optional[int] = None,
        note: str | None = None,
    ) -> "MazeFrame":
        """
        Convenience constructor if your maze uses a bool grid
        (True = wall, False = floor).
        """
        int_grid: list[list[int]] = [
            [1 if cell else 0 for cell in row] for row in grid
        ]
        return cls(
            grid=int_grid,
            player=player,
            entrance=entrance,
            exit=exit,
            solution_path=solution_path,
            visited=visited,
            step_index=step_index,
            note=note,
        )


# --------------------------------------------------------------------------- #
# Core viewer
# --------------------------------------------------------------------------- #


def _ensure_pygame() -> None:
    if pygame is None:  # pragma: no cover - runtime guard
        raise RuntimeError(
            "pygame is required for the Maze Tycoon UI.\n"
            "Install it with: pip install pygame"
        )


def run_maze_view(
    frames: Iterable[MazeFrame],
    *,
    fps: int = 20,
    cell_size: int = 24,
    hud_height: int = 48,
    window_title: str = "Maze Tycoon",
    hud_callback=None,
) -> None:
    """
    Render a sequence of MazeFrame objects using pygame.

    - `frames` may be a finite or infinite iterable.
    - Once frames are exhausted, the last frame remains on screen until the
      user closes the window or presses ESC.

    This function blocks until the window is closed.
    """
    _ensure_pygame()

    frame_iter = iter(frames)
    try:
        current = next(frame_iter)
    except StopIteration:
        # Nothing to show; silently return.
        return

    pygame.init()
    try:
        width = current.cols * cell_size
        height = current.rows * cell_size + hud_height

        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(window_title)

        font = pygame.font.SysFont(None, 18)
        clock = pygame.time.Clock()

        running = True
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            # Draw current frame
            _draw_frame(screen, current, font, cell_size, hud_height)

            if hud_callback is not None:
                hud_callback(screen)

            pygame.display.flip()
            clock.tick(fps)

            # Advance to next frame if available
            try:
                current = next(frame_iter)
            except StopIteration:
                # No more frames; keep displaying the last one.
                pass
    finally:
        pygame.quit()


def _draw_frame(
    screen: Surface,
    frame: MazeFrame,
    font: Font,
    cell_size: int,
    hud_height: int,
) -> None:
    """
    Draw a single MazeFrame onto the given pygame Surface.
    """
    # Background
    screen.fill(color("background"))

    rows, cols = frame.rows, frame.cols
    maze_height = rows * cell_size

    # Draw maze cells
    wall_color = color("wall")
    floor_color = color("floor")
    visited_color = color("visited")
    path_color = color("solution_path")
    grid_dot_color = color("grid_dot")

    solution = frame.solution_path or ()
    visited = frame.visited or ()

    # Floor + grid dots
    for r in range(rows):
        for c in range(cols):
            x = c * cell_size
            y = r * cell_size
            rect = (x, y, cell_size, cell_size)

            # Base floor
            pygame.draw.rect(screen, floor_color, rect)

            # Subtle grid dot
            cx = x + cell_size // 2
            cy = y + cell_size // 2
            pygame.draw.circle(screen, grid_dot_color, (cx, cy), max(1, cell_size // 8))

    # Visited cells
    for (r, c) in visited:
        if 0 <= r < rows and 0 <= c < cols:
            x = c * cell_size
            y = r * cell_size
            rect = (x, y, cell_size, cell_size)
            pygame.draw.rect(screen, visited_color, rect)

    # Walls
    for r in range(rows):
        for c in range(cols):
            if frame.grid[r][c]:
                x = c * cell_size
                y = r * cell_size
                rect = (x, y, cell_size, cell_size)
                pygame.draw.rect(screen, wall_color, rect)

    # Solution path overlay (drawn after walls/floor so it's visible)
    for (r, c) in solution:
        if 0 <= r < rows and 0 <= c < cols:
            x = c * cell_size
            y = r * cell_size
            inset = max(2, cell_size // 6)
            rect = (x + inset, y + inset, cell_size - 2 * inset, cell_size - 2 * inset)
            pygame.draw.rect(screen, path_color, rect)

    # Entrance / Exit markers
    if frame.entrance is not None:
        _draw_marker(screen, frame.entrance, cell_size, color("entrance"))

    if frame.exit is not None:
        _draw_marker(screen, frame.exit, cell_size, color("exit"))

    # Player
    if frame.player is not None:
        r, c = frame.player
        if 0 <= r < rows and 0 <= c < cols:
            x = c * cell_size + cell_size // 2
            y = r * cell_size + cell_size // 2
            radius = max(4, cell_size // 3)
            pygame.draw.circle(screen, color("player"), (x, y), radius)

    # HUD bar
    _draw_hud(screen, frame, font, maze_height, hud_height)


def _draw_marker(
    screen: Surface,
    pos: Pos,
    cell_size: int,
    marker_color: Tuple[int, int, int],
) -> None:
    r, c = pos
    x = c * cell_size + cell_size // 2
    y = r * cell_size + cell_size // 2
    radius = max(3, cell_size // 4)
    pygame.draw.circle(screen, marker_color, (x, y), radius)


def _draw_hud(
    screen: Surface,
    frame: MazeFrame,
    font: Font,
    y_offset: int,
    hud_height: int,
) -> None:
    
    hud_bg = color("hud_background")
    hud_border = color("hud_border")
    hud_text = color("hud_text")
    hud_accent = color("hud_accent")

    width = screen.get_width()
    rect = (0, y_offset, width, hud_height)
    pygame.draw.rect(screen, hud_bg, rect)
    pygame.draw.rect(screen, hud_border, rect, 1)

    # Left text: step, size
    lines = []
    if frame.step_index is not None:
        lines.append(f"Step: {frame.step_index}")
    lines.append(f"Size: {frame.rows} x {frame.cols}")

    if frame.note:
        # Short note / solver status
        lines.append(frame.note)

    x = 8
    y = y_offset + 6
    for i, text in enumerate(lines):
        img = font.render(text, True, hud_text if i < 2 else hud_accent)
        screen.blit(img, (x, y))
        y += img.get_height() + 2
