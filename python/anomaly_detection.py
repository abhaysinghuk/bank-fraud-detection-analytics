"""
ML-based anomaly detection using Isolation Forest + Z-score comparison.
Flags high-risk transactions not caught by rule-based approach.
"""
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
import os

DB_PATH = "data/banking.db"
OUT_DIR = "reports"
sns.set_theme(style="darkgrid")
os.makedirs(OUT_DIR, exist_ok=True)


def build_features(conn) -> pd.DataFrame:
    df = pd.read_sql_query("""
        SELECT t.id, t.customer_id, t.amount, t.is_flagged,
               CAST(SUBSTR(t.txn_time,1,2) AS INTEGER) AS hour,
               t.channel, t.txn_type,
               CAST(strftime('%w',t.txn_date) AS INTEGER) AS day_of_week,
               c.credit_score, c.account_balance
        FROM transactions t JOIN customers c ON t.customer_id=c.id
    """, conn)

    le = LabelEncoder()
    df["channel_enc"]  = le.fit_transform(df["channel"])
    df["txn_type_enc"] = le.fit_transform(df["txn_type"])

    # Per-customer stats (velocity features)
    cust_stats = df.groupby("customer_id").agg(
        cust_avg_amt=("amount","mean"),
        cust_std_amt=("amount","std"),
        cust_txn_count=("id","count")
    ).reset_index()
    df = df.merge(cust_stats, on="customer_id", how="left")
    df["amt_vs_avg"] = (df["amount"] - df["cust_avg_amt"]) / (df["cust_std_amt"] + 1)
    return df


def run_isolation_forest(df: pd.DataFrame):
    features = ["amount","hour","channel_enc","txn_type_enc","day_of_week",
                 "credit_score","account_balance","amt_vs_avg","cust_txn_count"]
    X = df[features].fillna(0)

    iso = IsolationForest(n_estimators=100, contamination=0.04, random_state=42)
    df["iso_pred"]  = iso.fit_predict(X)   # -1 = anomaly, 1 = normal
    df["iso_score"] = iso.decision_function(X)
    df["is_anomaly"] = (df["iso_pred"] == -1).astype(int)
    return df


def plot_isolation_results(df: pd.DataFrame):
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # Anomaly score distribution
    axes[0, 0].hist(df["iso_score"], bins=60, color="#6c5ce7", alpha=0.7, edgecolor="white")
    axes[0, 0].axvline(x=0, color="#e74c3c", linestyle="--", linewidth=2, label="Decision boundary")
    axes[0, 0].set_title("Isolation Forest Anomaly Score Distribution", fontsize=13, fontweight="bold")
    axes[0, 0].set_xlabel("Anomaly Score (lower = more anomalous)")
    axes[0, 0].set_ylabel("Count")
    axes[0, 0].legend()

    # Amount vs anomaly score
    normal = df[df["is_anomaly"] == 0].sample(min(2000, len(df[df["is_anomaly"]==0])))
    anom   = df[df["is_anomaly"] == 1]
    axes[0, 1].scatter(normal["amount"], normal["iso_score"], c="#6c5ce7", alpha=0.3, s=5, label="Normal")
    axes[0, 1].scatter(anom["amount"],   anom["iso_score"],   c="#e74c3c", alpha=0.6, s=15, label="Anomaly")
    axes[0, 1].set_xlabel("Transaction Amount (₹)")
    axes[0, 1].set_ylabel("Isolation Score")
    axes[0, 1].set_title("Amount vs Anomaly Score", fontsize=13, fontweight="bold")
    axes[0, 1].legend()

    # Anomaly rate by channel
    ch_anom = df.groupby("channel").agg(
        total=("id","count"),
        anomalies=("is_anomaly","sum"),
        rule_flagged=("is_flagged","sum")
    ).reset_index()
    ch_anom["iso_rate"]  = ch_anom["anomalies"] / ch_anom["total"] * 100
    ch_anom["rule_rate"] = ch_anom["rule_flagged"] / ch_anom["total"] * 100

    x = np.arange(len(ch_anom))
    w = 0.35
    axes[1, 0].bar(x - w/2, ch_anom["rule_rate"], w, label="Rule-Based", color="#e67e22", alpha=0.85)
    axes[1, 0].bar(x + w/2, ch_anom["iso_rate"],  w, label="Isolation Forest", color="#e74c3c", alpha=0.85)
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(ch_anom["channel"])
    axes[1, 0].set_title("Fraud Detection Rate: Rule-Based vs ML (by Channel)", fontsize=13, fontweight="bold")
    axes[1, 0].set_ylabel("Detection Rate (%)")
    axes[1, 0].legend()

    # Hour-based anomaly heatmap
    hour_day = df.groupby(["hour","day_of_week"])["is_anomaly"].mean().unstack(fill_value=0) * 100
    day_names = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]
    hour_day.columns = [day_names[c] for c in hour_day.columns if c in range(7)]
    sns.heatmap(hour_day, ax=axes[1, 1], cmap="YlOrRd", annot=False, linewidths=0.2,
                cbar_kws={"label": "Anomaly Rate (%)"})
    axes[1, 1].set_title("Anomaly Rate: Hour × Day of Week", fontsize=13, fontweight="bold")
    axes[1, 1].set_xlabel("Day")
    axes[1, 1].set_ylabel("Hour of Day")

    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/anomaly_detection.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved: reports/anomaly_detection.png")


def export_anomalies(conn, df: pd.DataFrame):
    top = df[df["is_anomaly"] == 1].nsmallest(500, "iso_score")[[
        "id","customer_id","amount","hour","channel","iso_score","is_flagged"
    ]]
    top.to_csv("reports/ml_anomalies.csv", index=False)
    print(f"Exported: reports/ml_anomalies.csv ({len(top)} records)")


def run():
    conn = sqlite3.connect(DB_PATH)
    print("=== ML ANOMALY DETECTION ===")

    df = build_features(conn)
    print(f"Features built for {len(df):,} transactions")

    df = run_isolation_forest(df)
    n_anom = df["is_anomaly"].sum()
    overlap = ((df["is_anomaly"] == 1) & (df["is_flagged"] == 1)).sum()
    new_catches = n_anom - overlap
    print(f"\nIsolation Forest anomalies    : {n_anom:,} ({n_anom/len(df)*100:.1f}%)")
    print(f"Overlap with rule-based flags : {overlap:,}")
    print(f"New catches (not rule-flagged): {new_catches:,}")

    plot_isolation_results(df)
    export_anomalies(conn, df)
    conn.close()


if __name__ == "__main__":
    run()
