from dwhpulse.quality import check_orders


def make(conn, orders, customers=(1, 2)):
    conn.executescript(
        "CREATE TABLE stg.customers (CUSTOMER_ID INTEGER);"
        "CREATE TABLE stg.orders (ORDER_ID INTEGER, PRODUCT_ID INTEGER, CUSTOMER_ID INTEGER,"
        " ORDERED_AT TEXT, AMOUNT_EUR INTEGER);"
    )
    conn.executemany("INSERT INTO stg.customers VALUES (?)", [(c,) for c in customers])
    conn.executemany("INSERT INTO stg.orders VALUES (?,?,?,?,?)", orders)


def rules(issues):
    return {i.rule: i for i in issues}


def test_clean_data_gives_no_issues(conn):
    make(conn, [(1, 1, 1, "2026-09-01", 100), (2, 1, 2, "2026-09-01", 200)])
    assert check_orders(conn) == []


def test_duplicate_order_counts_every_row_of_the_group(conn):
    make(conn, [(1, 1, 1, "2026-09-01", 100), (2, 1, 1, "2026-09-01", 100), (3, 1, 2, "2026-09-01", 5)])
    found = rules(check_orders(conn))["duplicate_order"]
    assert (found.count, found.order_ids) == (2, (1, 2))


def test_non_positive_amount(conn):
    make(conn, [(1, 1, 1, "2026-09-01", 0), (2, 1, 2, "2026-09-01", -5), (3, 1, 2, "2026-09-02", 7)])
    assert rules(check_orders(conn))["non_positive_amount"].order_ids == (1, 2)


def test_unknown_customer(conn):
    make(conn, [(1, 1, 999, "2026-09-01", 100)])
    assert rules(check_orders(conn))["unknown_customer"].count == 1


def test_at_most_five_ids_but_full_count(conn):
    make(conn, [(i, 1, 1, f"2026-09-{i:02d}", 0) for i in range(1, 9)])
    found = rules(check_orders(conn))["non_positive_amount"]
    assert found.count == 8 and found.order_ids == (1, 2, 3, 4, 5)


def test_check_does_not_change_data(conn):
    make(conn, [(1, 1, 1, "2026-09-01", 0)])
    check_orders(conn)
    assert conn.execute("SELECT COUNT(*) FROM stg.orders").fetchone()[0] == 1
