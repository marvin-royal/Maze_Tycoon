from __future__ import annotations
import time
import json
from typing import Any, Dict, List, Optional


class InMemoryMetricsSink:
    """
    Collects run_once() output rows in memory, with optional timestamps,
    and can flush/export them.
    """

    def __init__(self) -> None:
        self._rows: List[Dict[str, Any]] = []
        self._start_time = time.perf_counter()

    # Basic interface (matches MetricsSink Protocol)
    def log_event(self, name: str, **fields: Any) -> None:
        """Record an arbitrary event with timestamp."""
        entry = {"event": name, "t_ms": (time.perf_counter() - self._start_time) * 1000.0}
        entry.update(fields)
        self._rows.append(entry)

    def record_trial(self, row: Dict[str, Any]) -> None:
        """Record a normalized row from scripts.run_once()."""
        row = dict(row)
        row.setdefault("timestamp", time.strftime("%Y-%m-%d %H:%M:%S"))
        self._rows.append(row)

    def aggregate(self) -> Dict[str, float]:
        """Compute simple averages for numeric fields (runtime, expansions, path_length)."""
        if not self._rows:
            return {}
        totals: Dict[str, float] = {}
        count = 0
        for row in self._rows:
            count += 1
            for k, v in row.items():
                if isinstance(v, (int, float)):
                    totals[k] = totals.get(k, 0.0) + float(v)
        return {k: round(v / count, 4) for k, v in totals.items() if k in ("path_length", "node_expansions", "runtime_ms")}

    def flush(self) -> List[Dict[str, Any]]:
        """Return and clear the recorded rows."""
        rows, self._rows = self._rows, []
        return rows

    def export_json(self, path: str, *, indent: int = 2) -> None:
        """Write accumulated metrics to a JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._rows, f, indent=indent)

    # For convenience
    def __len__(self) -> int:
        return len(self._rows)

    def __repr__(self) -> str:
        return f"<InMemoryMetricsSink n={len(self)}>"
