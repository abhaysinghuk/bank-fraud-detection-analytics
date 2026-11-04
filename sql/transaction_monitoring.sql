-- Daily Transaction Monitoring Dashboard

-- Daily KPIs with threshold alerts
SELECT
    txn_date AS date,
    COUNT(*) AS total_txns,
    ROUND(SUM(amount), 2) AS total_volume,
    ROUND(AVG(amount), 2) AS avg_txn_amount,
    SUM(is_flagged) AS flagged_count,
    ROUND(SUM(is_flagged)*100.0/COUNT(*), 2) AS fraud_rate_pct,
    ROUND(MAX(amount), 2) AS max_txn,
    CASE
        WHEN SUM(is_flagged)*100.0/COUNT(*) > 5  THEN 'ALERT'
        WHEN SUM(is_flagged)*100.0/COUNT(*) > 3  THEN 'WARNING'
        ELSE 'NORMAL'
    END AS status
FROM transactions
GROUP BY txn_date
ORDER BY txn_date;

-- 7-day rolling average transaction volume
SELECT
    txn_date,
    COUNT(*) AS daily_txns,
    ROUND(SUM(amount), 2) AS daily_volume,
    ROUND(AVG(SUM(amount)) OVER (
        ORDER BY txn_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 2) AS rolling_7d_avg,
    ROUND(AVG(COUNT(*)) OVER (
        ORDER BY txn_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 0) AS rolling_7d_txn_avg
FROM transactions
GROUP BY txn_date
ORDER BY txn_date;

-- Peer comparison: customer vs branch average (window function)
SELECT
    c.customer_id, c.name, b.name AS branch,
    COUNT(t.id) AS txn_count,
    ROUND(AVG(t.amount), 2) AS customer_avg_txn,
    ROUND(AVG(AVG(t.amount)) OVER (PARTITION BY c.branch_id), 2) AS branch_avg_txn,
    ROUND(AVG(t.amount) - AVG(AVG(t.amount)) OVER (PARTITION BY c.branch_id), 2) AS deviation_from_branch
FROM transactions t
JOIN customers c ON t.customer_id = c.id
JOIN branches b ON c.branch_id = b.id
GROUP BY c.id
ORDER BY ABS(deviation_from_branch) DESC LIMIT 20;

-- Large transaction alerts (>3 std deviations from mean)
WITH stats AS (
    SELECT AVG(amount) AS mean_amt, AVG(amount*amount) - AVG(amount)*AVG(amount) AS variance
    FROM transactions WHERE is_flagged = 0
)
SELECT
    t.txn_id, c.customer_id, c.name, t.txn_date, t.txn_time,
    t.amount, t.channel, t.merchant_category, t.is_flagged,
    ROUND((t.amount - s.mean_amt) / SQRT(s.variance), 2) AS z_score
FROM transactions t
JOIN customers c ON t.customer_id = c.id
CROSS JOIN stats s
WHERE (t.amount - s.mean_amt) / SQRT(s.variance) > 3
ORDER BY z_score DESC LIMIT 25;

-- Branch-level daily monitoring
SELECT
    b.name AS branch, b.city,
    t.txn_date,
    COUNT(*) AS txns,
    ROUND(SUM(t.amount), 2) AS volume,
    SUM(t.is_flagged) AS flagged,
    ROUND(SUM(t.is_flagged)*100.0/COUNT(*), 2) AS fraud_rate_pct
FROM transactions t
JOIN customers c ON t.customer_id = c.id
JOIN branches b ON c.branch_id = b.id
GROUP BY b.id, t.txn_date
ORDER BY t.txn_date DESC, fraud_rate_pct DESC;
