"""The pipeline definition: which SQL file builds which table, and what it depends on.

Python only orchestrates. Every transformation lives in a SQL file under sql/.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict


class Step(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    layer: Literal["STG", "CORE", "MART"]
    sql_file: str  # relative to sql/
    target: str  # schema.table the step builds (used for the row count)
    depends_on: tuple[str, ...] = ()


STEPS: tuple[Step, ...] = (
    Step(name="stg_products", layer="STG", sql_file="stg/10_stg_products.sql", target="stg.products"),
    Step(name="stg_customers", layer="STG", sql_file="stg/11_stg_customers.sql", target="stg.customers"),
    Step(name="stg_orders", layer="STG", sql_file="stg/12_stg_orders.sql", target="stg.orders"),
    Step(name="core_products", layer="CORE", sql_file="core/20_core_products.sql", target="core.products", depends_on=("stg_products",)),
    Step(name="core_customers", layer="CORE", sql_file="core/21_core_customers.sql", target="core.customers", depends_on=("stg_customers",)),
    Step(name="core_orders", layer="CORE", sql_file="core/22_core_orders.sql", target="core.orders", depends_on=("stg_orders", "core_products", "core_customers")),
    Step(name="mart_dim_product", layer="MART", sql_file="mart/30_dim_product.sql", target="mart.dim_product", depends_on=("core_products",)),
    Step(name="mart_dim_customer", layer="MART", sql_file="mart/31_dim_customer.sql", target="mart.dim_customer", depends_on=("core_customers",)),
    Step(name="mart_fact_orders", layer="MART", sql_file="mart/32_fact_orders.sql", target="mart.fact_orders", depends_on=("core_orders", "mart_dim_product", "mart_dim_customer")),
)


def by_name() -> dict[str, Step]:
    return {step.name: step for step in STEPS}
