
# Banking Risk & Fraud Analytics

An end-to-end banking fraud detection and financial risk analytics project focused on identifying suspicious transaction patterns, detecting high-risk customers, monitoring daily fraud activity, and generating actionable insights through SQL, Python, Machine Learning, and Power BI.

## Project Overview

This project analyzes banking transactions to identify potential fraudulent activities, assess customer risk, and monitor transaction patterns across multiple branches and channels.

It combines SQL-based analytics, Python data processing, statistical analysis, Isolation Forest anomaly detection, and interactive Power BI dashboard reporting.

### Dataset Overview

| Metric | Value |
|---|---:|
| Customers | 5,000 |
| Branches | 10 |
| Total Transactions | 61,111 |
| Fraud Cases Identified | 2,444 |
| Dataset Period | 2023–2024 |
| Fraud Rate | 4.0% |

## Executive Summary

The following metrics are from a sample project run.

| Metric | Value |
|---|---:|
| Total Customers | 5,000 |
| Total Branches | 10 |
| Total Transactions | 61,111 |
| Fraud Flagged | 2,444 (4.0%) |
| Fraud Exposure | ₹90.99 Lakhs |
| Total Transaction Volume | ₹134.7 Crore |
| Average Transaction Amount | ₹22,037 |
| Fraud Cases Filed | 326 |
| Alert Days (Fraud Rate > 5%) | 194 days |
| Warning Days (Fraud Rate 3–5%) | 288 days |
| ML Anomalies (Isolation Forest) | 2,445 |
| New ML-only Detections | 2,336 |

## Key Features & Analysis

### 1. Fraud Transaction Pattern Analysis

Analyzed suspicious transaction behavior across different payment channels, merchant categories, and transaction timings.

**Fraud Rate by Transaction Channel**

| Channel | Fraud Rate | Average Fraud Amount |
|---|---:|---:|
| Online | 6.49% | ₹21,840 |
| ATM | 4.21% | ₹19,520 |
| Mobile | 2.98% | ₹20,310 |
| POS | 2.05% | ₹18,750 |
| Branch | 1.02% | ₹23,100 |

**Time-of-Day Risk Analysis**

- Transactions occurring between 10 PM and 4 AM showed approximately 2x higher fraud rates.
- Analyzed hourly transaction patterns to identify potentially suspicious activity.
- Compared fraud trends across different merchant categories.

### 2. High-Risk Customer Identification

Developed customer risk analysis using transaction behavior and multiple risk indicators.

**Customer Risk Distribution**

| Risk Category | Customers | Percentage |
|---|---:|---:|
| Low | 4,131 | 82.6% |
| Medium | 863 | 17.3% |
| High | 6 | 0.1% |
| Critical | 0 | 0.0% |

**Risk Indicators Tracked**

- **Transaction Velocity:** More than 8 transactions per day.
- **Large Transactions:** Transactions exceeding ₹1 lakh.
- **Unusual Timings:** More than 25% of transactions occurring at night.
- **Multi-City Activity:** Transactions across more than 5 cities.

Additional analysis included:
- Customer risk score distribution.
- Credit score versus fraud analysis.
- Branch-level risk heatmaps.
- Customer ranking using NTILE and DENSE_RANK.

### 3. Daily Transaction Monitoring

Implemented daily monitoring metrics to identify unusual changes in transaction activity.

| Monitoring Metric | Result |
|---|---:|
| Alert Days (Fraud Rate > 5%) | 194 |
| Warning Days (Fraud Rate 3–5%) | 288 |
| Z-Score Anomalies | 1,359 |

**Monitoring Techniques**

- Rolling averages for transaction trend analysis.
- Daily fraud-rate monitoring.
- Z-score-based anomaly identification.
- Branch-wise and monthly fraud monitoring.
- Threshold-based alert and warning classification.

### 4. Machine Learning Anomaly Detection

Implemented an **Isolation Forest** model to identify unusual transaction behavior and compare ML-based detections with rule-based fraud identification.

**Model Results**

| Metric | Result |
|---|---:|
| Total ML Anomalies Detected | 2,445 |
| ML-only New Detections | 2,336 |
| Contamination Rate | 4.0% |

**Features Used**

- Transaction Amount
- Transaction Hour
- Transaction Channel
- Transaction Type
- Day of Week
- Customer Credit Score
- Account Balance

The model helps identify unusual transaction patterns that may not be captured by traditional rule-based checks.

## Power BI Dashboard

The project includes a **4-page Power BI fraud monitoring dashboard** designed to provide an overview of fraud trends, transaction activity, customer risk, and fraud case analysis.

### Dashboard Pages

| Page | Key Visualizations |
|---|---|
| Executive Fraud Overview | KPI cards, monthly fraud-rate trend, channel-wise fraud bar chart, fraud case status donut |
| Transaction Monitoring | Daily transaction volume, rolling averages, fraud-rate analysis, branch-month heatmap |
| High-Risk Customers | Risk distribution, top 20 high-risk customers, branch heatmap, credit-band analysis |
| Fraud Case Analysis | Fraud loss by type, fraud case table, merchant fraud analysis, hour-versus-fraud scatter plot |

