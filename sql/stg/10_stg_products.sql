-- STG: raw copy of the source table plus the load timestamp. No business logic here.
DROP TABLE IF EXISTS stg.products;
CREATE TABLE stg.products AS
SELECT PRODUCT_ID, PRODUCT_NAME, PRODUCT_LINE, SALES_CHANNEL, LISTED_FROM, LISTED_TO, STATUS,
       datetime('now') AS LOADED_AT  -- Oracle: SYSTIMESTAMP
FROM src.products;
