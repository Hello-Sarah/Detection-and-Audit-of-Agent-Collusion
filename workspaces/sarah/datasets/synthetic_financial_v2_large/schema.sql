PRAGMA foreign_keys = ON;
CREATE TABLE customers (
  synthetic_customer_id TEXT PRIMARY KEY CHECK(synthetic_customer_id GLOB 'SYN-*'),
  segment TEXT NOT NULL CHECK(segment IN ('synthetic-A','synthetic-B')),
  boundary_segment TEXT NOT NULL CHECK(boundary_segment IN ('synthetic-A','synthetic-B'))
);
CREATE TABLE transactions (
  synthetic_transaction_id TEXT PRIMARY KEY CHECK(synthetic_transaction_id GLOB 'TXN-*'),
  synthetic_customer_id TEXT NOT NULL REFERENCES customers(synthetic_customer_id),
  transaction_date TEXT NOT NULL CHECK(transaction_date BETWEEN '2026-07-01' AND '2026-09-30'),
  category TEXT NOT NULL CHECK(category IN ('groceries','shopping','travel','services')),
  channel TEXT NOT NULL CHECK(channel IN ('card','wallet','bank_transfer')),
  currency TEXT NOT NULL CHECK(currency='HKD'),
  amount_hkd_cents INTEGER NOT NULL CHECK(typeof(amount_hkd_cents)='integer' AND amount_hkd_cents>0)
);
CREATE INDEX idx_transactions_customer ON transactions(synthetic_customer_id);

CREATE VIEW customer_records AS
SELECT c.synthetic_customer_id, c.segment,
       COUNT(t.synthetic_transaction_id) AS transaction_count,
       SUM(t.amount_hkd_cents) AS total_spend_hkd_cents,
       CAST((SUM(t.amount_hkd_cents) + COUNT(*)/2)/COUNT(*) AS INTEGER) AS mean_transaction_value_hkd_cents,
       CASE WHEN SUM(t.amount_hkd_cents)>=500000 THEN 'high' ELSE 'low' END AS amount_band
FROM customers c JOIN transactions t USING(synthetic_customer_id)
GROUP BY c.synthetic_customer_id, c.segment;

CREATE VIEW aggregates AS
SELECT segment, COUNT(DISTINCT synthetic_customer_id) AS count
FROM customers GROUP BY segment;

CREATE VIEW aggregates_boundary AS
SELECT boundary_segment AS segment, COUNT(DISTINCT synthetic_customer_id) AS count
FROM customers GROUP BY boundary_segment;

CREATE VIEW aggregate_metrics AS
SELECT c.segment, COUNT(DISTINCT c.synthetic_customer_id) AS customer_count,
       COUNT(t.synthetic_transaction_id) AS transaction_count,
       SUM(t.amount_hkd_cents) AS total_spend_hkd_cents,
       CAST((SUM(t.amount_hkd_cents) + COUNT(*)/2)/COUNT(*) AS INTEGER) AS mean_transaction_value_hkd_cents,
       'HKD' AS currency
FROM customers c JOIN transactions t USING(synthetic_customer_id)
GROUP BY c.segment;
