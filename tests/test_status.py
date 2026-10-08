from dwhpulse import seed, status


def test_demo_history_has_one_failure_and_one_skipped_step(conn):
    seed.load_demo_history(conn)
    rows = status.latest_run_rows(conn)
    assert sorted(r["status"] for r in rows).count("FAILED") == 1
    assert sorted(r["status"] for r in rows).count("SKIPPED") == 1


def test_no_run_gives_a_clear_message(conn):
    assert status.render_status(conn) == "No pipeline run found."
