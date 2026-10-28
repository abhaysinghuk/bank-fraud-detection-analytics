# Bank Fraud Detection Analytics Project
## Phase 8: Insights

### 1. Overall Fraud Signal Rate
9.16% of transactions (230 of 2,512) show at least one statistical fraud signal (unusual amount, login attempts, or duration). Of these, 5 transactions triggered two signals simultaneously — these represent the highest-confidence leads for manual fraud investigation, since they are unusual across more than one independent measure.

### 2. Geographic Concentration
Austin, Fort Worth, and San Diego show the highest suspicious transaction *rates* (15.25%, 14.29%, and 13.56% respectively) — meaningfully above the 9.16% dataset-wide baseline, even after correcting for transaction volume. This rules out "these cities just have more transactions" as an explanation and points to a genuinely elevated risk pattern worth targeted investigation.

### 3. Time of Day Is a Weak Signal
Suspicious rates by hour ranged narrowly from 8.75% to 9.40% across the three hours present in the data — not a meaningful difference. This is a useful negative finding: it means fraud investigators should not prioritize time-of-day as a red flag in this dataset, avoiding wasted effort on a weak indicator.

### 4. LoginAttempts Signal Has a Known Limitation
The IQR method for LoginAttempts produced collapsed bounds (both Q1 and Q3 equal to 1), causing over-sensitive flagging — any transaction with 2+ login attempts was flagged, even though this is common, non-fraudulent behavior. This signal should be treated as lower-confidence than the Amount outlier signal, or recalibrated with a higher manual threshold (e.g., 3+ attempts) in future iterations.

### 5. Fraud Signals Rarely Compound
No single transaction triggered all three risk signals (Amount, LoginAttempts, Duration) simultaneously — the maximum was 2 out of 3. This suggests that in this dataset, suspicious activity tends to show up as one or two red flags rather than an obviously extreme case, mirroring how real-world fraud is often subtle rather than glaring.

### 6. Account-Level Risk Accumulation Matters
Certain accounts (e.g., AC00071, AC00456) show risk points accumulating across multiple transactions even when no single transaction was extreme. This indicates that account-level monitoring (tracking patterns across a customer's full transaction history) may catch risk that transaction-by-transaction review would miss.

### Cross-Validation Note
All headline figures (230 suspicious transactions, 9.16% suspicious rate, 113 amount outliers) were independently reproduced across Python, SQL, Excel, and Power BI, adding confidence that these findings reflect the underlying data rather than a tool-specific error.
