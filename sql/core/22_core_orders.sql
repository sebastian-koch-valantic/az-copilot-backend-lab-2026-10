-- Only shipped orders of known products and of customers that may order.
DROP TABLE IF EXISTS core.orders;
CREATE TABLE core.orders AS
SELECT o.ORDER_ID, o.PRODUCT_ID, o.CUSTOMER_ID, o.AMOUNT_EUR,
       substr(o.ORDERED_AT, 1, 10) AS ORDER_DATE
FROM stg.orders o
JOIN core.products  p ON p.PRODUCT_ID  = o.PRODUCT_ID
JOIN core.customers c ON c.CUSTOMER_ID = o.CUSTOMER_ID
WHERE o.SHIPPED = 1;
