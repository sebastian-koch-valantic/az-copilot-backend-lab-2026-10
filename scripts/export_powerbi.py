"""Export the mart tables as CSV files that the Power BI model reads.

    uv run dwh run && uv run scripts/export_powerbi.py
"""

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dwhpulse import db  # noqa: E402

TABLES = ("dim_product", "dim_customer", "fact_orders")


def main() -> int:
    out = ROOT / "exports"
    out.mkdir(exist_ok=True)
    conn = db.connect()
    for table in TABLES:
        cursor = conn.execute(f"SELECT * FROM mart.{table}")  # noqa: S608 - fixed table names
        with open(out / f"{table}.csv", "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow([d[0] for d in cursor.description])
            writer.writerows(cursor.fetchall())
        print(f"exports/{table}.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
