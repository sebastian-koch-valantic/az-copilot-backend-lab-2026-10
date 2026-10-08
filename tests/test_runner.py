from datetime import datetime, timedelta

from dwhpulse.runner import run_pipeline


def fake_clock():
    now = datetime(2026, 10, 6, 5, 0, 0)

    def tick():
        nonlocal now
        now += timedelta(seconds=1)
        return now

    return tick


def statuses(conn, run_id):
    rows = conn.execute("SELECT step_name, status, skipped_because FROM ctl.dwh_control"
                        " WHERE run_id = ?", (run_id,)).fetchall()
    return {r["step_name"]: (r["status"], r["skipped_because"]) for r in rows}


def test_a_clean_run_loads_every_layer(conn):
    run_id = run_pipeline(conn, clock=fake_clock())
    assert {status for status, _ in statuses(conn, run_id).values()} == {"OK"}
    assert conn.execute("SELECT COUNT(*) FROM mart.fact_orders").fetchone()[0] > 0


def test_a_failed_step_skips_everything_downstream(conn):
    run_id = run_pipeline(conn, inject_failure="core_orders", clock=fake_clock())
    result = statuses(conn, run_id)
    assert result["core_orders"][0] == "FAILED"
    assert result["mart_fact_orders"] == ("SKIPPED", "core_orders")
    assert result["mart_dim_product"][0] == "OK"  # independent branch still runs


def test_credit_blocked_customers_never_reach_the_mart(conn):
    run_pipeline(conn, clock=fake_clock())
    blocked = {r[0] for r in conn.execute("SELECT CUSTOMER_ID FROM src.customers WHERE CREDIT_BLOCK = 1")}
    in_mart = {r[0] for r in conn.execute("SELECT DISTINCT CUSTOMER_ID FROM mart.fact_orders")}
    assert not blocked & in_mart
