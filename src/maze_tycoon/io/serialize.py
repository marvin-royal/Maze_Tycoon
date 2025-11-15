from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Iterable, Iterator, Mapping, Optional, Sequence, Union, List, Dict

Pathish = Union[str, Path]
Row = Mapping[str, Any]


def _p(path: Pathish) -> Path:
    return path if isinstance(path, Path) else Path(path)


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _atomic_write_text(path: Path, data: str, *, encoding: str = "utf-8") -> None:
    """Write text atomically: write to a temp file in the same dir, then replace."""
    _ensure_parent(path)
    with NamedTemporaryFile("w", delete=False, dir=str(path.parent), encoding=encoding) as tmp:
        tmp.write(data)
        tmp_name = tmp.name
    os.replace(tmp_name, path)  # atomic on most OS/filesystems


# ---------- JSON ----------

def write_json(obj: Any, path: Pathish, *, indent: int = 2, encoding: str = "utf-8") -> None:
    """Write one JSON object (pretty by default)."""
    p = _p(path)
    _ensure_parent(p)
    text = json.dumps(obj, indent=indent, ensure_ascii=False)
    _atomic_write_text(p, text, encoding=encoding)


def read_json(path: Pathish, *, encoding: str = "utf-8") -> Any:
    p = _p(path)
    with p.open("r", encoding=encoding) as f:
        return json.load(f)


# ---------- JSONL (one JSON object per line) ----------

def write_jsonl(rows: Iterable[Row], path: Pathish, *, encoding: str = "utf-8") -> None:
    """
    Write iterable of mapping-like rows to JSON Lines.
    Overwrites by default (use append_jsonl to append).
    """
    p = _p(path)
    _ensure_parent(p)
    with NamedTemporaryFile("w", delete=False, dir=str(p.parent), encoding=encoding) as tmp:
        wrote_any = False
        for row in rows:
            tmp.write(json.dumps(row, ensure_ascii=False))
            tmp.write("\n")
            wrote_any = True
        tmp_name = tmp.name
    # If no rows at all, still create/overwrite to an empty file
    if not wrote_any:
        Path(tmp_name).write_text("", encoding=encoding)
    os.replace(tmp_name, p)


def append_jsonl(rows: Union[Row, Iterable[Row]], path: Pathish, *, encoding: str = "utf-8") -> None:
    """
    Append one row or many rows to JSONL file. Creates file if missing.
    """
    p = _p(path)
    _ensure_parent(p)
    # normalize to iterable
    if isinstance(rows, Mapping):
        rows = [rows]
    with p.open("a", encoding=encoding) as f:
        for row in rows:  # type: ignore[assignment]
            f.write(json.dumps(row, ensure_ascii=False))
            f.write("\n")


def read_jsonl(path: Pathish, *, encoding: str = "utf-8") -> List[Dict[str, Any]]:
    """Read entire JSONL into a list (small/medium files)."""
    return list(iter_jsonl(path, encoding=encoding))


def iter_jsonl(path: Pathish, *, encoding: str = "utf-8") -> Iterator[Dict[str, Any]]:
    """Stream JSONL rows (large files)."""
    p = _p(path)
    if not p.exists():
        return iter(())  # empty iterator
    with p.open("r", encoding=encoding) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


# ---------- CSV ----------

def write_csv(
    rows: Iterable[Row],
    path: Pathish,
    *,
    fieldnames: Optional[Sequence[str]] = None,
    append: bool = False,
    encoding: str = "utf-8",
    newline: str = "",
) -> None:
    """
    Write mapping-like rows to CSV. If fieldnames is not provided, they are inferred
    from the union of keys across rows (order is deterministic by sorted keys).
    If append=True and file exists, header is NOT rewritten.
    """
    p = _p(path)
    _ensure_parent(p)

    rows_list: List[Row] = list(rows)

    if fieldnames is None:
        keyset = set()  # infer union of keys
        for r in rows_list:
            keyset.update(r.keys())
        fieldnames = sorted(keyset)

    # If we still have no fieldnames (e.g., empty rows and no fieldnames), write/append nothing but ensure file
    if not fieldnames:
        if not p.exists():
            p.write_text("", encoding=encoding)
        return

    mode = "a" if append and p.exists() else "w"
    with p.open(mode, encoding=encoding, newline=newline) as f:
        writer = csv.DictWriter(f, fieldnames=list(fieldnames))
        if mode == "w":
            writer.writeheader()
        for r in rows_list:
            writer.writerow({k: r.get(k, "") for k in fieldnames})
