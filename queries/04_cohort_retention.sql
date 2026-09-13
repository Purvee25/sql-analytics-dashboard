-- Monthly cohort retention.
-- Cohort = month of first purchase. Retention = % of cohort who ordered again in month N.

WITH first_order AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', MIN(order_date::DATE)) AS cohort_month
    FROM '{orders}'
    WHERE status = 'delivered'
    GROUP BY 1
),
customer_months AS (
    SELECT DISTINCT
        o.customer_id,
        DATE_TRUNC('month', o.order_date::DATE) AS order_month
    FROM '{orders}' o
    WHERE o.status = 'delivered'
),
cohort_data AS (
    SELECT
        f.cohort_month,
        DATE_DIFF('month', f.cohort_month, cm.order_month) AS month_number,
        COUNT(DISTINCT cm.customer_id)                      AS customers
    FROM first_order f
    JOIN customer_months cm USING (customer_id)
    GROUP BY 1, 2
),
cohort_sizes AS (
    SELECT cohort_month, customers AS cohort_size
    FROM cohort_data
    WHERE month_number = 0
)
SELECT
    cd.cohort_month,
    cs.cohort_size,
    cd.month_number,
    cd.customers                                                    AS retained,
    ROUND(cd.customers * 100.0 / cs.cohort_size, 1)                AS retention_pct
FROM cohort_data cd
JOIN cohort_sizes cs USING (cohort_month)
WHERE cd.month_number <= 6
ORDER BY cohort_month, month_number;
