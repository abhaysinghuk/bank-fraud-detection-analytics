# bank-fraud-detection-analytics

Banking Risk & Fraud Analytics
Fraud detection and financial risk analytics — suspicious transaction patterns, high-risk customer identification, and daily monitoring dashboards built with SQL · Python · Power BI · Machine Learning.

Dataset: 5,000 customers · 10 branches · 61,111 transactions · 2,444 fraud cases · 2023–2024

Executive Summary (sample run)
Metric	Value
Total Customers	5,000
Branches	10
Total Transactions	61,111
Fraud Flagged	2,444 (4.0%)
Fraud Exposure	₹90.99 Lakhs
Total Transaction Volume	₹134.7 Crore
Avg Transaction Amount	₹22,037
Fraud Cases Filed	326
Alert Days (fraud >5%)	194 days
Warning Days (fraud 3–5%)	288 days
ML Anomalies (Isolation Forest)	2,445
New ML-only Catches	2,336 (not caught by rules)
What's Inside
Module	Files	Description
sql/	5 files	Schema + 4 analytical query sets with window functions
python/	6 files	Data generator + 4 analysis scripts + master runner
notebooks/	1 notebook	9-section Jupyter EDA with ML
powerbi/	1 guide	4-page dashboard + 15 DAX measures
reports/	11 charts + HTML + 2 CSVs	Full analysis output
Key Analyses & Outputs
Fraud Transaction Patterns
Fraud Rate by Channel:

Channel	Fraud Rate	Avg Fraud Amount
Online	6.49%	₹21,840
ATM	4.21%	₹19,520
Mobile	2.98%	₹20,310
POS	2.05%	₹18,750
Branch	1.02%	₹23,100
Fraud Overview

Time-of-Day Risk: Transactions between 10pm–4am show 2x higher fraud rates

Hourly Fraud Pattern

Fraud by Merchant Category:

Merchant Fraud

Fraud Case Resolution:

Fraud Cases

High-Risk Customer Identification
Risk Score Distribution:

Risk Label	Customers	%
Low	4,131	82.6%
Medium	863	17.3%
High	6	0.1%
Critical	0	0.0%
Risk flags tracked per customer: Velocity (>8 txns/day) · Large Transaction (>₹1L) · Odd Hours (>25% at night) · Multi-City (>5 cities)

Risk Distribution

Credit Score vs Fraud

Branch Risk Heatmap:

Branch Risk Heatmap

Daily Transaction Monitoring
194 Alert Days where fraud rate exceeded 5% threshold
288 Warning Days where fraud rate was in the 3–5% range
1,359 Z-score anomalies (transactions >2.5 standard deviations above mean)
Daily Monitoring

Z-Score Anomalies

Branch × Month Fraud Heatmap:

Branch Monitoring

ML Anomaly Detection (Isolation Forest)
2,445 anomalies detected (4.0% contamination rate)
2,336 new catches not flagged by rule-based approach
Features used: amount, hour, channel, transaction type, day of week, credit score, balance
Anomaly Detection

Quick Start
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate synthetic dataset
python3 python/data_generator.py
# → 61,111 transactions, 4.0% fraud rate, full SQLite DB + CSVs

# 3. Run full analysis + ML detection
python3 python/analysis.py

# 4. Open HTML report
open reports/report.html

# 5. Launch Jupyter notebook
jupyter notebook notebooks/banking_fraud_analysis.ipynb
Project Structure
banking-risk-fraud-analytics/
├── data/
│   ├── branches.csv          10 bank branches across cities
│   ├── customers.csv         5,000 customers with credit scores
│   ├── transactions.csv      61,111 transactions (2023–2024)
│   ├── fraud_cases.csv       326 formal fraud case records
│   ├── risk_scores.csv       Risk scores for all 5,000 customers
│   └── banking.db            SQLite database
│
├── sql/
│   ├── schema.sql            Table definitions + 7 indexes
│   ├── fraud_patterns.sql    Channel fraud, hourly patterns, velocity checks, rolling rates
│   ├── high_risk_customers.sql  Risk distribution, credit bands, branch risk, NTILE ranking
│   ├── transaction_monitoring.sql  Daily KPIs with alerts, rolling averages, peer comparison
│   └── window_analytics.sql  Running totals, LAG/LEAD MoM, DENSE_RANK, NTILE buckets
│
├── python/
│   ├── data_generator.py     Fraud injection with channel/hour probability weights
│   ├── fraud_analysis.py     Channel risk, hourly patterns, merchant fraud, case analysis
│   ├── risk_scoring.py       Risk distribution, credit-fraud correlation, branch heatmap
│   ├── transaction_monitoring.py  Daily KPI dashboard, Z-score anomalies, branch heatmap
│   ├── anomaly_detection.py  Isolation Forest ML model + rule-based comparison
│   └── analysis.py           Master runner + HTML report generator
│
├── notebooks/
│   └── banking_fraud_analysis.ipynb  9-section EDA with ML anomaly detection
│
├── powerbi/
│   └── setup_guide.md        4-page dashboard setup + 15 DAX measures
│
├── reports/
│   ├── report.html           Auto-generated HTML executive report
│   ├── high_risk_customers.csv  High/Critical risk customer export
│   ├── ml_anomalies.csv      Top 500 ML-detected anomalies
│   └── *.png                 11 analysis charts
│
└── requirements.txt
Power BI Dashboard
The powerbi/setup_guide.md covers a 4-page fraud monitoring dashboard:

Page	Visuals
Executive Fraud Overview	KPI cards, monthly fraud rate line, channel bar, case status donut
Transaction Monitoring	Daily volume + rolling avg, conditional fraud bar, branch×month heatmap
High-Risk Customers	Risk label donut, top-20 risk table, branch heatmap, credit band bar
Fraud Case Analysis	Loss by fraud type, case table, merchant fraud bar, hour×fraud scatter
15 DAX Measures: Total Transactions · Fraud Count · Fraud Rate % · Fraud Exposure · Avg Transaction · High Risk Customers · High Risk % · Total Amount Lost · Fraud Cases Confirmed · Avg Resolution Days · Fraud Rate MoM Change % · Night Hour Fraud % · Velocity Risk Customers · Avg Risk Score · Fraud Detection Recall %

Stack
Tool	Purpose
SQLite	Portable database — queries use window functions (LAG, NTILE, DENSE_RANK)
pandas + numpy	Data wrangling and statistical computation
scikit-learn	Isolation Forest for ML-based anomaly detection
matplotlib + seaborn	11 publication-quality charts
Power BI Desktop	Interactive 4-page fraud monitoring dashboard
Jupyter	9-section EDA notebook with ML
