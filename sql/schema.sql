-- Banking Risk & Fraud Analytics — SQLite Schema

CREATE TABLE IF NOT EXISTS branches (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    code      TEXT NOT NULL UNIQUE,
    name      TEXT NOT NULL,
    city      TEXT NOT NULL,
    region    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS customers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id     TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    age             INTEGER NOT NULL,
    gender          TEXT NOT NULL,
    city            TEXT NOT NULL,
    account_type    TEXT NOT NULL CHECK (account_type IN ('Savings','Current','Salary','Fixed Deposit')),
    branch_id       INTEGER NOT NULL REFERENCES branches(id),
    account_balance REAL NOT NULL DEFAULT 0,
    credit_score    INTEGER NOT NULL DEFAULT 700,
    kyc_status      TEXT NOT NULL DEFAULT 'Verified' CHECK (kyc_status IN ('Verified','Pending','Rejected')),
    opened_on       TEXT NOT NULL,
    is_active       INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS transactions (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    txn_id           TEXT NOT NULL UNIQUE,
    customer_id      INTEGER NOT NULL REFERENCES customers(id),
    branch_id        INTEGER REFERENCES branches(id),
    txn_date         TEXT NOT NULL,
    txn_time         TEXT NOT NULL,
    amount           REAL NOT NULL,
    txn_type         TEXT NOT NULL CHECK (txn_type IN ('Credit','Debit')),
    channel          TEXT NOT NULL CHECK (channel IN ('ATM','Online','Branch','Mobile','POS')),
    merchant_category TEXT,
    city             TEXT,
    is_flagged       INTEGER DEFAULT 0,
    flag_reason      TEXT,
    balance_after    REAL NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS fraud_cases (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    txn_id           INTEGER NOT NULL REFERENCES transactions(id),
    customer_id      INTEGER NOT NULL REFERENCES customers(id),
    detected_on      TEXT NOT NULL,
    fraud_type       TEXT NOT NULL,
    amount_lost      REAL NOT NULL DEFAULT 0,
    status           TEXT NOT NULL DEFAULT 'Under Review' CHECK (status IN ('Confirmed','Dismissed','Under Review')),
    resolution_days  INTEGER
);

CREATE TABLE IF NOT EXISTS risk_scores (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id     INTEGER NOT NULL REFERENCES customers(id) UNIQUE,
    risk_score      REAL NOT NULL DEFAULT 0,
    risk_label      TEXT NOT NULL DEFAULT 'Low',
    velocity_flag   INTEGER DEFAULT 0,
    large_txn_flag  INTEGER DEFAULT 0,
    odd_hour_flag   INTEGER DEFAULT 0,
    multi_city_flag INTEGER DEFAULT 0,
    computed_on     TEXT NOT NULL
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_txn_date      ON transactions(txn_date);
CREATE INDEX IF NOT EXISTS idx_txn_customer  ON transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_txn_flagged   ON transactions(is_flagged);
CREATE INDEX IF NOT EXISTS idx_risk_label    ON risk_scores(risk_label);
CREATE INDEX IF NOT EXISTS idx_cust_branch   ON customers(branch_id);
