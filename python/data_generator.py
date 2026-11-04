"""
Banking synthetic data generator.
Produces branches, customers, transactions (with fraud injection),
fraud_cases, and risk_scores for 2023-2024.
"""
import sqlite3, random, os, csv, math
from datetime import date, timedelta, datetime

random.seed(42)
DB_PATH = "data/banking.db"
os.makedirs("data", exist_ok=True)

BRANCHES = [
    ("BRN001","Mumbai Central","Mumbai","West"),
    ("BRN002","Delhi Connaught","Delhi","North"),
    ("BRN003","Bengaluru MG Road","Bengaluru","South"),
    ("BRN004","Chennai Anna Nagar","Chennai","South"),
    ("BRN005","Hyderabad Banjara","Hyderabad","South"),
    ("BRN006","Pune Koregaon","Pune","West"),
    ("BRN007","Ahmedabad CG Road","Ahmedabad","West"),
    ("BRN008","Kolkata Park Street","Kolkata","East"),
    ("BRN009","Jaipur MI Road","Jaipur","North"),
    ("BRN010","Lucknow Hazratganj","Lucknow","North"),
]

FIRST = ["Amit","Priya","Rahul","Sunita","Vijay","Anita","Sanjay","Deepa","Rajesh","Kavita",
          "Mohan","Lalita","Suresh","Pooja","Arun","Rekha","Vinod","Meera","Ashok","Gita",
          "Harish","Jyoti","Nitin","Usha","Prakash","Sheela","Vivek","Swati","Naveen","Indira",
          "Dilip","Radha","Rohit","Tara","Kishore","Smita","Devendra","Madhuri","Girish","Saroj",
          "Ravi","Savita","Mukesh","Lata","Ganesh","Suman","Brijesh","Kamla","Ajay","Nirmala"]
LAST  = ["Sharma","Patel","Kumar","Singh","Gupta","Mehta","Joshi","Rao","Nair","Iyer",
          "Pillai","Verma","Bose","Chandra","Das","Reddy","Kulkarni","Banerjee","Saxena","Jain",
          "Agarwal","Mishra","Bhatt","Pandey","Yadav","Ghosh","Kapoor","Srivastava","Menon","Tiwari"]
CITIES = ["Mumbai","Delhi","Bengaluru","Chennai","Hyderabad","Pune","Ahmedabad","Kolkata","Jaipur","Lucknow",
           "Surat","Nagpur","Indore","Bhopal","Kochi","Patna","Agra","Vadodara","Chandigarh","Coimbatore"]
MERCHANT_CATS = ["Grocery","Electronics","Jewellery","Fuel","Travel","Restaurants",
                  "Healthcare","Education","Clothing","Online Retail","ATM Withdrawal",
                  "Utilities","Entertainment","Real Estate","Foreign Exchange"]
ACCOUNT_TYPES  = ["Savings","Current","Salary","Fixed Deposit"]
AT_WEIGHTS     = [55, 25, 15, 5]
CHANNELS       = ["ATM","Online","Branch","Mobile","POS"]
CH_WEIGHTS     = [20, 30, 10, 25, 15]

# Fraud probability by channel (Online and ATM are higher risk)
FRAUD_PROB = {"ATM":0.04,"Online":0.06,"Branch":0.01,"Mobile":0.03,"POS":0.02}

# Month transaction volume weights (higher in festive months)
MONTH_WEIGHTS = [1.0,0.9,1.0,1.0,1.0,1.0,1.1,1.1,1.2,1.3,1.4,1.5]


def rand_date(start: date, end: date) -> date:
    return start + timedelta(days=random.randint(0, (end - start).days))


