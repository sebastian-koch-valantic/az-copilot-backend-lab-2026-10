"""Pipeline status report, read from ctl.dwh_control (reference solution DWH-101)."""

import math
import sqlite3
from datetime import datetime

from dwhpulse.config import DAILY_DEADLINE

LAYER_ORDER = {"STG": 1, "CORE": 2, "MART": 3}


def latest_run_rows(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    run_id = conn.execute("SELECT MAX(run_id) FROM ctl.dwh_control").fetchone()[0]
    if run_id is None:
        return []
    return conn.execute(
        "SELECT step_name, layer, status, started_at, finished_at, rows_loaded,"
        " error_message, skipped_because FROM ctl.dwh_control WHERE run_id = ?",
        (run_id,),
    ).fetchall()


def _minutes_late(finished_at: str | None) -> int:
    """Started minutes after the deadline: 06:00:00 -> 0, 06:00:30 -> 1, 06:25:00 -> 25."""
    if not finished_at:
        return 0
    finished = datetime.strptime(finished_at, "%Y-%m-%d %H:%M:%S")
    hour, minute = map(int, DAILY_DEADLINE.split(":"))
    deadline = finished.replace(hour=hour, minute=minute, second=0)
    seconds = (finished - deadline).total_seconds()
    return max(0, math.ceil(seconds / 60))


def render_status(conn: sqlite3.Connection) -> str:
    rows = latest_run_rows(conn)
    if not rows:
        return "No pipeline run found."
    ordered = sorted(rows, key=lambda r: (LAYER_ORDER.get(r["layer"], 9), r["step_name"]))
    failed = [r for r in ordered if r["status"] == "FAILED"]
    skipped = [r for r in ordered if r["status"] == "SKIPPED"]
    late = [r for r in ordered if r["status"] == "OK" and _minutes_late(r["finished_at"]) > 0]
    ok = [r for r in ordered if r["status"] == "OK" and r not in late]
    run_date = max(r["started_at"] for r in rows)[:10]
    n_ok = len(ok) + len(late)
    lines = [
        f"Pipeline run {run_date}: {n_ok} of {len(rows)} steps OK, "
        f"{len(failed)} failed, {len(skipped)} skipped, {len(late)} late"
    ]
    for r in failed:
        lines.append(f"FAILED  {r['step_name']} ({r['layer']}): {r['error_message']}")
    for r in skipped:
        lines.append(f"SKIPPED {r['step_name']} ({r['layer']}): upstream {r['skipped_because']} failed")
    for r in late:
        lines.append(
            f"LATE    {r['step_name']} ({r['layer']}): finished {r['finished_at'][11:]},"
            f" {_minutes_late(r['finished_at'])} min after {DAILY_DEADLINE}"
        )
    for r in ok:
        lines.append(f"OK      {r['step_name']} ({r['layer']}): {r['rows_loaded']} rows")
    return "\n".join(lines)
