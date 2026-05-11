"""
Personal Finance Management System — Streamlit UI
SE-211 Lab 14 | BESE 15
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from db.database import DatabaseConnection
from patterns.strategy import BudgetContext, STRATEGIES
from patterns.composite import PortfolioManager
from patterns.state import FinancialContext, STATE_MAP
from ai.engine import RecommendationEngine, TransactionCategorizer


# ─── MySQL Data Loaders ───────────────────────────────────────────────────────
def load_transactions(user_id=1):
    """Load all transactions for a user from MySQL."""
    db = DatabaseConnection()
    cursor = db.execute(
        "SELECT id, description, amount, type, category, date "
        "FROM transactions WHERE user_id = %s ORDER BY date DESC",
        (user_id,)
    )
    if cursor is None:
        return []
    rows = cursor.fetchall()
    for row in rows:
        row["amount"] = float(row["amount"])
        if row["date"] is not None:
            row["date"] = str(row["date"])
    return rows


def load_goals(user_id=1):
    """Load all goals for a user from MySQL."""
    db = DatabaseConnection()
    cursor = db.execute(
        "SELECT id, name, target_amount AS target, current_amount AS current, "
        "deadline, status "
        "FROM goals WHERE user_id = %s",
        (user_id,)
    )
    if cursor is None:
        return []
    rows = cursor.fetchall()
    for row in rows:
        row["target"] = float(row["target"])
        row["current"] = float(row["current"])
        if row["deadline"] is not None:
            row["deadline"] = str(row["deadline"])
    return rows


def load_user(user_id=1):
    """Load user profile from MySQL."""
    db = DatabaseConnection()
    cursor = db.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    if cursor is None:
        return {"name": "Demo User", "monthly_income": 110000}
    row = cursor.fetchone()
    if row:
        row["monthly_income"] = float(row["monthly_income"])
        return row
    return {"name": "Demo User", "monthly_income": 110000}


def save_transaction(txn: dict, user_id=1):
    """Insert a new transaction into MySQL."""
    db = DatabaseConnection()
    db.execute(
        "INSERT INTO transactions (user_id, description, amount, type, category, date) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (user_id, txn["description"], txn["amount"], txn["type"], txn["category"], txn["date"])
    )


def save_goal(goal: dict, user_id=1):
    """Insert a new goal into MySQL."""
    db = DatabaseConnection()
    db.execute(
        "INSERT INTO goals (user_id, name, target_amount, current_amount, deadline) "
        "VALUES (%s, %s, %s, %s, %s)",
        (user_id, goal["name"], goal["target"], goal["current"], goal["deadline"])
    )

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinanceAI — Personal Finance System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Custom CSS (No sidebar, full page coverage) ─────────────────────────────
st.markdown("""
<style>
/* Import fonts */
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* Full page reset */
html, body, .stApp {
    margin: 0 !important;
    padding: 0 !important;
}

.stApp {
    background: #0a0f1e;
    font-family: 'Space Grotesk', sans-serif;
}

/* Hide Streamlit's default header/deploy bar and sidebar */
header[data-testid="stHeader"] {
    display: none !important;
}

[data-testid="stSidebar"] {
    display: none !important;
}

/* Remove top padding from main content */
.main .block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem;
    max-width: 1400px;
}

/* Headers */
h1, h2, h3, h4 { 
    color: #e2e8f0 !important; 
}

/* Metric cards */
[data-testid="metric-container"] {
    background: #111827;
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 16px;
}

/* Finance cards */
.finance-card {
    background: #111827;
    border: 1px solid #1e3a5f;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 16px;
}

