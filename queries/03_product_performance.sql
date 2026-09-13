-- Category-level revenue, margin, and return rate.
-- Margin = (selling_price - cost_price) / selling_price at the product level,
-- then averaged by revenue weight across the category.

WITH item_level AS (
    SELECT
        p.category,
        p.product_id,
        p.name                                          AS product_name,
        SUM(i.quantity)                                 AS units_sold,
        ROUND(SUM(i.quantity * i.unit_price), 2)        AS revenue,
        ROUND(SUM(i.quantity * p.cost_price), 2)        AS cost,
        ROUND(SUM(i.quantity * (i.unit_price - p.cost_price)), 2) AS gross_profit
    FROM '{order_items}' i
    JOIN '{products}' p   USING (product_id)
    JOIN '{orders}' o     USING (order_id)
    WHERE o.status = 'delivered'
    GROUP BY 1, 2, 3
),
returns AS (
    SELECT
        p.category,
        COUNT(DISTINCT o.order_id) AS returned_orders
    FROM '{orders}' o
    JOIN '{order_items}' i USING (order_id)
    JOIN '{products}' p    USING (product_id)
    WHERE o.status = 'returned'
    GROUP BY 1
),
delivered_totals AS (
    SELECT
        p.category,
        COUNT(DISTINCT o.order_id) AS delivered_orders
    FROM '{orders}' o
    JOIN '{order_items}' i USING (order_id)
    JOIN '{products}' p    USING (product_id)
    WHERE o.status = 'delivered'
    GROUP BY 1
)
SELECT
    il.category,
    SUM(il.units_sold)                                            AS units_sold,
    SUM(il.revenue)                                               AS revenue,
    SUM(il.gross_profit)                                          AS gross_profit,
    ROUND(SUM(il.gross_profit) / NULLIF(SUM(il.revenue), 0) * 100, 1) AS margin_pct,
    COALESCE(r.returned_orders, 0)                                AS returned_orders,
    dt.delivered_orders,
    ROUND(COALESCE(r.returned_orders, 0) * 100.0 / NULLIF(dt.delivered_orders, 0), 1) AS return_rate_pct
FROM item_level il
LEFT JOIN returns r         ON il.category = r.category
LEFT JOIN delivered_totals dt ON il.category = dt.category
GROUP BY il.category, r.returned_orders, dt.delivered_orders
ORDER BY revenue DESC;