### Power BI DAX Measures

The dashboard includes 15 DAX measures:

1. Total Transactions
2. Fraud Count
3. Fraud Rate %
4. Fraud Exposure
5. Average Transaction
6. High-Risk Customers
7. High-Risk %
8. Total Amount Lost
9. Confirmed Fraud Cases
10. Average Resolution Days
11. Fraud Rate MoM Change %
12. Night Hour Fraud %
13. Velocity Risk Customers
14. Average Risk Score
15. Fraud Detection Recall %

Refer to `powerbi/setup_guide.md` for dashboard setup instructions and DAX measure definitions.

## Technology Stack

| Technology | Purpose |
|---|---|
| SQL | Transaction analysis, analytical queries, and window functions |
| SQLite | Portable relational database |
| Python | Data processing, analysis, and automation |
| Pandas & NumPy | Data manipulation and statistical computation |
| Scikit-learn | Isolation Forest anomaly detection |
| Matplotlib & Seaborn | Data visualization and analytical charts |
| Power BI | Interactive fraud monitoring dashboard |
| DAX | Dashboard calculations and analytical measures |
| Jupyter Notebook | Exploratory data analysis and ML experimentation |

## Project Structure

```text
banking-risk-fraud-analytics/
│
├── data/
│   ├── branches.csv
│   ├── customers.csv
│   ├── transactions.csv
│   ├── fraud_cases.csv
│   ├── risk_scores.csv
│   └── banking.db
│
├── sql/
│   ├── schema.sql
│   ├── fraud_patterns.sql
│   ├── high_risk_customers.sql
│   ├── transaction_monitoring.sql
│   └── window_analytics.sql
│
├── python/
│   ├── data_generator.py
│   ├── fraud_analysis.py
│   ├── risk_scoring.py
│   ├── transaction_monitoring.py
│   ├── anomaly_detection.py
│   └── analysis.py
│
├── notebooks/
│   └── banking_fraud_analysis.ipynb
│
├── powerbi/
│   └── setup_guide.md
│
├── reports/
│   ├── report.html
│   ├── high_risk_customers.csv
│   ├── ml_anomalies.csv
│   └── *.png
│
└── requirements.txt
```

### Folder Description

| Folder | Description |
|---|---|
| `data/` | Customer, branch, transaction, fraud case, and risk score datasets |
| `sql/` | Database schema and analytical SQL queries |
| `python/` | Data generation, fraud analysis, risk scoring, monitoring, and ML scripts |
| `notebooks/` | 9-section exploratory data analysis and anomaly detection notebook |
| `powerbi/` | Power BI dashboard setup guide and DAX measures |
| `reports/` | Generated HTML reports, CSV exports, and analytical charts |

## SQL Analysis

The SQL module contains five SQL files covering database design and analytical queries.

**Key SQL techniques:**

- Window Functions: `LAG()`, `LEAD()`, `NTILE()`, `DENSE_RANK()`
- Running totals and cumulative calculations.
- Month-over-month transaction comparisons.
- Transaction velocity analysis.
- Rolling fraud-rate calculations.
- Customer risk ranking.
- Branch-wise and channel-wise fraud analysis.

The database schema also includes 7 indexes to support query execution.

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/abhaysinghuk/banking-risk-fraud-analytics.git

cd banking-risk-fraud-analytics
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Generate the Synthetic Dataset

```bash
python3 python/data_generator.py
```

This generates:
- 5,000 customers.
- 10 banking branches.
- 61,111 transactions.
- A 4.0% fraud rate.
- SQLite database and CSV datasets.

### 4. Run the Complete Analysis

```bash
python3 python/analysis.py
```

This executes the analysis pipeline, including fraud pattern analysis, customer risk scoring, transaction monitoring, Isolation Forest anomaly detection, and HTML report generation.

### 5. Open the HTML Report

```bash
open reports/report.html
```

On Windows, you can open the report using:

```bash
start reports/report.html
```

### 6. Launch the Jupyter Notebook

```bash
jupyter notebook notebooks/banking_fraud_analysis.ipynb
```

## Key Project Highlights

- Analyzed **61,111 banking transactions** across 5,000 customers and 10 branches.
- Identified **2,444 fraud-flagged transactions** through the project's fraud analysis.
- Detected **2,445 anomalies** using Isolation Forest.
- Identified **2,336 additional ML-only detections** beyond rule-based flags.
- Developed customer risk scoring using transaction behavior and multiple risk indicators.
- Implemented daily transaction monitoring with rolling averages and Z-score analysis.
- Designed a **4-page Power BI dashboard** with **15 DAX measures**.
- Generated automated HTML reports, analytical charts, and CSV exports.

## Disclaimer

This project uses a synthetic banking dataset generated for educational and analytical purposes. The fraud detection results and financial metrics represent the sample project run and should not be interpreted as results from a real banking institution or production fraud detection system.

## Author

**Abhay Singh**

- GitHub: [abhaysinghuk](https://github.com/abhaysinghuk)
- LinkedIn: [abhaysinghuk](https://linkedin.com/in/abhaysinghuk)
