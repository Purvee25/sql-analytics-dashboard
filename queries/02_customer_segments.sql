-- RFM-lite customer segmentation.
-- Recency: days since last order. Frequency: order count. Monetary: total spend.
-- Segments customers into Champions, Loyal, At-Risk, and Lost.

WITH rfm AS (
    SELECT
        o.customer_id,
        c.segment                                                  AS biz_segment,
        c.state,
        DATE_DIFF('day', MAX(o.order_date::DATE), DATE '2024-12-31') AS recency_days,
        COUNT(DISTINCT o.order_id)                                 AS frequency,
        ROUND(SUM(i.quantity * i.unit_price), 2)                   AS monetary
    FROM '{orders}' o
    JOIN '{order_items}' i USING (order_id)
    JOIN '{customers}' c   USING (customer_id)
    WHERE o.status = 'delivered'
    GROUP BY 1, 2, 3
),
scored AS (
    SELECT *,
        NTILE(4) OVER (ORDER BY recency_days ASC)  AS r_score,   -- lower recency → higher score
        NTILE(4) OVER (ORDER BY frequency    DESC) AS f_score,
        NTILE(4) OVER (ORDER BY monetary     DESC) AS m_score
    FROM rfm
)
SELECT
    customer_id,
    biz_segment,
    state,
    recency_days,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    CASE
        WHEN r_score >= 3 AND f_score >= 3              THEN 'Champion'
        WHEN r_score >= 3 AND f_score BETWEEN 1 AND 2   THEN 'Promising'
        WHEN r_score BETWEEN 2 AND 3 AND f_score >= 3   THEN 'Loyal'
        WHEN r_score = 2 AND f_score = 2                THEN 'Needs Attention'
        WHEN r_score <= 2 AND f_score >= 3              THEN 'At-Risk'
        ELSE                                                 'Lost'
    END AS rfm_label
FROM scored
ORDER BY monetary DESC;