.rec-card {
    background: linear-gradient(135deg, #0f1e38 0%, #1a2d4a 100%);
    border-left: 4px solid #3b82f6;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 10px;
    color: #cbd5e1;
    font-size: 0.92rem;
}

.goal-bar-wrap {
    background: #1a2332;
    border-radius: 20px;
    height: 10px;
    margin: 8px 0 4px;
    overflow: hidden;
}
.goal-bar-fill {
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    height: 100%;
    border-radius: 20px;
    transition: width 0.6s ease;
}

.state-badge {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 12px;
}

.tag {
    display: inline-block;
    background: #1e3a5f;
    color: #93c5fd;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.78rem;
    font-family: 'JetBrains Mono', monospace;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    color: white;
    border: none;
    border-radius: 8px;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    padding: 8px 20px;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    transform: translateY(-1px);
}

/* Selectbox, inputs */
.stSelectbox > div, .stNumberInput > div, .stTextInput > div {
    background: #111827 !important;
    border-color: #1e3a5f !important;
    color: #e2e8f0 !important;
}

.stDataFrame { 
    background: #111827 !important;
}

div[data-testid="stHorizontalBlock"] > div { 
    gap: 12px; 
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    background: #0d1327;
    border-radius: 10px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    color: #64748b;
    font-weight: 500;
    border-radius: 8px;
}
.stTabs [aria-selected="true"] {
    background: #1e3a5f !important;
    color: #e2e8f0 !important;
}

/* Radio buttons */
.stRadio div[role="radiogroup"] {
    background: #111827;
    padding: 8px;
    border-radius: 8px;
}

/* Code blocks */
pre {
    background: #0a0f1e !important;
}

/* Plotly charts container */
.js-plotly-plot {
    background: rgba(0,0,0,0) !important;
}

/* Info box */
.stAlert {
    background: #111827 !important;
    border-color: #1e3a5f !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Session State Init (loads from MySQL) ────────────────────────────────────
if "transactions" not in st.session_state:
    st.session_state.transactions = load_transactions()
if "goals" not in st.session_state:
    st.session_state.goals = load_goals()
if "user" not in st.session_state:
    st.session_state.user = load_user()
if "income" not in st.session_state:
    st.session_state.income = st.session_state.user.get("monthly_income", 110000)
if "financial_context" not in st.session_state:
    st.session_state.financial_context = FinancialContext()
if "budget_strategy" not in st.session_state:
    st.session_state.budget_strategy = "50/30/20 Rule"
if "portfolio" not in st.session_state:
    pm = PortfolioManager(st.session_state.user.get("name", "User"))
    pm.add_account("checking",   "HBL Checking",         45000)
    pm.add_account("savings",    "Meezan Savings",       185000)
    pm.add_account("savings",    "Allied Bank Savings",   60000)
    pm.add_account("investment", "PSX Stocks",            95000)
    pm.add_account("investment", "Meezan Mutual Fund",    75000)
    st.session_state.portfolio = pm

# DB connection status
db = DatabaseConnection()
db_connected = db.is_connected()

engine = RecommendationEngine()
categorizer = TransactionCategorizer()

# ─── Main Content ─────────────────────────────────────────────────────────────
st.markdown("# Personal Finance Management System")
st.markdown("*AI-powered insights | Design Patterns | SE-211 Lab 14*")
st.divider()

tabs = st.tabs(["📊 Dashboard", "💳 Transactions", "🎯 Goals", "🤖 AI Recommendations", "🏗️ Design Patterns", "⚙️ Settings"])

# ════════════════════════════════════════════════════════════
# TAB 1 — DASHBOARD
# ════════════════════════════════════════════════════════════
with tabs[0]:
    txns = st.session_state.transactions
    df = pd.DataFrame(txns) if txns else pd.DataFrame(
        columns=["id", "description", "amount", "type", "category", "date"]
    )
    income_txns  = df[df["type"] == "income"]["amount"].sum()     if not df.empty else 0.0
    expense_txns = df[df["type"] == "expense"]["amount"].sum()    if not df.empty else 0.0
    savings_txns = df[df["type"] == "savings"]["amount"].sum()    if not df.empty else 0.0
    invest_txns  = df[df["type"] == "investment"]["amount"].sum() if not df.empty else 0.0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💵 Total Income", f"PKR {income_txns:,.0f}")
    col2.metric("💸 Total Expenses", f"PKR {expense_txns:,.0f}", delta=f"-{(expense_txns/income_txns*100):.1f}%" if income_txns else None, delta_color="inverse")
    col3.metric("🏦 Savings", f"PKR {savings_txns:,.0f}")
    col4.metric("📈 Investments", f"PKR {invest_txns:,.0f}")

    st.markdown("")
    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown("#### Expense Breakdown by Category")
        exp_df = df[df["type"] == "expense"].groupby("category")["amount"].sum().reset_index()
        if not exp_df.empty:
            fig = px.pie(
                exp_df, names="category", values="amount",
                hole=0.55,
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e2e8f0",
                showlegend=True,
                legend=dict(bgcolor="rgba(0,0,0,0)"),
                margin=dict(t=20, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown("#### Budget Allocation")
        ctx = BudgetContext(STRATEGIES[st.session_state.budget_strategy]())
        alloc = ctx.get_allocation(st.session_state.income)
        st.markdown(f"**Strategy:** {alloc.label}")
        st.markdown(f"""
<div class='finance-card'>
<table style='width:100%;color:#cbd5e1;font-size:0.9rem'>
<tr><td>🏠 Needs</td><td style='text-align:right;color:#3b82f6;font-weight:600'>PKR {alloc.needs:,.0f}</td></tr>
<tr><td>🎯 Wants</td><td style='text-align:right;color:#8b5cf6;font-weight:600'>PKR {alloc.wants:,.0f}</td></tr>
<tr><td>🏦 Savings</td><td style='text-align:right;color:#10b981;font-weight:600'>PKR {alloc.savings:,.0f}</td></tr>
<tr><td>📈 Invest</td><td style='text-align:right;color:#f59e0b;font-weight:600'>PKR {alloc.investments:,.0f}</td></tr>
</table>
<br/><small style='color:#64748b'>{ctx.get_description().replace(chr(10),'<br/>')}</small>
</div>
""", unsafe_allow_html=True)

        st.markdown("#### Portfolio Balance")
        summary = st.session_state.portfolio.get_summary()
        st.markdown(f"""
<div class='finance-card'>
<div style='font-size:1.5rem;font-weight:700;color:#3b82f6'>PKR {summary['total']:,.0f}</div>
<div style='color:#64748b;font-size:0.8rem;margin-bottom:12px'>Total Portfolio Value</div>
<table style='width:100%;color:#cbd5e1;font-size:0.88rem'>
<tr><td>🏦 Savings</td><td style='text-align:right'>PKR {summary['savings']:,.0f}</td></tr>
<tr><td>💳 Checking</td><td style='text-align:right'>PKR {summary['checking']:,.0f}</td></tr>
<tr><td>📈 Investments</td><td style='text-align:right'>PKR {summary['investments']:,.0f}</td></tr>
</table>
</div>
""", unsafe_allow_html=True)

    # Monthly trend
    st.markdown("#### Monthly Cash Flow")
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.strftime("%b %d")
        monthly = df.groupby(["month", "type"])["amount"].sum().reset_index()
        fig2 = px.bar(
            monthly, x="month", y="amount", color="type", barmode="group",
            color_discrete_map={
                "income": "#3b82f6", "expense": "#ef4444",
                "savings": "#10b981", "investment": "#8b5cf6"
            }
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0", legend=dict(bgcolor="rgba(0,0,0,0)"),
            margin=dict(t=10, b=10), xaxis=dict(gridcolor="#1e3a5f"),
            yaxis=dict(gridcolor="#1e3a5f")
        )
        st.plotly_chart(fig2, use_container_width=True)

# ════════════════════════════════════════════════════════════
# TAB 2 — TRANSACTIONS
# ════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("### ➕ Add New Transaction")
    with st.container():
        c1, c2, c3 = st.columns(3)
        with c1:
            desc = st.text_input("Description", placeholder="e.g. KFC chicken meal")
            amount = st.number_input("Amount (PKR)", min_value=0.0, step=100.0)
        with c2:
            txn_type = st.selectbox("Type", ["expense", "income", "savings", "investment"])
            txn_date = st.date_input("Date", value=date.today())
        with c3:
            if desc:
                predicted_cat = categorizer.predict(desc)
                st.markdown(f"**🤖 AI Predicted Category:**")
                st.markdown(f"<span class='tag'>{predicted_cat}</span>", unsafe_allow_html=True)
                manual_cat = st.text_input("Override Category (optional)")
            else:
                predicted_cat = "Uncategorized"
                manual_cat = st.text_input("Category")

        if st.button("➕ Add Transaction", type="primary"):
            if desc and amount > 0:
                final_cat = manual_cat if manual_cat else predicted_cat
                new_txn = {
                    "id": len(st.session_state.transactions) + 1,
                    "description": desc,
                    "amount": amount,
                    "type": txn_type,
                    "category": final_cat,
                    "date": str(txn_date)
                }
                save_transaction(new_txn)
                st.session_state.transactions = load_transactions()
                st.success(f"✅ Transaction saved to MySQL! Category: **{final_cat}**")
                st.rerun()

    st.divider()
    st.markdown("### 📋 Transaction History")

    filter_type = st.multiselect(
        "Filter by Type", ["income", "expense", "savings", "investment"],
        default=["income", "expense", "savings", "investment"]
    )

    display_df = pd.DataFrame(st.session_state.transactions)
    if filter_type and not display_df.empty:
        display_df = display_df[display_df["type"].isin(filter_type)]

    if not display_df.empty:
        display_df = display_df.sort_values("date", ascending=False)
        display_df["amount"] = display_df["amount"].apply(lambda x: f"PKR {x:,.0f}")
        st.dataframe(
            display_df[["date", "description", "type", "category", "amount"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No transactions found. Add your first transaction above!")

# ════════════════════════════════════════════════════════════
# TAB 3 — GOALS
# ════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("### 🎯 Financial Goals Tracker")

    col_a, col_b = st.columns([3, 2])

    with col_a:
        if st.session_state.goals:
            for goal in st.session_state.goals:
                pct = min(100, (goal["current"] / goal["target"]) * 100)
                color = "#10b981" if pct >= 100 else "#3b82f6" if pct >= 50 else "#f59e0b"
                status_icon = "🏆" if pct >= 100 else "🚀" if pct >= 50 else "⏳"
                st.markdown(f"""
<div class='finance-card'>
  <div style='display:flex;justify-content:space-between;align-items:center'>
    <div style='font-weight:600;font-size:1rem;color:#e2e8f0'>{status_icon} {goal['name']}</div>
    <div style='color:{color};font-weight:700'>{pct:.0f}%</div>
  </div>
  <div style='color:#64748b;font-size:0.82rem;margin:4px 0'>
    PKR {goal['current']:,.0f} / PKR {goal['target']:,.0f}
    &nbsp;·&nbsp; Deadline: {goal['deadline']}
  </div>
  <div class='goal-bar-wrap'>
    <div class='goal-bar-fill' style='width:{pct}%;background:linear-gradient(90deg,{color},{color}99)'></div>
  </div>
  <div style='color:#475569;font-size:0.8rem'>
    Remaining: PKR {max(0, goal['target'] - goal['current']):,.0f}
  </div>
</div>
""", unsafe_allow_html=True)
        else:
            st.info("No goals set. Add your first goal on the right!")

    with col_b:
        st.markdown("### ➕ Add New Goal")
        g_name = st.text_input("Goal Name", placeholder="e.g. Vacation Fund")
        g_target = st.number_input("Target Amount (PKR)", min_value=0.0, step=1000.0)
        g_current = st.number_input("Current Savings (PKR)", min_value=0.0, step=100.0)
        g_deadline = st.date_input("Deadline")

        if st.button("Add Goal", type="primary"):
            if g_name and g_target > 0:
                new_goal = {
                    "name": g_name,
                    "target": g_target,
                    "current": g_current,
                    "deadline": str(g_deadline)
                }
                save_goal(new_goal)
                st.session_state.goals = load_goals()
                st.success(f"✅ Goal '{g_name}' saved to MySQL!")
                st.rerun()

        # Goals progress chart
        if st.session_state.goals:
            st.markdown("#### Goals Overview")
            goals_df = pd.DataFrame(st.session_state.goals)
            goals_df["progress"] = (goals_df["current"] / goals_df["target"] * 100).clip(0, 100)
            fig = px.bar(
                goals_df, x="name", y="progress",
                color="progress",
                color_continuous_scale=["#ef4444", "#f59e0b", "#10b981"],
                range_color=[0, 100]
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e2e8f0", showlegend=False,
                yaxis_title="% Complete", xaxis_title="",
                margin=dict(t=10, b=10),
                xaxis=dict(gridcolor="#1e3a5f"), yaxis=dict(gridcolor="#1e3a5f")
            )
            st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════════
# TAB 4 — AI RECOMMENDATIONS
# ════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("### 🤖 AI-Powered Financial Recommendations")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### 🔍 Transaction Categorizer")
        st.caption("Try the AI categorizer — type any transaction description:")
        test_desc = st.text_input("Transaction Description", placeholder="e.g. Careem food delivery order")
        if test_desc:
            pred = categorizer.predict(test_desc)
            probs = categorizer.predict_proba(test_desc)
            top3 = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:3]
            st.markdown(f"**Predicted:** <span class='tag'>{pred}</span>", unsafe_allow_html=True)
            st.markdown("**Confidence scores:**")
            for cat, prob in top3:
                st.progress(prob, text=f"{cat}: {prob*100:.1f}%")

    with col2:
        st.markdown("#### 🔄 Current Financial Mode")
        state = st.session_state.financial_context.get_state()
        st.markdown(f"""
<div class='finance-card' style='border-color:{state.get_color()}44'>
  <div style='font-size:1.4rem'>{state.get_icon()} <b>{state.get_name()}</b></div>
  <div style='color:#64748b;font-size:0.85rem;margin-top:4px'>
    Recommendations are tailored to your current mode. Change mode in Settings tab.
  </div>
</div>
""", unsafe_allow_html=True)

    st.divider()
    st.markdown("#### 💡 Personalized Recommendations")

    df_txns = pd.DataFrame(st.session_state.transactions)
    if not df_txns.empty:
        income_total = df_txns[df_txns["type"] == "income"]["amount"].sum()
        expense_total = df_txns[df_txns["type"] == "expense"]["amount"].sum()
        savings_rate = ((income_total - expense_total) / income_total * 100) if income_total > 0 else 0

        context_data = {
            "savings_rate": savings_rate,
            "dining_pct": (df_txns[df_txns["category"] == "Food & Dining"]["amount"].sum() / income_total * 100) if income_total > 0 else 0,
            "entertainment_pct": (df_txns[df_txns["category"] == "Entertainment"]["amount"].sum() / income_total * 100) if income_total > 0 else 0,
            "investment_pct": (df_txns[df_txns["type"] == "investment"]["amount"].sum() / income_total * 100) if income_total > 0 else 0,
        }

        state = st.session_state.financial_context.get_state()
        state_recs = st.session_state.financial_context.get_recommendations(context_data)
        st.markdown(f"**From {state.get_icon()} {state.get_name()}:**")
        for rec in state_recs:
            st.markdown(f"<div class='rec-card' style='border-color:{state.get_color()}'>{rec}</div>", unsafe_allow_html=True)

        st.markdown("")
        st.markdown("**📊 From Spending Analysis:**")
        ai_recs = engine.analyze(
            st.session_state.transactions,
            income_total,
            st.session_state.goals
        )
        for rec in ai_recs:
            st.markdown(f"<div class='rec-card'>{rec}</div>", unsafe_allow_html=True)
    else:
        st.info("Add some transactions to see personalized recommendations!")

# ════════════════════════════════════════════════════════════
# TAB 5 — DESIGN PATTERNS
# ════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("### 🏗️ Design Patterns Applied")
    st.caption("SE-211 Lab 14 — CLO3 & CLO4 Evidence")

    p1, p2 = st.columns(2)

    with p1:
        st.markdown("""
<div class='finance-card'>
<h4>🔒 Singleton Pattern</h4>
<span class='tag'>Creational</span>&nbsp;<span class='tag'>db/database.py</span>
<p style='color:#94a3b8;margin-top:10px;font-size:0.9rem'>
Ensures only one MySQL database connection exists throughout the app's lifetime.
Any module that calls <code>DatabaseConnection()</code> receives the same instance — 
preventing connection leaks and race conditions.
</p>
<pre style='background:#0a0f1e;padding:12px;border-radius:8px;font-size:0.78rem;color:#7dd3fc'>
class DatabaseConnection:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connect()  # Only once!
        return cls._instance
</pre>
</div>
""", unsafe_allow_html=True)

        st.markdown("""
<div class='finance-card'>
<h4>🎯 Strategy Pattern</h4>
<span class='tag'>Behavioral</span>&nbsp;<span class='tag'>patterns/strategy.py</span>
<p style='color:#94a3b8;margin-top:10px;font-size:0.9rem'>
Different budgeting algorithms (50/30/20, Zero-Based, Aggressive Savings) are 
encapsulated as interchangeable strategies. The BudgetContext switches between 
them at runtime without changing any client code — perfect SOLID Open/Closed Principle.
</p>
</div>
""", unsafe_allow_html=True)

    with p2:
        st.markdown("""
<div class='finance-card'>
<h4>🌳 Composite Pattern</h4>
<span class='tag'>Structural</span>&nbsp;<span class='tag'>patterns/composite.py</span>
<p style='color:#94a3b8;margin-top:10px;font-size:0.9rem'>
Financial accounts are organized in a tree. Individual Account (leaf) and AccountGroup 
(composite) share the same interface — so <code>get_balance()</code> works identically 
on a single account or an entire group of accounts.
</p>
</div>
""", unsafe_allow_html=True)
        portfolio_tree = st.session_state.portfolio.display_tree()
        st.code(portfolio_tree, language=None)

        st.markdown("""
<div class='finance-card'>
<h4>🔄 State Pattern <span style='color:#f59e0b;font-size:0.75rem'>BONUS</span></h4>
<span class='tag'>Behavioral</span>&nbsp;<span class='tag'>patterns/state.py</span>
<p style='color:#94a3b8;margin-top:10px;font-size:0.9rem'>
The system transitions between Budgeting, Savings, and Investment modes. Each state 
defines its own recommendation behavior — the FinancialContext delegates to the 
current state without knowing its concrete type.
</p>
</div>
""", unsafe_allow_html=True)

    st.divider()
    st.markdown("### 📐 SOLID Principles Applied")
    solid_cols = st.columns(5)
    solid = [
        ("S", "Single Responsibility", "Each class has one job"),
        ("O", "Open/Closed", "Add new strategies without modifying existing code"),
        ("L", "Liskov Substitution", "Any subclass can replace its parent"),
        ("I", "Interface Segregation", "Minimal, focused interfaces"),
        ("D", "Dependency Inversion", "Depend on abstractions, not concretions"),
    ]
    for col, (letter, name, desc) in zip(solid_cols, solid):
        col.markdown(f"""
<div class='finance-card' style='text-align:center'>
<div style='font-size:2rem;font-weight:700;color:#3b82f6'>{letter}</div>
<div style='font-weight:600;color:#e2e8f0;font-size:0.85rem'>{name}</div>
<div style='color:#64748b;font-size:0.78rem;margin-top:8px'>{desc}</div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# TAB 6 — SETTINGS (formerly Sidebar)
# ════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown("### ⚙️ Application Settings")
    
    col_s1, col_s2 = st.columns(2)
    
    with col_s1:
        st.markdown("#### 👤 Profile")
        st.session_state.income = st.number_input(
            "Monthly Income (PKR)", 
            value=float(st.session_state.income),
            min_value=0.0, 
            step=5000.0, 
            format="%.0f",
            key="income_input"
        )
        
        st.divider()
        
        st.markdown("#### 📊 Budget Strategy")
        selected_strategy = st.selectbox(
            "Select Budget Strategy", 
            list(STRATEGIES.keys()),
            index=list(STRATEGIES.keys()).index(st.session_state.budget_strategy),
            key="strategy_select"
        )
        st.session_state.budget_strategy = selected_strategy
        
        # Show current strategy description
        ctx = BudgetContext(STRATEGIES[st.session_state.budget_strategy]())
        st.info(f"**Current Strategy:** {ctx.get_description()}")
    
    with col_s2:
        st.markdown("#### 🔄 Financial Mode")
        st.markdown("*(State Pattern — Bonus Task)*")
        mode = st.radio(
            "Select Financial Mode",
            list(STATE_MAP.keys()),
            index=list(STATE_MAP.keys()).index(
                st.session_state.financial_context.get_state_name()
            ),
            key="mode_radio"
        )
        if mode != st.session_state.financial_context.get_state_name():
            st.session_state.financial_context.transition_to(STATE_MAP[mode]())
        
        current_state = st.session_state.financial_context.get_state()
        st.markdown(
            f"<div class='state-badge' style='background:{current_state.get_color()}22;"
            f"color:{current_state.get_color()};border:1px solid {current_state.get_color()}44'>"
            f"{current_state.get_icon()} Current: {current_state.get_name()}</div>",
            unsafe_allow_html=True
        )
        
        st.divider()
        
        st.markdown("#### 🗄️ Database Status")
        st.markdown("<span class='tag'>Singleton Pattern</span>", unsafe_allow_html=True)
        if db_connected:
            st.success("✅ MySQL Connected", icon="✅")
        else:
            st.error("⚠️ MySQL Offline", icon="⚠️")
        st.caption("Single connection instance shared across all modules.")