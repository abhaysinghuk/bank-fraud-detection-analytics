"""Fraud transaction pattern analysis — channel risk, time patterns, merchant categories."""
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np
import os

DB_PATH = "data/banking.db"
OUT_DIR = "reports"
sns.set_theme(style="darkgrid")
os.makedirs(OUT_DIR, exist_ok=True)


def plot_fraud_overview(conn):
    summary = pd.read_sql_query("""
        SELECT channel,
               COUNT(*) AS total,
               SUM(is_flagged) AS frauds,
               ROUND(SUM(is_flagged)*100.0/COUNT(*),2) AS fraud_rate,
               ROUND(AVG(CASE WHEN is_flagged=1 THEN amount END),2) AS avg_fraud_amt
        FROM transactions GROUP BY channel ORDER BY fraud_rate DESC
    """, conn)

    monthly = pd.read_sql_query("""
        SELECT strftime('%Y-%m',txn_date) AS month,
               COUNT(*) AS total, SUM(is_flagged) AS frauds,
               ROUND(SUM(is_flagged)*100.0/COUNT(*),2) AS fraud_rate
        FROM transactions GROUP BY month ORDER BY month
    """, conn)
    monthly["month"] = pd.to_datetime(monthly["month"])

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    colors = sns.color_palette("Reds_r", len(summary))
    axes[0].bar(summary["channel"], summary["fraud_rate"], color=colors)
    axes[0].set_title("Fraud Rate by Channel (%)", fontsize=14, fontweight="bold")
    axes[0].set_ylabel("Fraud Rate (%)")
    for i, (_, row) in enumerate(summary.iterrows()):
        axes[0].text(i, row["fraud_rate"] + 0.05, f"{row['fraud_rate']:.1f}%", ha="center", fontsize=9)

    axes[1].plot(monthly["month"], monthly["fraud_rate"], marker="o", color="#e74c3c", linewidth=2)
    axes[1].fill_between(monthly["month"], monthly["fraud_rate"], alpha=0.2, color="#e74c3c")
    axes[1].set_title("Monthly Fraud Rate Trend", fontsize=14, fontweight="bold")
    axes[1].set_ylabel("Fraud Rate (%)")
    axes[1].xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%b %Y"))
    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/fraud_overview.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved: reports/fraud_overview.png")
    return summary


def plot_hourly_pattern(conn):
    df = pd.read_sql_query("""
        SELECT CAST(SUBSTR(txn_time,1,2) AS INTEGER) AS hour,
               COUNT(*) AS total, SUM(is_flagged) AS frauds,
               ROUND(SUM(is_flagged)*100.0/COUNT(*),2) AS fraud_rate
        FROM transactions GROUP BY hour ORDER BY hour
    """, conn)

    fig, axes = plt.subplots(1, 2, figsize=(16, 5))
    bar_colors = ["#e74c3c" if (h >= 22 or h <= 4) else "#3498db" for h in df["hour"]]
    axes[0].bar(df["hour"], df["fraud_rate"], color=bar_colors)
    axes[0].set_title("Fraud Rate by Hour of Day", fontsize=14, fontweight="bold")
    axes[0].set_xlabel("Hour (0-23)")
    axes[0].set_ylabel("Fraud Rate (%)")
    from matplotlib.patches import Patch
    axes[0].legend(handles=[Patch(color="#e74c3c", label="High-Risk Hours (10pm-4am)"),
                              Patch(color="#3498db", label="Normal Hours")])

    axes[1].bar(df["hour"], df["total"], color="#6c5ce7", alpha=0.75)
    axes[1].set_title("Transaction Volume by Hour", fontsize=14, fontweight="bold")
    axes[1].set_xlabel("Hour (0-23)")
    axes[1].set_ylabel("Transactions")

    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/hourly_fraud_pattern.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved: reports/hourly_fraud_pattern.png")


def plot_merchant_fraud(conn):
    df = pd.read_sql_query("""
        SELECT merchant_category,
               COUNT(*) AS total, SUM(is_flagged) AS frauds,
               ROUND(SUM(is_flagged)*100.0/COUNT(*),2) AS fraud_rate,
               ROUND(SUM(CASE WHEN is_flagged=1 THEN amount END),2) AS fraud_amount
        FROM transactions WHERE merchant_category IS NOT NULL
        GROUP BY merchant_category ORDER BY fraud_amount DESC
    """, conn)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    axes[0].barh(df["merchant_category"][::-1], df["fraud_rate"][::-1],
                 color=sns.color_palette("OrRd", len(df)))
    axes[0].set_title("Fraud Rate by Merchant Category", fontsize=14, fontweight="bold")
    axes[0].set_xlabel("Fraud Rate (%)")

    axes[1].barh(df["merchant_category"][::-1], df["fraud_amount"][::-1],
                 color=sns.color_palette("Reds_r", len(df)))
    axes[1].set_title("Total Fraud Amount by Merchant Category", fontsize=14, fontweight="bold")
    axes[1].set_xlabel("Fraud Amount (₹)")
    axes[1].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))

    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/merchant_fraud.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved: reports/merchant_fraud.png")


def plot_fraud_cases(conn):
    df = pd.read_sql_query("""
        SELECT fraud_type, status,
               COUNT(*) AS cases,
               ROUND(SUM(amount_lost),2) AS total_loss,
               ROUND(AVG(resolution_days),1) AS avg_resolution_days
        FROM fraud_cases GROUP BY fraud_type, status
        ORDER BY total_loss DESC
    """, conn)

    by_type = df.groupby("fraud_type")["total_loss"].sum().sort_values(ascending=False)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    axes[0].barh(by_type.index[::-1], by_type.values[::-1],
                 color=sns.color_palette("Reds_r", len(by_type)))
    axes[0].set_title("Total Loss by Fraud Type", fontsize=14, fontweight="bold")
    axes[0].set_xlabel("Amount Lost (₹)")
    axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))

    status_ct = pd.read_sql_query("SELECT status, COUNT(*) AS n FROM fraud_cases GROUP BY status", conn)
    axes[1].pie(status_ct["n"], labels=status_ct["status"], autopct="%1.1f%%",
                colors=["#e74c3c","#27ae60","#f39c12"], startangle=90)
    axes[1].set_title("Fraud Case Resolution Status", fontsize=14, fontweight="bold")

    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/fraud_cases.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved: reports/fraud_cases.png")


def run():
    conn = sqlite3.connect(DB_PATH)
    print("=== FRAUD PATTERN ANALYSIS ===")
    ch_df = plot_fraud_overview(conn)
    plot_hourly_pattern(conn)
    plot_merchant_fraud(conn)
    plot_fraud_cases(conn)

    total = pd.read_sql_query("SELECT COUNT(*) AS t, SUM(is_flagged) AS f, ROUND(SUM(CASE WHEN is_flagged=1 THEN amount END),2) AS fa FROM transactions", conn).iloc[0]
    print(f"\nTotal transactions : {int(total['t']):,}")
    print(f"Flagged (fraud)    : {int(total['f']):,} ({int(total['f'])/int(total['t'])*100:.1f}%)")
    print(f"Fraud exposure     : ₹{total['fa']:,.0f}")
    print(f"\nHighest fraud rate channel: {ch_df.iloc[0]['channel']} ({ch_df.iloc[0]['fraud_rate']}%)")
    conn.close()


if __name__ == "__main__":
    run()
