# maze_tycoon/game/logging.py
from __future__ import annotations

import logging
from logging import Logger
from pathlib import Path
from typing import Optional, Mapping, Any

_LOGGER_INITIALISED = False
_ROOT_LOGGER_NAME = "maze_tycoon"


def init_logging(
    *,
    level: int = logging.INFO,
    mode: str = "game",
    log_dir: Optional[str] = None,
    run_id: Optional[str] = None,
) -> Logger:
    """
    Initialise the root Maze Tycoon logger.

    mode: "game" | "cli" | "test" etc. (currently just for tagging).
    log_dir: if provided, write a log file there in addition to console.
    run_id: optional suffix for per-run log files.
    """
    global _LOGGER_INITIALISED

    if _LOGGER_INITIALISED:
        return logging.getLogger(_ROOT_LOGGER_NAME)

    logger = logging.getLogger(_ROOT_LOGGER_NAME)
    logger.setLevel(level)
    logger.propagate = False  # don't spam root Python logger

    fmt = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    # Console handler
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    logger.addHandler(console)

    # Optional file handler
    if log_dir is not None:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
        filename = "maze_tycoon.log"
        if run_id is not None:
            filename = f"maze_tycoon_{run_id}.log"
        file_handler = logging.FileHandler(path / filename, encoding="utf-8")
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)

    _LOGGER_INITIALISED = True
    logger.debug("Logging initialised (mode=%s)", mode)
    return logger


def get_logger(name: str) -> Logger:
    """
    Get a child logger under the maze_tycoon namespace.

    Example: get_logger("run") -> maze_tycoon.run
    """
    return logging.getLogger(f"{_ROOT_LOGGER_NAME}.{name}")


def log_game_event(
    logger: Logger,
    event: str,
    fields: Optional[Mapping[str, Any]] = None,
    level: int = logging.INFO,
) -> None:
    """
    Convenience helper to log a structured-ish game event.

    Example:
        log_game_event(logger, "run_completed",
                       {"solver": "bfs", "steps": 120, "reward": 35})
    """
    if fields:
        payload = " ".join(f"{k}={v}" for k, v in fields.items())
        msg = f"{event} {payload}"
    else:
        msg = event

    logger.log(level, msg)
