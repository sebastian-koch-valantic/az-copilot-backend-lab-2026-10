-- MART: tables the Power BI model reads. See powerbi/model.md.
DROP TABLE IF EXISTS mart.dim_product;
CREATE TABLE mart.dim_product AS
SELECT PRODUCT_ID, PRODUCT_NAME, PRODUCT_LINE, SALES_CHANNEL, LISTED_FROM, LISTED_TO
FROM core.products;
