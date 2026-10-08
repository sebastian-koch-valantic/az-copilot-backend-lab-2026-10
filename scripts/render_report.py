"""Render a static HTML preview of the Power BI report 'Sales Credit Monitor'.

    uv run dwh run && uv run scripts/render_report.py   ->   exports/report.html

SIMULATION. This is not Power BI: it recomputes the measures of powerbi/model.md in plain
Python/SQL and draws bars as inline SVG. Use it to see what a mart change does to the report.
"""

import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dwhpulse import db  # noqa: E402


def main() -> int:
    conn = db.connect()
    orders, revenue, customers = conn.execute(
        "SELECT COUNT(*), COALESCE(SUM(AMOUNT_EUR), 0), COUNT(DISTINCT CUSTOMER_ID)"
        " FROM mart.fact_orders"
    ).fetchone()
    per_customer = round(revenue / customers, 2) if customers else 0  # DIVIDE() in DAX
    weeks = conn.execute(
        "SELECT strftime('%Y-W%W', ORDER_DATE) AS WEEK, PRODUCT_LINE, SUM(AMOUNT_EUR) AS REVENUE"
        " FROM mart.fact_orders GROUP BY WEEK, PRODUCT_LINE ORDER BY WEEK, PRODUCT_LINE"
    ).fetchall()
    conn.close()

    top = max((w["REVENUE"] for w in weeks), default=1)
    bars = []
    for i, w in enumerate(weeks):
        height = int(160 * w["REVENUE"] / top)
        x = 20 + i * 44
        bars.append(
            f'<rect x="{x}" y="{180 - height}" width="36" height="{height}" fill="#5b6cff">'
            f'<title>{html.escape(w["WEEK"])} {html.escape(w["PRODUCT_LINE"])}: {w["REVENUE"]}</title></rect>'
            f'<text x="{x + 18}" y="196" font-size="9" text-anchor="middle">{html.escape(w["PRODUCT_LINE"][:1])}</text>'
        )
    width = 40 + 44 * max(len(weeks), 1)
    page = f"""<!doctype html><meta charset="utf-8"><title>Sales Credit Monitor (simulation)</title>
<body style="font-family:sans-serif;max-width:720px;margin:2em auto">
<h1>Sales Credit Monitor</h1><p><em>Simulation of the Power BI report, not Power BI.</em></p>
<p><strong>Orders</strong> {orders} | <strong>Revenue</strong> {revenue} EUR |
<strong>Active Customers</strong> {customers} | <strong>Revenue per Customer</strong> {per_customer}</p>
<h2>Revenue per week and product line</h2>
<svg width="{width}" height="210" role="img" aria-label="Revenue per week">{''.join(bars)}</svg>
<p>P = PUMPS, V = VALVES. Hover a bar for week and value.</p></body>"""
    out = ROOT / "exports"
    out.mkdir(exist_ok=True)
    (out / "report.html").write_text(page, encoding="utf-8")
    print("exports/report.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
