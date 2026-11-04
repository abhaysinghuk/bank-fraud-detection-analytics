"""High-risk customer identification — risk scoring, credit bands, branch heatmap."""
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


def plot_risk_distribution(conn):
    df = pd.read_sql_query("""
        SELECT r.risk_label, r.risk_score,
               r.velocity_flag, r.large_txn_flag, r.odd_hour_flag, r.multi_city_flag,
               c.credit_score, c.account_balance, c.account_type
        FROM risk_scores r JOIN customers c ON r.customer_id=c.id
    """, conn)

    label_order = ["Critical","High","Medium","Low"]
    colors = {"Critical":"#e74c3c","High":"#e67e22","Medium":"#f1c40f","Low":"#27ae60"}
    counts = df["risk_label"].value_counts().reindex(label_order, fill_value=0)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    pie_c = [colors[l] for l in counts.index]
    axes[0].pie(counts, labels=counts.index, autopct="%1.1f%%", colors=pie_c, startangle=90,
                wedgeprops={"edgecolor":"white","linewidth":1.5})
    axes[0].set_title("Customer Risk Label Distribution", fontsize=14, fontweight="bold")

    data = [df[df["risk_label"]==l]["risk_score"].values for l in label_order]
    bp = axes[1].boxplot(data, patch_artist=True, labels=label_order)
    for patch, lbl in zip(bp["boxes"], label_order):
        patch.set_facecolor(colors[lbl])
        patch.set_alpha(0.75)
    axes[1].set_title("Risk Score Distribution by Label", fontsize=14, fontweight="bold")
    axes[1].set_ylabel("Risk Score")

    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/risk_distribution.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved: reports/risk_distribution.png")
    return df


def plot_credit_vs_fraud(conn):
    df = pd.read_sql_query("""
        SELECT
            CASE
                WHEN c.credit_score < 550 THEN 'Very Poor\n(<550)'
                WHEN c.credit_score < 650 THEN 'Poor\n(550-649)'
                WHEN c.credit_score < 750 THEN 'Fair\n(650-749)'
                WHEN c.credit_score < 800 THEN 'Good\n(750-799)'
                ELSE 'Excellent\n(800+)'
            END AS band,
            c.credit_score,
            COUNT(DISTINCT c.id) AS customers,
            ROUND(AVG(t.is_flagged)*100, 2) AS fraud_rate,
            ROUND(AVG(c.account_balance), 2) AS avg_balance
        FROM customers c JOIN transactions t ON t.customer_id=c.id
        GROUP BY band ORDER BY AVG(c.credit_score)
    """, conn)

    fig, axes = plt.subplots(1, 2, figsize=(16, 5))
    bar_colors = ["#e74c3c","#e67e22","#f1c40f","#2ecc71","#27ae60"]
    axes[0].bar(df["band"], df["fraud_rate"], color=bar_colors[:len(df)])
    axes[0].set_title("Fraud Rate by Credit Score Band", fontsize=14, fontweight="bold")
    axes[0].set_ylabel("Fraud Rate (%)")
    for i, (_, row) in enumerate(df.iterrows()):
        axes[0].text(i, row["fraud_rate"] + 0.02, f"{row['fraud_rate']:.1f}%", ha="center", fontsize=9)

    axes[1].scatter(df["avg_balance"]/1000, df["fraud_rate"],
                    s=df["customers"]/5, c=bar_colors[:len(df)],
                    alpha=0.85, edgecolors="white", linewidths=1)
    for _, row in df.iterrows():
        axes[1].annotate(row["band"].replace("\n"," "), (row["avg_balance"]/1000, row["fraud_rate"]),
                         fontsize=8, ha="left")
    axes[1].set_xlabel("Avg Balance (₹K)")
    axes[1].set_ylabel("Fraud Rate (%)")
    axes[1].set_title("Balance vs Fraud Rate by Credit Band", fontsize=14, fontweight="bold")

    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/credit_fraud.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved: reports/credit_fraud.png")


def plot_branch_risk_heatmap(conn):
    df = pd.read_sql_query("""
        SELECT b.name AS branch, r.risk_label, COUNT(*) AS customers
        FROM risk_scores r
        JOIN customers c ON r.customer_id=c.id
        JOIN branches b ON c.branch_id=b.id
        GROUP BY b.id, r.risk_label
    """, conn)

    pivot = df.pivot(index="branch", columns="risk_label", values="customers").fillna(0)
    for col in ["Critical","High","Medium","Low"]:
        if col not in pivot.columns:
            pivot[col] = 0
    pivot = pivot[["Critical","High","Medium","Low"]]

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="RdYlGn_r", linewidths=0.5, ax=ax)
    ax.set_title("Risk Customer Count per Branch × Risk Label", fontsize=14, fontweight="bold")
    ax.set_xlabel("Risk Label")
    ax.set_ylabel("Branch")
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/branch_risk_heatmap.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved: reports/branch_risk_heatmap.png")


def export_high_risk(conn):
    df = pd.read_sql_query("""
        SELECT c.customer_id, c.name, c.city, c.account_type, c.credit_score,
               ROUND(c.account_balance,2) AS balance,
               r.risk_score, r.risk_label,
               r.velocity_flag, r.large_txn_flag, r.odd_hour_flag, r.multi_city_flag,
               COUNT(t.id) AS txns,
               SUM(t.is_flagged) AS fraud_txns
        FROM risk_scores r
        JOIN customers c ON r.customer_id=c.id
        LEFT JOIN transactions t ON t.customer_id=c.id
        WHERE r.risk_label IN ('Critical','High')
        GROUP BY c.id ORDER BY r.risk_score DESC
    """, conn)
    path = "reports/high_risk_customers.csv"
    df.to_csv(path, index=False)
    print(f"Exported: {path} ({len(df)} records)")
    return df


def run():
    conn = sqlite3.connect(DB_PATH)
    print("=== HIGH-RISK CUSTOMER ANALYSIS ===")
    df = plot_risk_distribution(conn)
    plot_credit_vs_fraud(conn)
    plot_branch_risk_heatmap(conn)
    hr_df = export_high_risk(conn)

    dist = df["risk_label"].value_counts()
    print("\nRisk distribution:")
    for label in ["Critical","High","Medium","Low"]:
        n = dist.get(label, 0)
        print(f"  {label:<10}: {n:,} ({n/len(df)*100:.1f}%)")
    print(f"\nHigh/Critical customers: {len(hr_df):,}")
    conn.close()


if __name__ == "__main__":
    run()
