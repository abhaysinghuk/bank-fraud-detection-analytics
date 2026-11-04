-- Fraud Transaction Pattern Analysis

-- Overall fraud summary
SELECT
    COUNT(*)                                              AS total_transactions,
    SUM(is_flagged)                                       AS flagged_count,
    ROUND(SUM(is_flagged) * 100.0 / COUNT(*), 2)         AS fraud_rate_pct,
    ROUND(SUM(CASE WHEN is_flagged=1 THEN amount END), 2) AS flagged_amount,
    ROUND(AVG(CASE WHEN is_flagged=1 THEN amount END), 2) AS avg_fraud_amount
FROM transactions;

-- Fraud by channel
SELECT
    channel,
    COUNT(*) AS total,
    SUM(is_flagged) AS flagged,
    ROUND(SUM(is_flagged)*100.0/COUNT(*), 2) AS fraud_rate_pct,
    ROUND(AVG(CASE WHEN is_flagged=1 THEN amount END), 2) AS avg_fraud_amount
FROM transactions
GROUP BY channel
ORDER BY fraud_rate_pct DESC;

-- Fraud by hour of day (time-of-day pattern)
SELECT
    CAST(SUBSTR(txn_time, 1, 2) AS INTEGER) AS hour,
    COUNT(*) AS total,
    SUM(is_flagged) AS flagged,
    ROUND(SUM(is_flagged)*100.0/COUNT(*), 2) AS fraud_rate_pct
FROM transactions
GROUP BY hour
ORDER BY hour;

-- Fraud by merchant category
SELECT
    merchant_category,
    COUNT(*) AS total,
    SUM(is_flagged) AS flagged,
    ROUND(SUM(is_flagged)*100.0/COUNT(*), 2) AS fraud_rate_pct,
    ROUND(SUM(CASE WHEN is_flagged=1 THEN amount END), 2) AS total_fraud_amount
FROM transactions
WHERE merchant_category IS NOT NULL
GROUP BY merchant_category
ORDER BY total_fraud_amount DESC;

-- Velocity fraud: customers with > 5 transactions in a single day
SELECT
    c.customer_id, c.name, t.txn_date,
    COUNT(*) AS txn_count,
    ROUND(SUM(t.amount), 2) AS daily_total,
    SUM(t.is_flagged) AS flagged
FROM transactions t
JOIN customers c ON t.customer_id = c.id
GROUP BY c.id, t.txn_date
HAVING txn_count > 5
ORDER BY txn_count DESC LIMIT 20;

-- Window function: running fraud rate per month
SELECT
    strftime('%Y-%m', txn_date) AS month,
    COUNT(*) AS total,
    SUM(is_flagged) AS flagged,
    ROUND(SUM(is_flagged)*100.0/COUNT(*), 2) AS monthly_fraud_rate,
    ROUND(AVG(SUM(is_flagged)*100.0/COUNT(*)) OVER (
        ORDER BY strftime('%Y-%m', txn_date)
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2) AS rolling_3m_fraud_rate
FROM transactions
GROUP BY month
ORDER BY month;
