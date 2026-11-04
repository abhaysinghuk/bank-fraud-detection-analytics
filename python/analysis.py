"""
Master runner — executes all modules and generates an HTML executive report.
Usage: python3 python/analysis.py
"""
import sqlite3, os, sys, pandas as pd
from datetime import datetime

DB_PATH = "data/banking.db"
OUT_DIR = "reports"
sys.path.insert(0, os.path.dirname(__file__))


def check_db():
    if not os.path.exists(DB_PATH):
        import subprocess
        subprocess.run(["python3", "python/data_generator.py"], check=True)


def run_all():
    check_db()
    os.makedirs(OUT_DIR, exist_ok=True)

    from fraud_analysis        import run as run_fraud
    from risk_scoring          import run as run_risk
    from transaction_monitoring import run as run_monitor
    from anomaly_detection     import run as run_anomaly

    print("\n" + "="*55); run_fraud()
    print("\n" + "="*55); run_risk()
    print("\n" + "="*55); run_monitor()
    print("\n" + "="*55); run_anomaly()
    generate_html_report()


def generate_html_report():
    conn = sqlite3.connect(DB_PATH)

    kpi = pd.read_sql_query("""
        SELECT
            (SELECT COUNT(*) FROM customers) AS customers,
            (SELECT COUNT(*) FROM branches)  AS branches,
            COUNT(*) AS total_txns,
            SUM(is_flagged) AS flagged,
            ROUND(SUM(is_flagged)*100.0/COUNT(*),2) AS fraud_rate,
            ROUND(SUM(CASE WHEN is_flagged=1 THEN amount END),2) AS fraud_exposure,
            ROUND(SUM(amount),2) AS total_volume,
            ROUND(AVG(amount),2) AS avg_txn
        FROM transactions
    """, conn).iloc[0]

    risk_dist = pd.read_sql_query("""
        SELECT risk_label, COUNT(*) AS n FROM risk_scores
        GROUP BY risk_label ORDER BY n DESC
    """, conn)

    top_cases = pd.read_sql_query("""
        SELECT fc.fraud_type, fc.status,
               COUNT(*) AS cases, ROUND(SUM(fc.amount_lost),2) AS total_loss
        FROM fraud_cases fc
        GROUP BY fc.fraud_type, fc.status
        ORDER BY total_loss DESC LIMIT 8
    """, conn)
    conn.close()

    charts = [
        ("Fraud Overview",           "fraud_overview.png"),
        ("Hourly Fraud Pattern",     "hourly_fraud_pattern.png"),
        ("Merchant Category Fraud",  "merchant_fraud.png"),
        ("Fraud Cases & Losses",     "fraud_cases.png"),
        ("Risk Score Distribution",  "risk_distribution.png"),
        ("Credit Score vs Fraud",    "credit_fraud.png"),
        ("Branch Risk Heatmap",      "branch_risk_heatmap.png"),
        ("Daily Monitoring",         "daily_monitoring.png"),
        ("Z-Score Anomalies",        "zscore_anomalies.png"),
        ("Branch Fraud Heatmap",     "branch_monitoring.png"),
        ("ML Anomaly Detection",     "anomaly_detection.png"),
    ]

    charts_html = "".join(
        f'<div class="chart-block"><h3>{t}</h3><img src="{f}" alt="{t}"/></div>'
        for t, f in charts if os.path.exists(f"{OUT_DIR}/{f}")
    )

    fraud_rate_class = "kpi-danger" if kpi["fraud_rate"] > 4 else "kpi-warn" if kpi["fraud_rate"] > 2 else "kpi-ok"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>Banking Risk & Fraud Analytics</title>
<style>
  body{{font-family:'Segoe UI',sans-serif;background:#f0f2f5;color:#1a1a2e;margin:0;padding:0}}
  header{{background:linear-gradient(135deg,#e74c3c,#c0392b);color:white;padding:30px 40px}}
  header h1{{margin:0;font-size:2rem}}
  header p{{margin:6px 0 0;opacity:.85}}
  .container{{max-width:1200px;margin:auto;padding:30px}}
  .kpi-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:16px;margin-bottom:30px}}
  .kpi{{background:white;border-radius:12px;padding:20px;box-shadow:0 2px 8px rgba(0,0,0,.08);text-align:center}}
  .kpi .val{{font-size:1.8rem;font-weight:700;color:#e74c3c}}
  .kpi-danger .val{{color:#e74c3c}}
  .kpi-warn .val{{color:#e67e22}}
  .kpi-ok .val{{color:#27ae60}}
  .kpi .lbl{{font-size:.8rem;color:#636e72;margin-top:4px}}
  table{{width:100%;border-collapse:collapse;background:white;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08);margin-bottom:30px}}
  th{{background:#c0392b;color:white;padding:12px 14px;text-align:left;font-size:.85rem}}
  td{{padding:10px 14px;border-bottom:1px solid #f0f0f0;font-size:.85rem}}
  tr:last-child td{{border-bottom:none}}
  tr:hover td{{background:#fff5f5}}
  h2{{color:#c0392b;margin-top:40px}}
  .chart-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(520px,1fr));gap:20px}}
  .chart-block{{background:white;border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(0,0,0,.08)}}
  .chart-block h3{{margin:0 0 12px;color:#636e72;font-size:.95rem}}
  .chart-block img{{width:100%;border-radius:8px}}
  footer{{text-align:center;padding:20px;color:#636e72;font-size:.8rem;margin-top:40px}}
</style>
</head>
<body>
<header>
  <h1>Banking Risk & Fraud Analytics</h1>
  <p>Generated {datetime.now().strftime("%d %B %Y, %H:%M")} &nbsp;|&nbsp; DataSenseHQ</p>
</header>
<div class="container">
  <h2>Executive Summary</h2>
  <div class="kpi-grid">
    <div class="kpi"><div class="val">{int(kpi['customers']):,}</div><div class="lbl">Customers</div></div>
    <div class="kpi"><div class="val">{int(kpi['branches'])}</div><div class="lbl">Branches</div></div>
    <div class="kpi"><div class="val">{int(kpi['total_txns']):,}</div><div class="lbl">Transactions</div></div>
    <div class="kpi"><div class="val">{int(kpi['flagged']):,}</div><div class="lbl">Fraud Flagged</div></div>
    <div class="kpi {fraud_rate_class}"><div class="val">{kpi['fraud_rate']}%</div><div class="lbl">Fraud Rate</div></div>
    <div class="kpi kpi-danger"><div class="val">₹{kpi['fraud_exposure']/1e5:.1f}L</div><div class="lbl">Fraud Exposure</div></div>
    <div class="kpi"><div class="val">₹{kpi['total_volume']/1e7:.1f}Cr</div><div class="lbl">Total Volume</div></div>
    <div class="kpi"><div class="val">₹{kpi['avg_txn']:,.0f}</div><div class="lbl">Avg Transaction</div></div>
  </div>

  <h2>Risk Score Distribution</h2>
  {risk_dist.to_html(index=False, classes="", border=0)}

  <h2>Top Fraud Cases by Loss</h2>
  {top_cases.to_html(index=False, classes="", border=0)}

  <h2>Charts</h2>
  <div class="chart-grid">{charts_html}</div>
</div>
<footer>Banking Risk & Fraud Analytics &copy; {datetime.now().year} DataSenseHQ</footer>
</body></html>"""

    with open(f"{OUT_DIR}/report.html", "w") as f:
        f.write(html)
    print(f"\nHTML report: {OUT_DIR}/report.html")


if __name__ == "__main__":
    run_all()
