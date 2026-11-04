"""Daily transaction monitoring — KPI alerts, rolling averages, z-score anomalies."""
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


def plot_daily_monitoring(conn):
    df = pd.read_sql_query("""
        SELECT txn_date AS date,
               COUNT(*) AS total_txns,
               ROUND(SUM(amount),2) AS volume,
               SUM(is_flagged) AS flagged,
               ROUND(SUM(is_flagged)*100.0/COUNT(*),2) AS fraud_rate,
               ROUND(MAX(amount),2) AS max_txn
        FROM transactions GROUP BY date ORDER BY date
    """, conn)
    df["date"] = pd.to_datetime(df["date"])
    df["rolling_7d_vol"]  = df["volume"].rolling(7).mean()
    df["rolling_7d_rate"] = df["fraud_rate"].rolling(7).mean()
    df["alert"] = df["fraud_rate"].apply(lambda x: "ALERT" if x > 5 else "WARNING" if x > 3 else "NORMAL")

    fig, axes = plt.subplots(3, 1, figsize=(18, 12), sharex=True)

    # Volume + rolling avg
    axes[0].bar(df["date"], df["volume"]/1e6, width=0.8, color="#6c5ce7", alpha=0.5, label="Daily Volume")
    axes[0].plot(df["date"], df["rolling_7d_vol"]/1e6, color="#2c3e50", linewidth=2, label="7-day rolling avg")
    axes[0].set_title("Daily Transaction Volume (₹M)", fontsize=13, fontweight="bold")
    axes[0].set_ylabel("Volume (₹M)")
    axes[0].legend(fontsize=8)

    # Fraud rate + thresholds
    colors = df["alert"].map({"ALERT":"#e74c3c","WARNING":"#f39c12","NORMAL":"#27ae60"})
    axes[1].bar(df["date"], df["fraud_rate"], width=0.8, color=colors, alpha=0.8)
    axes[1].plot(df["date"], df["rolling_7d_rate"], color="#2c3e50", linewidth=2, label="7-day rolling")
    axes[1].axhline(y=3, color="#f39c12", linestyle="--", linewidth=1, label="Warning (3%)")
    axes[1].axhline(y=5, color="#e74c3c", linestyle="--", linewidth=1, label="Alert (5%)")
    axes[1].set_title("Daily Fraud Rate with Alert Thresholds", fontsize=13, fontweight="bold")
    axes[1].set_ylabel("Fraud Rate (%)")
    axes[1].legend(fontsize=8)

    # Transaction count
    axes[2].plot(df["date"], df["total_txns"], color="#0984e3", linewidth=1.5)
    axes[2].fill_between(df["date"], df["total_txns"], alpha=0.15, color="#0984e3")
    axes[2].set_title("Daily Transaction Count", fontsize=13, fontweight="bold")
    axes[2].set_ylabel("Transactions")
    axes[2].xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%b %Y"))
    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/daily_monitoring.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved: reports/daily_monitoring.png")
    return df


def plot_zscore_anomalies(conn):
    df = pd.read_sql_query("""
        SELECT t.txn_id, c.customer_id, c.name, t.txn_date, t.txn_time,
               t.amount, t.channel, t.merchant_category, t.is_flagged
        FROM transactions t JOIN customers c ON t.customer_id=c.id
    """, conn)

    mean_amt = df["amount"].mean()
    std_amt  = df["amount"].std()
    df["z_score"] = (df["amount"] - mean_amt) / std_amt
    anomalies = df[df["z_score"] > 2.5].copy()

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Amount distribution with anomaly threshold
    axes[0].hist(df["amount"].clip(0, 50000), bins=60, color="#6c5ce7", alpha=0.7, edgecolor="white")
    axes[0].axvline(x=mean_amt + 2.5 * std_amt, color="#e74c3c", linestyle="--", linewidth=2,
                    label=f"Anomaly threshold (z>2.5): ₹{mean_amt + 2.5*std_amt:,.0f}")
    axes[0].set_title("Transaction Amount Distribution", fontsize=13, fontweight="bold")
    axes[0].set_xlabel("Amount (₹)")
    axes[0].set_ylabel("Frequency")
    axes[0].legend(fontsize=8)

    # Anomaly scatter by channel
    chan_colors = {"ATM":"#e74c3c","Online":"#e67e22","Branch":"#3498db","Mobile":"#27ae60","POS":"#9b59b6"}
    for ch, grp in anomalies.groupby("channel"):
        axes[1].scatter(grp["amount"], grp["z_score"], label=ch,
                        color=chan_colors.get(ch,"#95a5a6"), alpha=0.6, s=30)
    axes[1].axhline(y=2.5, color="#e74c3c", linestyle="--", label="z=2.5 threshold")
    axes[1].set_xlabel("Transaction Amount (₹)")
    axes[1].set_ylabel("Z-Score")
    axes[1].set_title(f"Anomalous Transactions (z > 2.5) — {len(anomalies):,} flagged", fontsize=13, fontweight="bold")
    axes[1].legend(fontsize=8)

    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/zscore_anomalies.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved: reports/zscore_anomalies.png")
    return anomalies


def plot_branch_monitoring(conn):
    df = pd.read_sql_query("""
        SELECT b.name AS branch,
               strftime('%Y-%m',t.txn_date) AS month,
               COUNT(*) AS txns,
               ROUND(SUM(t.amount),2) AS volume,
               SUM(t.is_flagged) AS frauds
        FROM transactions t
        JOIN customers c ON t.customer_id=c.id
        JOIN branches b ON c.branch_id=b.id
        GROUP BY b.id, month ORDER BY month
    """, conn)
    pivot = df.pivot(index="branch", columns="month", values="frauds").fillna(0)
    # Keep last 12 months
    pivot = pivot.iloc[:, -12:]

    fig, ax = plt.subplots(figsize=(18, 6))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlOrRd", linewidths=0.3, ax=ax,
                cbar_kws={"label": "Fraud Transactions"})
    ax.set_title("Branch × Month Fraud Transaction Heatmap", fontsize=14, fontweight="bold")
    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/branch_monitoring.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved: reports/branch_monitoring.png")


def run():
    conn = sqlite3.connect(DB_PATH)
    print("=== TRANSACTION MONITORING ===")
    daily_df = plot_daily_monitoring(conn)
    anomalies = plot_zscore_anomalies(conn)
    plot_branch_monitoring(conn)

    alert_days = (daily_df["alert"] == "ALERT").sum()
    warn_days  = (daily_df["alert"] == "WARNING").sum()
    print(f"\nAlert days (fraud >5%)   : {alert_days}")
    print(f"Warning days (fraud 3-5%): {warn_days}")
    print(f"Z-score anomalies (>2.5) : {len(anomalies):,}")
    conn.close()


if __name__ == "__main__":
    run()
