"""
Color palettes and semantic color helpers for Maze Tycoon.

This module centralises all color choices so that the pygame UI, plotting,
and any future renderers can share a consistent visual language.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

# Basic RGB color tuple, suitable for pygame.
Color = Tuple[int, int, int]


@dataclass(frozen=True)
class MazePalette:
    # Core maze visuals
    background: Color
    grid_dot: Color
    wall: Color
    floor: Color
    solution_path: Color
    visited: Color

    # Points of interest
    entrance: Color
    exit: Color
    player: Color
    collectible: Color

    # UI / HUD
    hud_background: Color
    hud_border: Color
    hud_text: Color
    hud_accent: Color

    # Misc / states
    highlight: Color
    error: Color
    debug: Color


# --- Preset palettes ------------------------------------------------------- #

DARK_PALETTE = MazePalette(
    background=(12, 12, 16),
    grid_dot=(36, 36, 48),
    wall=(220, 90, 70),
    floor=(24, 24, 32),
    solution_path=(70, 190, 240),
    visited=(80, 80, 110),
    entrance=(120, 200, 120),
    exit=(240, 220, 120),
    player=(250, 250, 250),
    collectible=(255, 170, 80),
    hud_background=(18, 18, 26),
    hud_border=(90, 90, 120),
    hud_text=(235, 235, 245),
    hud_accent=(150, 120, 255),
    highlight=(255, 255, 160),
    error=(255, 80, 80),
    debug=(160, 100, 255),
)

LIGHT_PALETTE = MazePalette(
    background=(245, 245, 250),
    grid_dot=(220, 220, 230),
    wall=(90, 50, 40),
    floor=(230, 230, 240),
    solution_path=(40, 140, 210),
    visited=(180, 180, 200),
    entrance=(60, 160, 90),
    exit=(210, 180, 80),
    player=(40, 40, 40),
    collectible=(210, 130, 40),
    hud_background=(250, 250, 255),
    hud_border=(180, 180, 200),
    hud_text=(30, 30, 40),
    hud_accent=(110, 80, 210),
    highlight=(250, 240, 160),
    error=(210, 70, 70),
    debug=(130, 80, 220),
)

HIGH_CONTRAST_PALETTE = MazePalette(
    background=(0, 0, 0),
    grid_dot=(60, 60, 60),
    wall=(255, 255, 255),
    floor=(0, 0, 0),
    solution_path=(0, 255, 255),
    visited=(128, 128, 128),
    entrance=(0, 255, 0),
    exit=(255, 255, 0),
    player=(255, 0, 255),
    collectible=(255, 128, 0),
    hud_background=(0, 0, 0),
    hud_border=(255, 255, 255),
    hud_text=(255, 255, 255),
    hud_accent=(0, 255, 255),
    highlight=(255, 0, 0),
    error=(255, 0, 0),
    debug=(0, 0, 255),
)


PALETTES: Dict[str, MazePalette] = {
    "dark": DARK_PALETTE,
    "light": LIGHT_PALETTE,
    "high_contrast": HIGH_CONTRAST_PALETTE,
}

_active_palette_name: str = "dark"


# --- Public API ------------------------------------------------------------ #

def get_palette(name: str | None = None) -> MazePalette:
    """
    Return a MazePalette by name.

    If name is None, returns the currently active palette.
    Raises KeyError for unknown names.
    """
    if name is None:
        return PALETTES[_active_palette_name]
    return PALETTES[name]


def set_active_palette(name: str) -> None:
    """
    Set the active palette by name.

    Intended for configuration / command-line options.
    """
    global _active_palette_name
    if name not in PALETTES:
        raise KeyError(f"Unknown palette: {name!r}")
    _active_palette_name = name


def color(role: str) -> Color:
    """
    Convenience accessor for a color by semantic role name.

    Example:
        screen.fill(color("background"))
        wall_color = color("wall")

    Valid roles correspond to MazePalette field names.
    """
    palette = get_palette()
    try:
        return getattr(palette, role)
    except AttributeError as exc:
        raise KeyError(f"Unknown color role: {role!r}") from exc
