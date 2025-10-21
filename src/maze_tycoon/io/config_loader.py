# src/maze_tycoon/io/config_loader.py
from __future__ import annotations
import yaml
from pathlib import Path
from typing import Any, Dict

def load_yaml(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)
