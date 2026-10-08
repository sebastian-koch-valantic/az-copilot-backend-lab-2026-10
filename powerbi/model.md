# Power BI model: Sales Credit Monitor (simulated)

The real model is not in this repo. This file documents what it reads and how, so an agent can
keep the SQL marts and the model in sync. Source: CSV files from `scripts/export_powerbi.py`.

## Tables

| Power BI table | Mart table | Grain | Key |
|---|---|---|---|
| DimProduct | `mart.dim_product` | one row per active product | PRODUCT_ID |
| DimCustomer | `mart.dim_customer` | one row per customer without credit block | CUSTOMER_ID |
| FactOrders | `mart.fact_orders` | one row per shipped order | ORDER_ID |

## Relationships

- FactOrders[PRODUCT_ID] many-to-one DimProduct[PRODUCT_ID]
- FactOrders[CUSTOMER_ID] many-to-one DimCustomer[CUSTOMER_ID]

## Measures (DAX)

```dax
Orders = COUNTROWS ( FactOrders )
Revenue = SUM ( FactOrders[AMOUNT_EUR] )
Active Customers = DISTINCTCOUNT ( FactOrders[CUSTOMER_ID] )
Revenue per Customer = DIVIDE ( [Revenue], [Active Customers] )
```

## Lineage

```text
src.products, src.customers, src.orders
  -> stg.* -> core.products, core.customers, core.orders
  -> mart.dim_product, mart.dim_customer, mart.fact_orders
  -> CSV export -> DimProduct, DimCustomer, FactOrders
```

## Preview without Power BI

`uv run scripts/render_report.py` writes `exports/report.html`: a static simulation of the report
(measures recomputed in Python, revenue bars as SVG). It does not test DAX or filter context.

## Rule

Every change to a mart table that adds, renames or removes a column also changes this file.
