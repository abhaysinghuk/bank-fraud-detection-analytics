# Bank Fraud Detection Analytics Project
## Phase 9: Recommendations

Based on the insights in Phase 8, the following actions are recommended:

1. **Prioritize the 5 double-flagged transactions** for immediate manual review — these are the highest-confidence fraud leads, having triggered two independent statistical signals simultaneously.

2. **Increase monitoring intensity in Austin, Fort Worth, and San Diego.** These cities show suspicious rates meaningfully above the dataset-wide baseline even after correcting for transaction volume, suggesting a genuine elevated risk pattern worth targeted attention.

3. **Deprioritize time-of-day as a standalone fraud rule.** The data showed only a marginal difference in suspicious rate across hours (8.75%–9.40%), so alerting logic and investigator time are better spent on stronger signals.

4. **Recalibrate the LoginAttempts threshold** from flagging any deviation to a stricter rule (e.g., 3+ attempts) before using it as an automated flag. The current threshold produces excessive false positives due to low variance in normal customer behavior.

5. **Treat multi-signal transactions as escalation triggers.** A simple tiered rule is recommended: 1 signal detected → log for periodic review; 2+ signals detected → immediate hold and escalate to a fraud investigator.

6. **Implement account-level risk scoring, not just transaction-level review.** Some accounts accumulate risk across multiple individually-unremarkable transactions. Tracking cumulative risk points per account over a rolling window (e.g., 30 days) could catch slow-building risk patterns that transaction-by-transaction review would miss.
