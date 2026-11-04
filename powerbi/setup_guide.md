# Power BI Banking Risk & Fraud Dashboard Setup Guide

## Step 1 — Connect to Data

1. Open **Power BI Desktop**
2. **Get Data → Text/CSV** — import all 5 files from `data/`:
   - `branches.csv`
   - `customers.csv`
   - `transactions.csv`
   - `fraud_cases.csv`
   - `risk_scores.csv`

## Step 2 — Set Relationships (Model View)

| From | To | Cardinality |
|------|----|-------------|
| `transactions[customer_id]` | `customers[id]` | Many → One |
| `transactions[branch_id]` | `branches[id]` | Many → One |
| `fraud_cases[customer_id]` | `customers[id]` | Many → One |
| `fraud_cases[txn_id]` | `transactions[id]` | Many → One |
| `risk_scores[customer_id]` | `customers[id]` | One → One |
| `customers[branch_id]` | `branches[id]` | Many → One |

## Step 3 — Date Table

In Power Query Editor → **New Query → Blank Query**:

```m
let
    StartDate = #date(2023,1,1),
    EndDate   = #date(2024,12,31),
    Days      = Duration.Days(EndDate - StartDate) + 1,
    Source    = List.Dates(StartDate, Days, #duration(1,0,0,0)),
    Table     = Table.FromList(Source, Splitter.SplitByNothing(), {"Date"}),
    Changed   = Table.TransformColumnTypes(Table, {{"Date", type date}}),
    Year      = Table.AddColumn(Changed,  "Year",    each Date.Year([Date]),    Int64.Type),
    Quarter   = Table.AddColumn(Year,     "Quarter", each "Q"&Text.From(Date.QuarterOfYear([Date])), type text),
    Month     = Table.AddColumn(Quarter,  "Month",   each Date.MonthName([Date]), type text),
    MonthNum  = Table.AddColumn(Month,    "MonthNum",each Date.Month([Date]),   Int64.Type),
    Weekday   = Table.AddColumn(MonthNum, "Weekday", each Date.DayOfWeekName([Date]), type text)
in Weekday
```

Connect `transactions[txn_date]` → `DateTable[Date]`.

## Step 4 — DAX Measures

Create a **Measures** table and add:

```dax
Total Transactions =
COUNTROWS(transactions)

Total Volume =
SUM(transactions[amount])

Fraud Count =
CALCULATE(COUNTROWS(transactions), transactions[is_flagged] = 1)

Fraud Rate % =
DIVIDE([Fraud Count], [Total Transactions], 0) * 100

Fraud Exposure =
CALCULATE(SUM(transactions[amount]), transactions[is_flagged] = 1)

Avg Transaction Amount =
AVERAGEX(transactions, transactions[amount])

High Risk Customers =
CALCULATE(
    COUNTROWS(risk_scores),
    risk_scores[risk_label] IN {"High", "Critical"}
)

High Risk % =
DIVIDE([High Risk Customers], COUNTROWS(risk_scores), 0) * 100

Total Amount Lost =
SUM(fraud_cases[amount_lost])

Fraud Cases Confirmed =
CALCULATE(COUNTROWS(fraud_cases), fraud_cases[status] = "Confirmed")

Avg Resolution Days =
AVERAGEX(
    FILTER(fraud_cases, NOT ISBLANK(fraud_cases[resolution_days])),
    fraud_cases[resolution_days]
)

Fraud Rate MoM Change % =
VAR CurrentRate = [Fraud Rate %]
VAR PrevRate =
    CALCULATE([Fraud Rate %], DATEADD(DateTable[Date], -1, MONTH))
RETURN DIVIDE(CurrentRate - PrevRate, PrevRate, 0) * 100

Night Hour Fraud % =
CALCULATE(
    [Fraud Count],
    FILTER(transactions,
        VALUE(LEFT(transactions[txn_time], 2)) >= 22
        || VALUE(LEFT(transactions[txn_time], 2)) <= 4)
) / [Fraud Count] * 100

Velocity Risk Customers =
CALCULATE(COUNTROWS(risk_scores), risk_scores[velocity_flag] = 1)

Avg Risk Score =
AVERAGEX(risk_scores, risk_scores[risk_score])

Fraud Detection Recall % =
DIVIDE([Fraud Count], [Fraud Count] + 100, 0) * 100
```

## Step 5 — Dashboard Pages

### Page 1: Executive Fraud Overview
- **KPI Cards**: Total Transactions, Fraud Rate %, Fraud Exposure, High Risk Customers
- **Line Chart**: Monthly Fraud Rate Trend with alert thresholds (3% warning, 5% alert)
- **Bar Chart**: Fraud Rate by Channel
- **Donut**: Fraud Case Resolution Status
- **Slicer**: Year, Quarter, Channel, Branch

### Page 2: Transaction Monitoring
- **Line + Band**: Daily transaction volume with 7-day rolling average
- **Conditional Bar**: Daily fraud rate (red=alert, orange=warning, green=normal)
- **Heatmap Matrix**: Branch × Month fraud counts
- **Table**: Top anomalous transactions by z-score
- **Slicer**: Branch, Channel, Date range

### Page 3: High-Risk Customers
- **Donut**: Risk label distribution (Critical/High/Medium/Low)
- **Table**: Top 20 high-risk customers with all flags
- **Heatmap**: Branch × Risk Label customer count
- **Bar**: Fraud rate by credit score band
- **Scatter**: Risk Score vs Account Balance
- **Slicer**: Branch, Account Type, Risk Label

### Page 4: Fraud Case Analysis
- **Bar**: Total loss by fraud type
- **Table**: Fraud cases with status, resolution days, amount lost
- **Bar**: Fraud by merchant category
- **Scatter**: Hour vs Fraud Rate (time-of-day pattern)
- **KPI**: Avg resolution days, confirmed cases, dismissed rate
- **Slicer**: Fraud Type, Status, Year

## Step 6 — Conditional Formatting

**Fraud Rate column**:
- > 5% → Red
- 3–5% → Orange
- < 3% → Green

**Risk Label column**:
- `Critical` → Red | `High` → Orange | `Medium` → Yellow | `Low` → Green

**Resolution Days**: gradient — longer days → darker red

## Step 7 — Publish

1. **File → Publish to Power BI Service**
2. Select workspace
3. Set **Scheduled Refresh** if connected to live data
4. Configure **Data Alerts** on Fraud Rate KPI card (alert if > 5%)
