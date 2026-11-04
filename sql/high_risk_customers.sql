-- High-Risk Customer Identification

-- Risk score distribution
SELECT
    risk_label,
    COUNT(*) AS customers,
    ROUND(AVG(risk_score), 2) AS avg_score,
    SUM(velocity_flag)   AS velocity_flags,
    SUM(large_txn_flag)  AS large_txn_flags,
    SUM(odd_hour_flag)   AS odd_hour_flags,
    SUM(multi_city_flag) AS multi_city_flags
FROM risk_scores
GROUP BY risk_label
ORDER BY avg_score DESC;

-- Top 20 highest risk customers
SELECT
    c.customer_id, c.name, c.city, c.account_type,
    c.credit_score, c.account_balance,
    r.risk_score, r.risk_label,
    r.velocity_flag, r.large_txn_flag, r.odd_hour_flag, r.multi_city_flag,
    COUNT(t.id) AS total_txns,
    SUM(t.is_flagged) AS flagged_txns,
    ROUND(SUM(t.amount), 2) AS total_txn_volume
FROM risk_scores r
JOIN customers c ON r.customer_id = c.id
LEFT JOIN transactions t ON t.customer_id = c.id
GROUP BY c.id
ORDER BY r.risk_score DESC LIMIT 20;

-- High risk customers by branch
SELECT
    b.name AS branch, b.city,
    COUNT(DISTINCT c.id) AS total_customers,
    COUNT(DISTINCT CASE WHEN r.risk_label IN ('High','Critical') THEN c.id END) AS high_risk_count,
    ROUND(COUNT(DISTINCT CASE WHEN r.risk_label IN ('High','Critical') THEN c.id END) * 100.0
          / COUNT(DISTINCT c.id), 1) AS high_risk_pct
FROM branches b
JOIN customers c ON c.branch_id = b.id
LEFT JOIN risk_scores r ON r.customer_id = c.id
GROUP BY b.id
ORDER BY high_risk_pct DESC;

-- Credit score vs fraud correlation (bucketed)
SELECT
    CASE
        WHEN credit_score < 550 THEN 'Very Poor (<550)'
        WHEN credit_score < 650 THEN 'Poor (550-649)'
        WHEN credit_score < 750 THEN 'Fair (650-749)'
        WHEN credit_score < 800 THEN 'Good (750-799)'
        ELSE 'Excellent (800+)'
    END AS credit_band,
    COUNT(DISTINCT c.id) AS customers,
    ROUND(AVG(t.is_flagged)*100, 2) AS fraud_rate_pct,
    ROUND(AVG(c.account_balance), 2) AS avg_balance
FROM customers c
JOIN transactions t ON t.customer_id = c.id
GROUP BY credit_band
ORDER BY fraud_rate_pct DESC;

-- Window: customer percentile ranking by fraud exposure
SELECT
    c.customer_id, c.name,
    COUNT(t.id) AS txn_count,
    SUM(t.is_flagged) AS fraud_count,
    ROUND(SUM(t.is_flagged)*100.0/COUNT(t.id), 2) AS fraud_pct,
    NTILE(100) OVER (ORDER BY SUM(t.is_flagged)*100.0/COUNT(t.id)) AS fraud_percentile
FROM customers c
JOIN transactions t ON t.customer_id = c.id
GROUP BY c.id
HAVING txn_count >= 10
ORDER BY fraud_pct DESC LIMIT 20;
