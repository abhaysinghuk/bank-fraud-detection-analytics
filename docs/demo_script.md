# Demo Script: Bank Fraud Detection Project
(Aim for 3-5 minutes)

## 1. The hook (15-20 seconds)
"Banks typically catch fraud manually, after the damage is done. I built a project that analyzes transaction data and flags suspicious activity automatically — and I did it on a dataset that had no fraud labels at all, so I had to design my own detection logic from scratch."

## 2. The challenge (20-30 seconds)
"The dataset I found on Kaggle had rich transaction data — amount, location, device, login attempts — but no 'is this fraud' answer key. So instead of switching to an easier dataset, I built a statistical risk-scoring system using outlier detection, similar to how a real fraud team might approach messy, unlabeled data."

## 3. Show the Python work (30-45 seconds)
[Screen: phase3_cleaning.py output or fraud_data_cleaned.csv]
"I used the IQR method to flag unusual transaction amounts, login attempts, and durations, then combined them into a single Fraud Risk Score from 0 to 3. Two hundred thirty transactions — about 9% — triggered at least one signal."

## 4. Show the SQL work (20-30 seconds)
[Screen: pgAdmin query results]
"I moved the data into PostgreSQL and wrote queries to rank the riskiest accounts and merchants — the kind of query a bank's actual fraud team would run daily."

## 5. Show the dashboard (60-90 seconds — the centerpiece)
[Screen: Power BI dashboard]
"This is the interactive dashboard — you can see the overall fraud rate, the highest-risk cities, a monthly trend, and a table of the riskiest accounts. I built this with DAX measures rather than hardcoded numbers, so it updates live if the underlying data changes. [Click the Channel slicer] — and it's fully interactive, so a fraud analyst could filter by channel or drill into a specific city."

## 6. The key insight (20-30 seconds)
"The most interesting finding was actually a mistake I caught and fixed: my first pass showed one city with the most flagged transactions, but that was just because it had more transactions overall. Once I corrected for volume, a completely different city turned out to be the real outlier by rate. That taught me to never trust a raw count without checking the denominator."

## 7. Close (10-15 seconds)
"Everything here — the Python scores, SQL rankings, Excel pivot tables, and Power BI dashboard — all produce the exact same numbers, which I used as a way to validate my own work. Happy to walk through any part of it in more detail."

---
## Tips for delivery
- Practice the dashboard section most — it's the visual centerpiece and where people's attention peaks
- If asked a question you don't know, it's fine to say "I'd want to dig into that further" rather than guessing — this is more credible than overclaiming
- Keep a backup: screenshots of the dashboard in case live software isn't available during the interview
