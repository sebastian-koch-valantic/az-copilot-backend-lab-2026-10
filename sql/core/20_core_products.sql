-- CORE: cleaned and conformed. Discontinued products never leave this layer.
DROP TABLE IF EXISTS core.products;
CREATE TABLE core.products AS
SELECT PRODUCT_ID,
       TRIM(PRODUCT_NAME)  AS PRODUCT_NAME,
       UPPER(PRODUCT_LINE) AS PRODUCT_LINE,
       SALES_CHANNEL, LISTED_FROM, LISTED_TO
FROM stg.products
WHERE STATUS = 'ACTIVE';