def build_db():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(open("sql/schema.sql").read())
    cur = conn.cursor()

    # Branches
    for b in BRANCHES:
        cur.execute("INSERT OR IGNORE INTO branches(code,name,city,region) VALUES(?,?,?,?)", b)
    conn.commit()
    branch_ids = [r[0] for r in cur.execute("SELECT id FROM branches").fetchall()]

    # Customers — 5000
    print("Generating customers...")
    for i in range(1, 5001):
        cid   = f"CUST-{i:05d}"
        name  = f"{random.choice(FIRST)} {random.choice(LAST)}"
        age   = random.randint(18, 75)
        gender = random.choices(["Male","Female"], weights=[52,48])[0]
        city  = random.choice(CITIES)
        atype = random.choices(ACCOUNT_TYPES, weights=AT_WEIGHTS)[0]
        bid   = random.choice(branch_ids)
        bal   = round(random.uniform(1000, 500000), 2)
        cs    = random.randint(450, 850)
        kyc   = random.choices(["Verified","Pending","Rejected"], weights=[88,9,3])[0]
        opened = rand_date(date(2018, 1, 1), date(2022, 12, 31)).isoformat()
        cur.execute(
            "INSERT OR IGNORE INTO customers(customer_id,name,age,gender,city,account_type,branch_id,account_balance,credit_score,kyc_status,opened_on) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (cid, name, age, gender, city, atype, bid, bal, cs, kyc, opened)
        )
    conn.commit()
    cust_ids = [r[0] for r in cur.execute("SELECT id FROM customers").fetchall()]
    print(f"  {len(cust_ids)} customers created")

    # Transactions — ~50k
    print("Generating transactions...")
    start_d = date(2023, 1, 1)
    end_d   = date(2024, 12, 31)
    txn_count  = 0
    fraud_count = 0
    txn_id_counter = 1

    d = start_d
    while d <= end_d:
        # 60-90 transactions per day, weighted by month
        n = int(random.randint(60, 90) * MONTH_WEIGHTS[d.month - 1])
        for _ in range(n):
            cid    = random.choice(cust_ids)
            bid    = cur.execute("SELECT branch_id FROM customers WHERE id=?", (cid,)).fetchone()[0]
            channel = random.choices(CHANNELS, weights=CH_WEIGHTS)[0]
            hour   = random.choices(
                list(range(24)),
                weights=[1,1,1,1,1,2,4,8,10,10,10,10,9,9,9,9,8,7,6,5,4,3,2,1]
            )[0]
            txn_time = f"{hour:02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}"
            txn_type = random.choices(["Debit","Credit"], weights=[72,28])[0]
            amount   = round(random.lognormvariate(7.5, 1.2), 2)  # log-normal for realistic amounts
            amount   = max(50, min(amount, 500000))
            mcat     = random.choice(MERCHANT_CATS) if txn_type == "Debit" else None
            city     = random.choice(CITIES)
            bal_after = round(random.uniform(500, 200000), 2)
            txn_id   = f"TXN{txn_id_counter:08d}"

            # Fraud injection
            is_fraud = 0
            reason   = None
            base_prob = FRAUD_PROB.get(channel, 0.02)

            # Higher fraud at night (10pm-4am)
            if hour >= 22 or hour <= 4:
                base_prob *= 2.0
            # Large amount increases fraud probability
            if amount > 50000:
                base_prob *= 1.5

            if random.random() < base_prob:
                is_fraud = 1
                fraud_count += 1
                reason = random.choice([
                    "Unusual amount","Velocity breach","Odd-hour transaction",
                    "Multi-city anomaly","Unrecognized merchant","Card not present",
                    "Geo-mismatch","Rapid successive transactions"
                ])

            cur.execute(
                "INSERT INTO transactions(txn_id,customer_id,branch_id,txn_date,txn_time,amount,txn_type,channel,merchant_category,city,is_flagged,flag_reason,balance_after) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (txn_id, cid, bid, d.isoformat(), txn_time, amount, txn_type, channel, mcat, city, is_fraud, reason, bal_after)
            )
            txn_id_counter += 1
            txn_count += 1
        d += timedelta(days=1)
    conn.commit()
    print(f"  {txn_count:,} transactions generated ({fraud_count:,} flagged as fraud)")

    # Fraud cases for confirmed flagged transactions
    print("Generating fraud cases...")
    flagged = cur.execute("SELECT id,customer_id,txn_date,amount FROM transactions WHERE is_flagged=1 LIMIT 800").fetchall()
    fraud_types = ["Card Skimming","Phishing","Account Takeover","Synthetic Identity",
                    "Money Laundering","Unauthorized Transfer","Mobile Fraud","POS Tampering"]
    for txn_id, cust_id, txn_date, amount in flagged:
        if random.random() > 0.4:  # only ~60% become formal fraud cases
            continue
        detect_days = random.randint(0, 7)
        detect_date = (datetime.fromisoformat(txn_date) + timedelta(days=detect_days)).date().isoformat()
        status  = random.choices(["Confirmed","Dismissed","Under Review"], weights=[50,20,30])[0]
        res_days = random.randint(3, 45) if status != "Under Review" else None
        lost    = round(amount * random.uniform(0.3, 1.0), 2) if status == "Confirmed" else 0
        cur.execute(
            "INSERT INTO fraud_cases(txn_id,customer_id,detected_on,fraud_type,amount_lost,status,resolution_days) VALUES(?,?,?,?,?,?,?)",
            (txn_id, cust_id, detect_date, random.choice(fraud_types), lost, status, res_days)
        )
    conn.commit()
    fc = cur.execute("SELECT COUNT(*) FROM fraud_cases").fetchone()[0]
    print(f"  {fc} fraud cases created")

    # Risk scores
    print("Computing risk scores...")
    today = date.today().isoformat()
    for cid in cust_ids:
        stats = cur.execute("""
            SELECT COUNT(*) AS tc, SUM(is_flagged) AS fc,
                   MAX(amount) AS max_amt, AVG(amount) AS avg_amt,
                   SUM(CASE WHEN CAST(SUBSTR(txn_time,1,2) AS INTEGER) >= 22 OR CAST(SUBSTR(txn_time,1,2) AS INTEGER) <= 4 THEN 1 ELSE 0 END) AS odd_hrs,
                   COUNT(DISTINCT city) AS cities,
                   COUNT(DISTINCT txn_date) AS active_days
            FROM transactions WHERE customer_id=?
        """, (cid,)).fetchone()

        tc, fc, max_amt, avg_amt, odd_hrs, cities, active_days = stats

        if tc == 0:
            continue

        # Compute flags
        vel_flag   = 1 if (tc / max(active_days or 1, 1)) > 8 else 0
        large_flag = 1 if (max_amt or 0) > 100000 else 0
        odd_flag   = 1 if odd_hrs > (tc * 0.25) else 0
        city_flag  = 1 if (cities or 1) > 5 else 0

        # Risk score formula
        score = (fc / tc) * 50 + vel_flag * 20 + large_flag * 15 + odd_flag * 10 + city_flag * 5
        score = min(round(score, 2), 100)

        label = "Critical" if score >= 40 else "High" if score >= 25 else "Medium" if score >= 10 else "Low"

        cur.execute(
            "INSERT OR REPLACE INTO risk_scores(customer_id,risk_score,risk_label,velocity_flag,large_txn_flag,odd_hour_flag,multi_city_flag,computed_on) VALUES(?,?,?,?,?,?,?,?)",
            (cid, score, label, vel_flag, large_flag, odd_flag, city_flag, today)
        )
    conn.commit()
    print("  Risk scores computed")

    # Export CSVs
    for tbl in ("branches","customers","transactions","fraud_cases","risk_scores"):
        rows = cur.execute(f"SELECT * FROM {tbl}").fetchall()
        cols = [d[0] for d in cur.execute(f"PRAGMA table_info({tbl})").fetchall()]
        with open(f"data/{tbl}.csv", "w", newline="") as f:
            csv.writer(f).writerow(cols)
            csv.writer(f).writerows(rows)
        print(f"Exported data/{tbl}.csv ({len(rows):,} rows)")

    conn.close()
    print(f"\nDatabase ready: {DB_PATH}")
    print(f"  Transactions : {txn_count:,}")
    print(f"  Fraud txns   : {fraud_count:,} ({fraud_count/txn_count*100:.1f}%)")


if __name__ == "__main__":
    build_db()
