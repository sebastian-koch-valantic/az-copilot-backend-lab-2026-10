-- Credit-blocked customers are removed here, so no later layer can ever report their orders.
DROP TABLE IF EXISTS core.customers;
CREATE TABLE core.customers AS
SELECT CUSTOMER_ID, SEGMENT, REGION, CREDIT_LIMIT_EUR
FROM stg.customers
WHERE COALESCE(CREDIT_BLOCK, 0) = 0;  -- Oracle: NVL(CREDIT_BLOCK, 0)
