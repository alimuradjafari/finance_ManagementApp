# 💰 Personal Finance Management System
**SE-211: Software Design and Architecture — Lab 14**
**Class: BESE 15**

---

## 🏗️ Design Patterns Implemented

| Pattern | Type | File | Purpose |
|---|---|---|---|
| **Singleton** | Creational | `db/database.py` | Single MySQL connection instance |
| **Strategy** | Behavioral | `patterns/strategy.py` | Pluggable budgeting algorithms |
| **Composite** | Structural | `patterns/composite.py` | Account/portfolio hierarchy |
| **State** *(Bonus)* | Behavioral | `patterns/state.py` | Financial mode transitions |

---

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| Language | Python 3.10+ |
| Database | MySQL + mysql-connector-python |
| AI/ML | scikit-learn (Naive Bayes), pandas |
| Charts | Plotly |
| UI | Streamlit |
| DB Pattern | Singleton |

---

## ⚙️ Setup Instructions

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up MySQL Database
Make sure MySQL is running locally, then:
```bash
# Set environment variables (or edit schema.py directly)
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=your_password
export DB_NAME=finance_db

# Run schema creation
python db/schema.py
```

### 3. Run the Application
```bash
streamlit run app.py
```

> **Note:** If MySQL is not running, the app automatically falls back to **in-memory mode** using the sample data — perfect for demos without a database.

---

## 📁 Project Structure

```
finance_app/
├── app.py                  ← Main Streamlit UI
├── requirements.txt
├── db/
│   ├── database.py         ← Singleton DB Connection (MySQL)
│   ├── schema.py           ← MySQL table definitions
│   └── sample_data.py      ← Demo data
├── patterns/
│   ├── strategy.py         ← Strategy Pattern (budgeting)
│   ├── composite.py        ← Composite Pattern (accounts)
│   └── state.py            ← State Pattern (financial modes) [Bonus]
└── ai/
    └── engine.py           ← AI categorizer + recommendation engine
```

---

## 🖥️ Features

- **Dashboard** — Income/expense overview, budget allocation, portfolio summary
- **Transactions** — Add transactions with AI auto-categorization
- **Goals** — Track financial goals with progress bars
- **AI Recommendations** — State-aware, spending-pattern-based tips
- **Design Patterns Tab** — Live demo of all patterns with code snippets

---

## 🔌 MySQL Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DB_HOST` | `localhost` | MySQL host |
| `DB_USER` | `root` | MySQL username |
| `DB_PASSWORD` | *(empty)* | MySQL password |
| `DB_NAME` | `finance_db` | Database name |
