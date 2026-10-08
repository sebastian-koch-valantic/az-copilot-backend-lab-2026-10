from dwhpulse.cli import peek_table
from dwhpulse.runner import run_pipeline


def test_peek_shows_header_rows_and_count(conn):
    run_pipeline(conn)
    text = peek_table(conn, "mart.fact_orders", 3)
    assert text.splitlines()[0].startswith("ORDER_ID")
    assert text.endswith(")") and "(3 of" in text


def test_peek_rejects_unknown_tables(conn):
    assert peek_table(conn, "mart.nope").startswith("Unknown table")
    assert peek_table(conn, "x; DROP TABLE src.orders").startswith("Unknown table")
