-- Seller SLA compliance: on-time delivery rate and average delay by seller tier.

WITH delivery_stats AS (
    SELECT
        o.seller_id,
        s.name          AS seller_name,
        s.tier,
        s.city,
        COUNT(*)                                                    AS delivered_orders,
        SUM(
            CASE WHEN o.actual_delivery::DATE <= o.promised_delivery::DATE THEN 1 ELSE 0 END
        )                                                           AS on_time,
        ROUND(AVG(
            DATE_DIFF('day', o.promised_delivery::DATE, o.actual_delivery::DATE)
        ), 1)                                                       AS avg_delay_days
    FROM '{orders}' o
    JOIN '{sellers}' s USING (seller_id)
    WHERE o.status = 'delivered'
      AND o.actual_delivery IS NOT NULL
    GROUP BY 1, 2, 3, 4
)
SELECT
    seller_id,
    seller_name,
    tier,
    city,
    delivered_orders,
    on_time,
    ROUND(on_time * 100.0 / delivered_orders, 1) AS sla_pct,
    avg_delay_days
FROM delivery_stats
ORDER BY sla_pct DESC, delivered_orders DESC;
