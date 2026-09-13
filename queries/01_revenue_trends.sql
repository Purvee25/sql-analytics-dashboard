-- Monthly revenue with month-over-month growth rate.
-- Only counts delivered orders to avoid inflating with cancellations.

WITH monthly AS (
    SELECT
        DATE_TRUNC('month', o.order_date::DATE)   AS month,
        ROUND(SUM(i.quantity * i.unit_price), 2)  AS revenue,
        COUNT(DISTINCT o.order_id)                AS orders,
        COUNT(DISTINCT o.customer_id)             AS unique_customers
    FROM '{orders}' o
    JOIN '{order_items}' i USING (order_id)
    WHERE o.status = 'delivered'
    GROUP BY 1
)
SELECT
    month,
    revenue,
    orders,
    unique_customers,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY month))
        / NULLIF(LAG(revenue) OVER (ORDER BY month), 0) * 100,
        1
    ) AS mom_growth_pct
FROM monthly
ORDER BY month;
