"""Synthetic data only. Creates the simulated Oracle source (src) and a demo run history."""

import random
import sqlite3
from datetime import date, timedelta

DEMO_RUN_ID = "RUN-20261006-0500"

SRC_DDL = """
DROP TABLE IF EXISTS src.products;
DROP TABLE IF EXISTS src.customers;
DROP TABLE IF EXISTS src.orders;
CREATE TABLE src.products (
    PRODUCT_ID INTEGER PRIMARY KEY, PRODUCT_NAME TEXT, PRODUCT_LINE TEXT,
    SALES_CHANNEL TEXT, LISTED_FROM TEXT, LISTED_TO TEXT, STATUS TEXT);
CREATE TABLE src.customers (
    CUSTOMER_ID INTEGER PRIMARY KEY, SEGMENT TEXT, REGION TEXT,
    CREDIT_LIMIT_EUR INTEGER, CREDIT_BLOCK INTEGER);
CREATE TABLE src.orders (
    ORDER_ID INTEGER PRIMARY KEY, PRODUCT_ID INTEGER, CUSTOMER_ID INTEGER,
    ORDERED_AT TEXT, SHIPPED INTEGER, AMOUNT_EUR INTEGER);
"""

CONTROL_DDL = """
CREATE TABLE IF NOT EXISTS ctl.dwh_control (
    run_id TEXT NOT NULL, step_name TEXT NOT NULL, layer TEXT NOT NULL, status TEXT NOT NULL,
    started_at TEXT, finished_at TEXT, rows_loaded INTEGER, error_message TEXT,
    skipped_because TEXT);
DROP VIEW IF EXISTS ctl.v_pipeline_status;
CREATE VIEW ctl.v_pipeline_status AS
    SELECT run_id, step_name, layer, status, started_at, finished_at, rows_loaded,
           error_message, skipped_because
    FROM ctl.dwh_control;
"""

_PRODUCT_LINES = ("pumps", "valves")
_CHANNELS = ("DIRECT", "PARTNER", "ONLINE")
_SEGMENTS = ("ENTERPRISE", "MIDMARKET", "SMB", "PUBLIC")
_REGIONS = ("DE-N", "DE-S", "DE-W", "DE-E")


def ensure_control(conn: sqlite3.Connection) -> None:
    conn.executescript(CONTROL_DDL)


def load_source(conn: sqlite3.Connection, seed: int = 42) -> None:
    rng = random.Random(seed)
    conn.executescript(SRC_DDL)
    start = date(2026, 9, 1)
    products = []
    for pid in range(1, 7):
        first = start + timedelta(days=(pid - 1) * 4)
        products.append((pid, f" Product {pid:02d} ", rng.choice(_PRODUCT_LINES),
                         _CHANNELS[pid % 3], first.isoformat(),
                         (first + timedelta(days=20)).isoformat(),
                         "ACTIVE" if pid != 6 else "DISCONTINUED"))
    conn.executemany("INSERT INTO src.products VALUES (?,?,?,?,?,?,?)", products)
    customers = [(i, rng.choice(_SEGMENTS), rng.choice(_REGIONS),
                  rng.choice((5000, 10000, 25000)), 1 if i % 17 == 0 else 0)
                 for i in range(1, 41)]
    conn.executemany("INSERT INTO src.customers VALUES (?,?,?,?,?)", customers)
    orders, order_id = [], 1
    for pid, _name, _line, _ch, first, _end, status in products:
        if status == "DISCONTINUED":
            continue
        for customer_id in rng.sample(range(1, 41), 22):
            day = date.fromisoformat(first) + timedelta(days=rng.randint(0, 12))
            orders.append((order_id, pid, customer_id, f"{day.isoformat()} 09:{rng.randint(10, 59)}:00",
                           0 if rng.random() < 0.05 else 1, rng.randint(2, 40) * 100))
            order_id += 1
    # Deliberately dirty rows for ticket DWH-103: a duplicate, a zero amount, an unknown customer.
    first_order = orders[0]
    orders.append((order_id, first_order[1], first_order[2], first_order[3], 1, first_order[5]))
    orders.append((order_id + 1, 1, 2, "2026-09-05 10:00:00", 1, 0))
    orders.append((order_id + 2, 1, 999, "2026-09-05 10:30:00", 1, 1500))
    conn.executemany("INSERT INTO src.orders VALUES (?,?,?,?,?,?)", orders)
    conn.commit()


def load_demo_history(conn: sqlite3.Connection) -> None:
    """A fixed, deterministic run: one failure, one skipped step, one step late by seconds,
    one step finishing exactly at the deadline."""
    conn.execute("DELETE FROM ctl.dwh_control WHERE run_id = ?", (DEMO_RUN_ID,))
    day = "2026-10-06"
    rows = [
        ("stg_products", "STG", "OK", "05:00:05", "05:00:09", 6, None, None),
        ("stg_customers", "STG", "OK", "05:00:09", "05:00:12", 40, None, None),
        ("stg_orders", "STG", "OK", "05:00:12", "05:58:41", 113, None, None),  # slow source
        ("core_products", "CORE", "OK", "05:58:41", "05:58:44", 5, None, None),
        ("core_customers", "CORE", "OK", "05:58:44", "05:58:47", 38, None, None),
        ("core_orders", "CORE", "FAILED", "05:58:47", "05:58:48", None,
         "ORA-00942: table or view does not exist", None),
        ("mart_dim_product", "MART", "OK", "05:58:48", "06:00:00", 5, None, None),
        ("mart_dim_customer", "MART", "OK", "06:00:00", "06:00:30", 38, None, None),
        ("mart_fact_orders", "MART", "SKIPPED", "06:00:30", "06:00:30", None, None, "core_orders"),
    ]
    conn.executemany(
        "INSERT INTO ctl.dwh_control VALUES (?,?,?,?,?,?,?,?,?)",
        [(DEMO_RUN_ID, n, l, s, f"{day} {a}", f"{day} {b}", r, e, k) for n, l, s, a, b, r, e, k in rows],
    )
    conn.commit()
