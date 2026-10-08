"""Runs the pipeline and logs every step into ctl.dwh_control."""

import sqlite3
from datetime import datetime, timedelta
from typing import Callable

from dwhpulse import config
from dwhpulse.pipeline import STEPS, Step


class SimulatedOracleError(Exception):
    """Stands in for an error raised by the Oracle database."""


def scheduler_clock() -> Callable[[], datetime]:
    """Simulated scheduler time: today at 05:00, then real elapsed time.

    A live run in a workshop afternoon must not look 'late' only because the wall clock is later.
    """
    began = datetime.now()
    # Offset by the real time within a half hour, so two runs never share a run id.
    offset = timedelta(seconds=(began.minute % 30) * 60 + began.second)
    start = began.replace(hour=5, minute=0, second=0, microsecond=0) + offset
    return lambda: start + (datetime.now() - began)


def _stamp(now: datetime) -> str:
    return now.strftime("%Y-%m-%d %H:%M:%S")


def _log(conn: sqlite3.Connection, run_id: str, step: Step, status: str, started: str,
         finished: str, rows: int | None = None, error: str | None = None,
         skipped_because: str | None = None) -> None:
    conn.execute(
        "INSERT INTO ctl.dwh_control (run_id, step_name, layer, status, started_at, finished_at,"
        " rows_loaded, error_message, skipped_because) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (run_id, step.name, step.layer, status, started, finished, rows, error, skipped_because),
    )
    conn.commit()


def run_pipeline(conn: sqlite3.Connection, steps: tuple[Step, ...] = STEPS, *,
                 inject_failure: str | None = None,
                 clock: Callable[[], datetime] | None = None) -> str:
    """Run all steps in order. A step whose upstream failed or was skipped is SKIPPED."""
    clock = clock or scheduler_clock()
    run_id = "RUN-" + clock().strftime("%Y%m%d-%H%M%S")
    not_ok: dict[str, str] = {}  # step name -> the failed step it traces back to
    for step in steps:
        started = _stamp(clock())
        blocker = next((d for d in step.depends_on if d in not_ok), None)
        if blocker:
            not_ok[step.name] = not_ok[blocker]
            _log(conn, run_id, step, "SKIPPED", started, started, skipped_because=not_ok[blocker])
            continue
        try:
            if step.name == inject_failure:
                raise SimulatedOracleError("ORA-00942: table or view does not exist")
            conn.executescript((config.SQL_DIR / step.sql_file).read_text(encoding="utf-8"))
            rows = conn.execute(f"SELECT COUNT(*) FROM {step.target}").fetchone()[0]
            _log(conn, run_id, step, "OK", started, _stamp(clock()), rows=rows)
        except Exception as exc:  # the log records the failure, the run continues
            not_ok[step.name] = step.name
            _log(conn, run_id, step, "FAILED", started, _stamp(clock()), error=str(exc))
    return run_id
