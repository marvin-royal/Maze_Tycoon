from maze_tycoon.io.serialize import (
    write_json, read_json,
    write_jsonl, read_jsonl, append_jsonl, iter_jsonl,
    write_csv,
)

def test_json_roundtrip(tmp_path):
    p = tmp_path / "one.json"
    obj = {"a": 1, "b": [1, 2, 3], "s": "héllo"}
    write_json(obj, p)
    out = read_json(p)
    assert out == obj

def test_jsonl_roundtrip_and_iter(tmp_path):
    p = tmp_path / "many.jsonl"
    rows = [{"i": i, "v": i * i} for i in range(5)]
    write_jsonl(rows, p)
    out_all = read_jsonl(p)
    assert out_all == rows
    out_iter = list(iter_jsonl(p))
    assert out_iter == rows

def test_jsonl_append(tmp_path):
    p = tmp_path / "append.jsonl"
    write_jsonl([{"i": 0}], p)
    append_jsonl({"i": 1}, p)
    append_jsonl([{"i": 2}, {"i": 3}], p)
    out = read_jsonl(p)
    assert [r["i"] for r in out] == [0, 1, 2, 3]

def test_csv_write_infer_headers(tmp_path):
    p = tmp_path / "out.csv"
    rows = [{"a": 1, "b": 2}, {"b": 3, "c": 4}]  # union headers: a,b,c
    write_csv(rows, p)
    text = p.read_text(encoding="utf-8").strip().splitlines()
    # header + 2 rows
    assert len(text) == 3
    assert text[0].replace(",","").strip() == "abc"

def test_csv_write_with_explicit_headers_and_append(tmp_path):
    p = tmp_path / "app.csv"
    write_csv([{"x": 1, "y": 2}], p, fieldnames=["x", "y"])
    write_csv([{"x": 3, "y": 4}], p, fieldnames=["x", "y"], append=True)
    text = p.read_text(encoding="utf-8").strip().splitlines()
    assert text[0].strip() == "x,y"
    assert text[1].strip() == "1,2"
    assert text[2].strip() == "3,4"
