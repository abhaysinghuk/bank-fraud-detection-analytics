-- Advanced Window Function Analytics

-- Running total and cumulative fraud rate per customer
SELECT
    c.customer_id,
    t.txn_date,
    t.txn_id,
    t.amount,
    t.is_flagged,
    SUM(t.amount) OVER (PARTITION BY c.id ORDER BY t.txn_date, t.id) AS running_total,
    COUNT(*) OVER (PARTITION BY c.id ORDER BY t.txn_date, t.id) AS txn_number,
    SUM(t.is_flagged) OVER (PARTITION BY c.id ORDER BY t.txn_date, t.id) AS cumulative_flags,
    ROUND(
        SUM(t.is_flagged) OVER (PARTITION BY c.id ORDER BY t.txn_date, t.id) * 100.0
        / COUNT(*) OVER (PARTITION BY c.id ORDER BY t.txn_date, t.id)
    , 2) AS cumulative_fraud_pct
FROM transactions t
JOIN customers c ON t.customer_id = c.id
ORDER BY c.id, t.txn_date, t.id
LIMIT 500;

-- Month-over-month transaction volume change per branch
WITH monthly AS (
    SELECT
        c.branch_id,
        strftime('%Y-%m', t.txn_date) AS month,
        COUNT(*) AS txns,
        ROUND(SUM(t.amount), 2) AS volume
    FROM transactions t
    JOIN customers c ON t.customer_id = c.id
    GROUP BY c.branch_id, month
)
SELECT
    b.name AS branch,
    m.month,
    m.txns,
    m.volume,
    LAG(m.volume) OVER (PARTITION BY m.branch_id ORDER BY m.month) AS prev_month_volume,
    ROUND(
        (m.volume - LAG(m.volume) OVER (PARTITION BY m.branch_id ORDER BY m.month))
        / LAG(m.volume) OVER (PARTITION BY m.branch_id ORDER BY m.month) * 100
    , 1) AS mom_growth_pct
FROM monthly m
JOIN branches b ON b.id = m.branch_id
ORDER BY b.name, m.month;

-- Top-N transactions per customer (dense rank)
SELECT *
FROM (
    SELECT
        c.customer_id, c.name,
        t.txn_date, t.amount, t.channel, t.is_flagged,
        DENSE_RANK() OVER (PARTITION BY t.customer_id ORDER BY t.amount DESC) AS amount_rank
    FROM transactions t
    JOIN customers c ON t.customer_id = c.id
) ranked
WHERE amount_rank <= 3
ORDER BY customer_id, amount_rank
LIMIT 100;

-- Transaction amount percentile buckets (NTILE)
SELECT
    txn_bucket,
    COUNT(*) AS txns,
    ROUND(MIN(amount), 2) AS min_amount,
    ROUND(MAX(amount), 2) AS max_amount,
    ROUND(AVG(amount), 2) AS avg_amount,
    SUM(is_flagged) AS frauds,
    ROUND(SUM(is_flagged)*100.0/COUNT(*), 2) AS fraud_rate_pct
FROM (
    SELECT amount, is_flagged,
           NTILE(10) OVER (ORDER BY amount) AS txn_bucket
    FROM transactions
)
GROUP BY txn_bucket
ORDER BY txn_bucket;
