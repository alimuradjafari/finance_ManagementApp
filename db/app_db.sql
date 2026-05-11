-- ============================================================
-- Personal Finance Management System — Database Schema
-- SE-211: Software Design and Architecture | Lab 14 | BESE 15
-- ============================================================
-- HOW TO USE:
--   1. Open MySQL Workbench
--   2. Connect to your local MySQL server
--   3. Go to: File > Open SQL Script > select this file
--   4. Click the lightning bolt (⚡) to execute
-- ============================================================

-- Create & select the database
CREATE DATABASE IF NOT EXISTS finance_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE finance_db;

-- ────────────────────────────────────────────
-- TABLE: users
-- ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100)    NOT NULL,
    email           VARCHAR(150)    NOT NULL UNIQUE,
    monthly_income  DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);

-- ────────────────────────────────────────────
-- TABLE: transactions
-- ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS transactions (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT             NOT NULL,
    description VARCHAR(255)    NOT NULL,
    amount      DECIMAL(12,2)   NOT NULL,
    type        ENUM('income','expense','investment','savings') NOT NULL,
    category    VARCHAR(100),
    date        DATE            NOT NULL,
    created_at  TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ────────────────────────────────────────────
-- TABLE: goals
-- ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS goals (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT             NOT NULL,
    name            VARCHAR(150)    NOT NULL,
    target_amount   DECIMAL(12,2)   NOT NULL,
    current_amount  DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    deadline        DATE,
    status          ENUM('active','completed','paused') DEFAULT 'active',
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ────────────────────────────────────────────
-- TABLE: recommendations
-- ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS recommendations (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT     NOT NULL,
    message         TEXT    NOT NULL,
    category        VARCHAR(100),
    generated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- SAMPLE DATA (optional — for demo purposes)
-- ============================================================

INSERT IGNORE INTO users (id, name, email, monthly_income) VALUES
(1, 'Ali', 'demo@financeai.com', 110000.00);

INSERT IGNORE INTO transactions (user_id, description, amount, type, category, date) VALUES
(1, 'Monthly Salary',               85000.00, 'income',     'Income',        '2026-04-01'),
(1, 'Imtiaz Supermarket grocery',    8500.00, 'expense',    'Food & Dining', '2026-04-03'),
(1, 'WAPDA electricity bill',        4200.00, 'expense',    'Utilities',     '2026-04-05'),
(1, 'Careem ride to office',          650.00, 'expense',    'Transport',     '2026-04-06'),
(1, 'Netflix subscription',          1500.00, 'expense',    'Entertainment', '2026-04-07'),
(1, 'Meezan Bank savings deposit',  10000.00, 'savings',    'Savings',       '2026-04-08'),
(1, 'KFC chicken dinner',            2800.00, 'expense',    'Food & Dining', '2026-04-10'),
(1, 'Petrol pump fuel',              3500.00, 'expense',    'Transport',     '2026-04-11'),
(1, 'Shifa Hospital lab test',       2200.00, 'expense',    'Health',        '2026-04-12'),
(1, 'Mutual fund investment',        5000.00, 'investment', 'Investment',    '2026-04-13'),
(1, 'Daraz online shopping',         4500.00, 'expense',    'Shopping',      '2026-04-14'),
(1, 'Jazz mobile recharge',           500.00, 'expense',    'Utilities',     '2026-04-15'),
(1, 'Pizza Hut order',               1800.00, 'expense',    'Food & Dining', '2026-04-17'),
(1, 'Freelance web project payment', 25000.00, 'income',    'Income',        '2026-04-18'),
(1, 'Udemy online course',           2000.00, 'expense',    'Education',     '2026-04-19'),
(1, 'Careem Food delivery',           900.00, 'expense',    'Food & Dining', '2026-04-20'),
(1, 'Gym membership fee',            3000.00, 'expense',    'Health',        '2026-04-21'),
(1, 'Cinema ticket Cinepax',         1200.00, 'expense',    'Entertainment', '2026-04-22'),
(1, 'SUI gas bill',                  1800.00, 'expense',    'Utilities',     '2026-04-25'),
(1, 'Stocks purchased PSX',          8000.00, 'investment', 'Investment',    '2026-04-28'),
(1, 'Restaurant dinner family',      5500.00, 'expense',    'Food & Dining', '2026-04-29'),
(1, 'Spotify music subscription',     400.00, 'expense',    'Entertainment', '2026-04-30');

INSERT IGNORE INTO goals (user_id, name, target_amount, current_amount, deadline, status) VALUES
(1, 'Emergency Fund',       300000.00,  85000.00, '2026-12-31', 'active'),
(1, 'Vacation to Thailand', 150000.00,  45000.00, '2026-09-01', 'active'),
(1, 'New Laptop',           120000.00, 110000.00, '2026-06-01', 'active'),
(1, 'Investment Portfolio', 500000.00,  65000.00, '2027-12-31', 'active');

-- ============================================================
-- VERIFY — run these SELECT statements to confirm setup
-- ============================================================

SELECT "users"        AS table_name, COUNT(*) AS row_s FROM users
UNION ALL
SELECT 'transactions' AS table_name, COUNT(*) AS row_s FROM transactions
UNION ALL
SELECT 'goals'        AS table_name, COUNT(*) AS row_s FROM goals
UNION ALL
SELECT 'recommendations', COUNT(*) FROM recommendations;