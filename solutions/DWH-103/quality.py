"""Data quality check on stg.orders (reference solution DWH-103)."""

import sqlite3

from pydantic import BaseModel, ConfigDict

_RULES = {
    "duplicate_order": (
        "SELECT ORDER_ID FROM stg.orders WHERE (PRODUCT_ID, CUSTOMER_ID, ORDERED_AT) IN ("
        " SELECT PRODUCT_ID, CUSTOMER_ID, ORDERED_AT FROM stg.orders"
        " GROUP BY PRODUCT_ID, CUSTOMER_ID, ORDERED_AT HAVING COUNT(*) > 1) ORDER BY ORDER_ID"
    ),
    "non_positive_amount": (
        "SELECT ORDER_ID FROM stg.orders WHERE AMOUNT_EUR <= 0 ORDER BY ORDER_ID"
    ),
    "unknown_customer": (
        "SELECT ORDER_ID FROM stg.orders WHERE CUSTOMER_ID NOT IN"
        " (SELECT CUSTOMER_ID FROM stg.customers) ORDER BY ORDER_ID"
    ),
}


class Issue(BaseModel):
    model_config = ConfigDict(frozen=True)

    rule: str
    count: int
    order_ids: tuple[int, ...]


def check_orders(conn: sqlite3.Connection) -> list[Issue]:
    issues = []
    for rule, sql in _RULES.items():
        ids = [row[0] for row in conn.execute(sql)]
        if ids:
            issues.append(Issue(rule=rule, count=len(ids), order_ids=tuple(ids[:5])))
    return issues
