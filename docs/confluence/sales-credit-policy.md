# Sales credit policy (simulated Confluence page)

## Why
Sales must not ship to customers who exceed their credit exposure, whatever product line or
channel the orders come through.

## Rules
- The shipped order value of a customer in any rolling 30 days must not exceed the customer's
  credit limit (CREDIT_LIMIT_EUR), summed across all product lines and sales channels.
- Customers with a credit block never appear in reporting.
- A sales manager can request an exception for one customer, approved by Credit Management.
- Orders of discontinued products are not part of the check.

## Reporting
- The Power BI report "Sales Credit Monitor" shows the check per week.
- Credit Management reviews the report every Monday.
- Customers above the limit are listed with their orders, never with more than the customer id and segment.
