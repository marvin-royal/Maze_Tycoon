from __future__ import annotations
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple, Union
from statistics import mean

Row = Mapping[str, Any]
Rows = Iterable[Row]


def _as_groups(rows: Rows, by: Union[str, Sequence[str]]) -> Dict[Tuple[Any, ...], List[Row]]:
    """Group rows by one or more keys. Missing keys group under None."""
    if isinstance(by, str):
        by = [by]
    groups: Dict[Tuple[Any, ...], List[Row]] = {}
    for r in rows:
        key = tuple(r.get(k) for k in by)  # type: ignore[arg-type]
        groups.setdefault(key, []).append(r)
    return groups


def group_mean(
    rows: Rows,
    *,
    by: Union[str, Sequence[str]] = "algorithm",
    fields: Sequence[str] = ("path_length", "runtime_ms", "node_expansions"),
    round_to: int = 4,
) -> List[Dict[str, Any]]:
    """
    Compute per-group means for numeric fields.

    Returns a list of dicts with the group keys plus mean_<field> entries.
    Rows missing a field are ignored for that field (not counted as zeros).
    """
    groups = _as_groups(rows, by)
    by = (by,) if isinstance(by, str) else tuple(by)
    out: List[Dict[str, Any]] = []

    for key, bucket in groups.items():
        row_out: Dict[str, Any] = {k: v for k, v in zip(by, key)}
        for f in fields:
            vals = [float(r[f]) for r in bucket if isinstance(r.get(f), (int, float))]
            if vals:
                row_out[f"mean_{f}"] = round(mean(vals), round_to)
        out.append(row_out)

    # Stable sort by group keys for deterministic tests
    out.sort(key=lambda d: tuple(d.get(k) for k in by))
    return out


def percentiles(
    rows: Rows,
    *,
    field: str = "runtime_ms",
    q: Sequence[Union[int, float]] = (50, 90, 95),
    round_to: int = 4,
) -> Dict[Union[int, float], float]:
    """
    Compute simple (nearest-rank) percentiles for a numeric field across all rows.
    Empty input -> {}. Non-numeric values are ignored.
    """
    vals = sorted(float(v) for v in (r.get(field) for r in rows) if isinstance(v, (int, float)))
    if not vals:
        return {}
    n = len(vals)
    def rank(p: Union[int, float]) -> int:
        # nearest-rank (1-based), clamp to [1, n]
        import math
        r = int(math.ceil((p / 100.0) * n))
        return max(1, min(n, r))
    out: Dict[Union[int, float], float] = {}
    for p in q:
        out[p] = round(vals[rank(p) - 1], round_to)
    return out


def groupby_agg(
    rows: Rows,
    *,
    by: Union[str, Sequence[str]],
    agg: Mapping[str, str],
    round_to: int = 4,
) -> List[Dict[str, Any]]:
    """
    General-purpose groupby with simple aggregations.

    agg: mapping of output_field -> "mean" | "min" | "max" over an input field of the same name.
         Example: {"runtime_ms": "mean", "path_length": "max"}
    """
    groups = _as_groups(rows, by)
    by = (by,) if isinstance(by, str) else tuple(by)
    out: List[Dict[str, Any]] = []

    for key, bucket in groups.items():
        row_out: Dict[str, Any] = {k: v for k, v in zip(by, key)}
        # collect numeric vectors
        columns: Dict[str, List[float]] = {}
        for col in agg.keys():
            columns[col] = [float(r[col]) for r in bucket if isinstance(r.get(col), (int, float))]
        # apply
        for col, op in agg.items():
            vals = columns[col]
            if not vals:
                continue
            if op == "mean":
                from statistics import mean as _m
                row_out[f"{op}_{col}"] = round(_m(vals), round_to)
            elif op == "min":
                row_out[f"{op}_{col}"] = round(min(vals), round_to)
            elif op == "max":
                row_out[f"{op}_{col}"] = round(max(vals), round_to)
            else:
                raise ValueError(f"Unsupported aggregation '{op}' for column '{col}'")
        out.append(row_out)

    out.sort(key=lambda d: tuple(d.get(k) for k in by))
    return out
