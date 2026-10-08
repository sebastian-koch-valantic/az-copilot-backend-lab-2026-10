"""Finish-line check for ticket DWH-101 (pipeline status report).

    uv run scripts/lab_check.py

Offline. Seeds a demo run history in a temporary folder and checks the status report.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dwhpulse import db, seed, status  # noqa: E402


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        conn = db.connect(tmp)
        seed.ensure_control(conn)
        seed.load_demo_history(conn)
        report = status.render_status(conn)
        conn.close()

    lines = report.splitlines()
    problems = []

    expected = "Pipeline run 2026-10-06: 7 of 9 steps OK, 1 failed, 1 skipped, 1 late"
    if not lines or lines[0] != expected:
        problems.append(f"AC1 summary line: expected '{expected}'")

    def first_index(word):
        return next((i for i, line in enumerate(lines[1:], 1) if word in line), None)

    failed, skipped = first_index("FAILED"), first_index("SKIPPED")
    ok = first_index(" OK")
    if failed is None or (ok is not None and failed > ok):
        problems.append("AC2 failed steps are listed first")
    elif not all(token in lines[failed] for token in ("core_orders", "CORE", "ORA-00942")):
        problems.append("AC2 failed line shows step, layer and error")
    if skipped is None or "core_orders" not in lines[skipped] or "FAILED" in lines[skipped]:
        problems.append("AC3 skipped step names its upstream step and is not shown as FAILED")
    late_lines = [line for line in lines[1:] if "LATE" in line]
    late_ok = (
        any("mart_dim_customer" in line and " 1 min" in line for line in late_lines)
        and not any("mart_dim_product" in line or "mart_fact_orders" in line for line in late_lines)
    )
    if not late_ok:
        problems.append("AC4 late flags do not follow the lateness rules in docs/confluence/pipeline-operations.md")

    for problem in problems:
        print(f"[FAIL] {problem}")
    if problems:
        return 1
    print("[OK]   summary, failed first, skipped upstream, late flag")
    print("[DONE] DWH-101 complete! Now run `uv run dwh status` and read it as a colleague would.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
