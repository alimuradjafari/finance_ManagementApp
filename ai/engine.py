"""
AI Recommendation Engine — Transaction Categorization + Smart Tips
SE-211 Lab 14: Personal Finance Management System
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


# ─────────────────────────────────────────────
# Training data for transaction categorizer
# ─────────────────────────────────────────────
TRAINING_DATA = [
    # Food & Dining
    ("mcdonalds burger meal", "Food & Dining"),
    ("kfc chicken lunch", "Food & Dining"),
    ("pizza hut order", "Food & Dining"),
    ("grocery store weekly", "Food & Dining"),
    ("imtiaz supermarket", "Food & Dining"),
    ("careem food delivery", "Food & Dining"),
    ("chai dhaba tea", "Food & Dining"),
    ("restaurant dinner", "Food & Dining"),

    # Transport
    ("careem ride", "Transport"),
    ("uber cab", "Transport"),
    ("petrol pump fuel", "Transport"),
    ("cng station gas", "Transport"),
    ("bus ticket metro", "Transport"),
    ("rickshaw fare", "Transport"),
    ("toll plaza highway", "Transport"),

    # Utilities
    ("wapda electricity bill", "Utilities"),
    ("sui gas bill", "Utilities"),
    ("internet ptcl broadband", "Utilities"),
    ("jazz mobile recharge", "Utilities"),
    ("zong data package", "Utilities"),
    ("water bill municipality", "Utilities"),

    # Entertainment
    ("netflix subscription", "Entertainment"),
    ("youtube premium", "Entertainment"),
    ("cinema ticket movie", "Entertainment"),
    ("spotify music", "Entertainment"),
    ("steam game purchase", "Entertainment"),
    ("concert show tickets", "Entertainment"),

    # Health
    ("pharmacy medicine", "Health"),
    ("doctor consultation fee", "Health"),
    ("hospital lab test", "Health"),
    ("gym membership fitness", "Health"),
    ("shifa hospital", "Health"),

    # Education
    ("university fee tuition", "Education"),
    ("books stationary store", "Education"),
    ("online course udemy", "Education"),
    ("coaching center fee", "Education"),

    # Shopping
    ("daraz online shopping", "Shopping"),
    ("clothes garments store", "Shopping"),
    ("electronics laptop", "Shopping"),
    ("shoes footwear", "Shopping"),
    ("amazon purchase", "Shopping"),

    # Income
    ("salary credit", "Income"),
    ("freelance payment received", "Income"),
    ("bank interest credited", "Income"),
    ("dividend payment", "Income"),
    ("rental income received", "Income"),

    # Savings & Investments
    ("mutual fund investment", "Investment"),
    ("stocks purchased", "Investment"),
    ("savings deposit", "Savings"),
    ("fixed deposit fd", "Savings"),
    ("meezan bank saving", "Savings"),
]

TEXTS = [t for t, _ in TRAINING_DATA]
LABELS = [l for _, l in TRAINING_DATA]


class TransactionCategorizer:
    """AI model to auto-categorize transaction descriptions."""

    def __init__(self):
        self.model = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
            ("clf", MultinomialNB(alpha=0.5)),
        ])
        self.model.fit(TEXTS, LABELS)

    def predict(self, description: str) -> str:
        return self.model.predict([description.lower()])[0]

    def predict_proba(self, description: str) -> dict:
        classes = self.model.classes_
        probs = self.model.predict_proba([description.lower()])[0]
        return dict(zip(classes, probs))


class RecommendationEngine:
    """Generates personalized financial recommendations from spending data."""

    def __init__(self):
        self.categorizer = TransactionCategorizer()

    def analyze(self, transactions: list, income: float, goals: list) -> list:
        """Main method — returns list of recommendation strings."""
        if not transactions:
            return ["Add some transactions to get personalized recommendations!"]

        df = pd.DataFrame(transactions)
        recommendations = []

        # ── Spending analysis ──────────────────────────────────────
        expenses = df[df["type"] == "expense"] if "type" in df.columns else df
        total_expense = expenses["amount"].sum() if len(expenses) > 0 else 0

        if income > 0:
            expense_ratio = (total_expense / income) * 100
            savings_rate = max(0, ((income - total_expense) / income) * 100)

            if expense_ratio > 90:
                recommendations.append(
                    f"🚨 You're spending {expense_ratio:.1f}% of income. "
                    "Aim to keep expenses below 80%."
                )
            elif expense_ratio > 70:
                recommendations.append(
                    f"⚠️ Expenses are at {expense_ratio:.1f}% of income. "
                    "Consider reducing non-essential spending."
                )
            else:
                recommendations.append(
                    f"✅ Healthy! Spending {expense_ratio:.1f}% of income. Keep it up."
                )

            if savings_rate < 10:
                recommendations.append(
                    "💡 Savings rate is low. Try automating a fixed amount to savings each month."
                )
            elif savings_rate >= 20:
                recommendations.append(
                    f"🌟 Excellent {savings_rate:.1f}% savings rate! Consider investing the surplus."
                )

        # ── Category breakdown tips ────────────────────────────────
        if "category" in df.columns and len(expenses) > 0:
            cat_totals = expenses.groupby("category")["amount"].sum()
            top_category = cat_totals.idxmax() if len(cat_totals) > 0 else None

            if top_category == "Food & Dining" and income > 0:
                food_pct = (cat_totals["Food & Dining"] / income) * 100
                if food_pct > 20:
                    recommendations.append(
                        f"🍽️ Food & Dining is {food_pct:.1f}% of income. "
                        "Try meal prepping to cut this by 30%."
                    )

            if "Entertainment" in cat_totals and income > 0:
                ent_pct = (cat_totals["Entertainment"] / income) * 100
                if ent_pct > 10:
                    recommendations.append(
                        f"🎬 Entertainment at {ent_pct:.1f}% is high. "
                        "Audit subscriptions — cancel unused ones."
                    )

        # ── Goal recommendations ───────────────────────────────────
        for goal in goals:
            progress = (goal.get("current", 0) / goal.get("target", 1)) * 100
            if progress < 25:
                recommendations.append(
                    f"🎯 Goal '{goal['name']}' is only {progress:.0f}% funded. "
                    "Increase monthly contributions."
                )
            elif progress >= 100:
                recommendations.append(
                    f"🏆 Goal '{goal['name']}' achieved! Set a new financial milestone."
                )

        # ── Investment nudge ───────────────────────────────────────
        has_investment = any(t.get("type") == "investment" for t in transactions)
        if not has_investment:
            recommendations.append(
                "📈 No investments recorded. Consider starting with a mutual fund "
                "or index fund for long-term wealth growth."
            )

        return recommendations if recommendations else ["Your finances look balanced — keep it up! 🎉"]
