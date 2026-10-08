"""Command line: `uv run dwh seed | run | status | peek <schema.table>`."""

import argparse

from dwhpulse import config, db, runner, seed, status


def peek_table(conn, table: str, rows: int = 5) -> str:
    """First rows of a table as aligned text. Read only."""
    schema, _, name = table.partition(".")
    known = {r[0] for r in conn.execute(f"SELECT name FROM {schema}.sqlite_master WHERE type = 'table'")} \
        if schema in config.SCHEMAS else set()
    if name not in known:
        return f"Unknown table {table}. Try: uv run dwh peek mart.fact_orders"
    cursor = conn.execute(f"SELECT * FROM {schema}.{name} LIMIT ?", (rows,))  # name checked above
    header = [d[0] for d in cursor.description]
    data = [[str(v) for v in row] for row in cursor.fetchall()]
    widths = [max(len(h), *(len(r[i]) for r in data)) if data else len(h) for i, h in enumerate(header)]
    lines = ["  ".join(h.ljust(w) for h, w in zip(header, widths))]
    lines += ["  ".join(v.ljust(w) for v, w in zip(r, widths)) for r in data]
    total = conn.execute(f"SELECT COUNT(*) FROM {schema}.{name}").fetchone()[0]
    return "\n".join(lines + [f"({len(data)} of {total} rows)"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dwh", description="az-copilot-backend-lab-2026-10 sandbox pipeline")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("seed", help="create the simulated source data and a demo run history")
    run = sub.add_parser("run", help="run the whole pipeline (STG, CORE, MART)")
    run.add_argument("--inject-failure", metavar="STEP", help="make this step fail with ORA-00942")
    sub.add_parser("status", help="show the status of the latest pipeline run")
    peek = sub.add_parser("peek", help="show the first rows of a table, for example mart.fact_orders")
    peek.add_argument("table", help="schema.table, for example src.orders or mart.fact_orders")
    peek.add_argument("--rows", type=int, default=5)
    args = parser.parse_args(argv)

    conn = db.connect()
    seed.ensure_control(conn)
    if args.command == "seed":
        seed.load_source(conn)
        seed.load_demo_history(conn)
        print("Seeded src.* and a demo run history in ctl.dwh_control.")
    elif args.command == "run":
        run_id = runner.run_pipeline(conn, inject_failure=args.inject_failure)
        print(f"Finished {run_id}. See: uv run dwh status")
    elif args.command == "peek":
        print(peek_table(conn, args.table, args.rows))
    else:
        print(status.render_status(conn))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
