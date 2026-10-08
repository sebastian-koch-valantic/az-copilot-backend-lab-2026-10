"""Pipeline status report, read from ctl.dwh_control."""

import sqlite3

LAYER_ORDER = {"STG": 1, "CORE": 2, "MART": 3}


def latest_run_rows(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    run_id = conn.execute("SELECT MAX(run_id) FROM ctl.dwh_control").fetchone()[0]
    if run_id is None:
        return []
    return conn.execute(
        "SELECT * FROM ctl.dwh_control WHERE run_id = ?", (run_id,)
    ).fetchall()


def render_status(conn: sqlite3.Connection) -> str:
    """Today: a raw dump of the latest run, one line per step."""
    rows = latest_run_rows(conn)
    if not rows:
        return "No pipeline run found."
    lines = []
    for row in sorted(rows, key=lambda r: (LAYER_ORDER.get(r["layer"], 9), r["step_name"])):
        lines.append(
            f"{row['step_name']} | {row['layer']} | {row['status']} | {row['finished_at']}"
            f" | {row['rows_loaded']} | {row['error_message']}"
        )
    return "\n".join(lines)
