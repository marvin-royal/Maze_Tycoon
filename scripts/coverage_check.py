
#!/usr/bin/env python3
"""Run tests and produce a clear 'what's left uncovered' report.

Usage:
  python scripts/coverage_check.py              # console summary + markdown
  python scripts/coverage_check.py --html       # also build htmlcov/
  python scripts/coverage_check.py --fail=90    # exit nonzero if total < 90%
"""
import argparse
import io
import os
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--html', action='store_true', help='Generate HTML coverage report (htmlcov/)')
    parser.add_argument('--fail', type=float, default=None, help='Fail if total coverage < N (e.g., 90)')
    parser.add_argument('--source', nargs='*', default=['maze_tycoon'], help='Source package(s) to measure')
    args = parser.parse_args()

    # Ensure repository root on sys.path
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    # Lazy import so we can print friendly errors
    try:
        import coverage
    except ImportError:
        print("Missing dependency: coverage. Install with `pip install coverage pytest`", file=sys.stderr)
        sys.exit(2)
    try:
        import pytest
    except ImportError:
        print("Missing dependency: pytest. Install with `pip install pytest`", file=sys.stderr)
        sys.exit(2)

    # Configure coverage
    cov = coverage.Coverage(source=args.source, omit=['*/tests/*', '*/__pycache__/*'])
    cov.erase()
    cov.start()

    # Run pytest
    exit_code = pytest.main([])  # use pytest.ini/pyproject if present
    cov.stop()
    cov.save()

    # Build text report (capture to buffer), and collect file stats
    buf = io.StringIO()
    total = cov.report(file=buf, show_missing=False)
    text_table = buf.getvalue()

    # Per-file analysis for 'what is left' summary
    # analysis2(file) -> (filename, statements, excluded, missing, missing_str)
    file_stats = []
    for file in sorted(cov.get_data().measured_files()):
        if any(part in ('tests', '__pycache__') for part in Path(file).parts):
            continue
        try:
            # cov.analysis2(file) -> (filename, statements, excluded, missing, missing_str)
            result = cov.analysis2(file)
        except coverage.CoverageException:
            continue

        filename, statements, excluded, missing, _ = result
        stmts = len(statements) if isinstance(statements, list) else statements
        miss_list = missing if isinstance(missing, list) else []
        covered = stmts - len(miss_list)
        pct = 100.0 * covered / max(1, stmts)

        file_stats.append({
            'file': str(Path(filename).resolve().relative_to(ROOT)),
            'statements': stmts,
            'missed': len(miss_list),
            'percent': pct,
            'missing_lines': miss_list,
        })

    file_stats.sort(key=lambda d: (d['percent'], -d['missed']))

    # Create human-friendly missing line ranges: [1,2,3,7,8] -> "1-3, 7-8"
    def compress_ranges(nums):
        if not nums:
            return ""
        nums = sorted(nums)
        ranges = []
        start = prev = nums[0]
        for n in nums[1:]:
            if n == prev + 1:
                prev = n
            else:
                ranges.append((start, prev))
                start = prev = n
        ranges.append((start, prev))
        parts = []
        for a,b in ranges:
            parts.append(f"{a}" if a==b else f"{a}-{b}")
        return ", ".join(parts)

    # Emit markdown summary
    md_lines = []
    md_lines.append("# Test Coverage Summary\n")
    md_lines.append(f"**Total Coverage:** {total:.2f}%\n")
    md_lines.append("\n## Files Needing Attention (lowest coverage first)\n")
    md_lines.append("| File | Coverage | Missed / Stmts | Missing Lines |")
    md_lines.append("|---|---:|---:|---|")
    for d in file_stats:
        if d['percent'] >= 100.0:
            continue
        md_lines.append(f"| `{d['file']}` | {d['percent']:.1f}% | {d['missed']} / {d['statements']} | {compress_ranges(d['missing_lines'])} |")

    md = "\n".join(md_lines) + "\n"

    out_md = ROOT / "coverage_summary.md"
    out_md.write_text(md, encoding="utf-8")

    # Optional HTML
    if args.html:
        cov.html_report(directory=str(ROOT/"htmlcov"))

    # Console output
    print(text_table.strip())
    print("\nWrote markdown summary to:", out_md)
    if args.html:
        print("Wrote HTML report to:", ROOT/"htmlcov/index.html")

    if args.fail is not None and total < float(args.fail):
        print(f"FAIL: total coverage {total:.2f}% < threshold {args.fail:.2f}%", file=sys.stderr)
        sys.exit(1)

    # Propagate pytest failure if tests failed
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
