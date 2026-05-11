"""
State Pattern — Financial Mode Management (Bonus Task)
SE-211 Lab 14: Personal Finance Management System
"""

from abc import ABC, abstractmethod


class FinancialState(ABC):
    """Abstract state base class."""

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_recommendations(self, data: dict) -> list:
        pass

    @abstractmethod
    def get_color(self) -> str:
        pass

    @abstractmethod
    def get_icon(self) -> str:
        pass


class BudgetingMode(FinancialState):
    """User is focused on controlling expenses."""

    def get_name(self) -> str:
        return "Budgeting Mode"

    def get_color(self) -> str:
        return "#f59e0b"

    def get_icon(self) -> str:
        return "📊"

    def get_recommendations(self, data: dict) -> list:
        tips = [
            "Track every expense this week — awareness is the first step.",
            "Identify your top 3 spending categories and set limits.",
            "Use cash envelopes for discretionary spending to stay on track.",
        ]
        if data.get("dining_pct", 0) > 15:
            tips.append("🍽️ Dining out exceeds 15% of spending — try meal prepping.")
        if data.get("entertainment_pct", 0) > 10:
            tips.append("🎬 Entertainment is high — consider free alternatives this month.")
        return tips


class SavingsMode(FinancialState):
    """User is focused on building savings."""

    def get_name(self) -> str:
        return "Savings Mode"

    def get_color(self) -> str:
        return "#10b981"

    def get_icon(self) -> str:
        return "🏦"

    def get_recommendations(self, data: dict) -> list:
        tips = [
            "Automate a transfer to savings on payday — pay yourself first.",
            "Build a 3–6 month emergency fund before other goals.",
            "Review subscriptions — cancel any you haven't used this month.",
        ]
        savings_rate = data.get("savings_rate", 0)
        if savings_rate < 10:
            tips.append(f"⚠️ Savings rate is {savings_rate:.1f}% — aim for at least 20%.")
        elif savings_rate >= 20:
            tips.append(f"✅ Great! {savings_rate:.1f}% savings rate — consider investing the surplus.")
        return tips


class InvestmentMode(FinancialState):
    """User is focused on growing wealth through investments."""

    def get_name(self) -> str:
        return "Investment Mode"

    def get_color(self) -> str:
        return "#6366f1"

    def get_icon(self) -> str:
        return "📈"

    def get_recommendations(self, data: dict) -> list:
        tips = [
            "Diversify: mix stocks, bonds, and mutual funds to reduce risk.",
            "Review your portfolio quarterly — rebalance if any asset drifts >5%.",
            "Consider index funds for low-cost, long-term growth.",
            "Don't time the market — stay consistent with monthly investments.",
        ]
        if data.get("investment_pct", 0) < 10:
            tips.append("📉 Less than 10% going to investments — increase if possible.")
        return tips


class FinancialContext:
    """Manages the current financial state and handles transitions."""

    def __init__(self):
        self._state: FinancialState = BudgetingMode()
        self._history = []

    def transition_to(self, state: FinancialState):
        self._history.append(self._state.get_name())
        self._state = state

    def get_state(self) -> FinancialState:
        return self._state

    def get_recommendations(self, data: dict) -> list:
        return self._state.get_recommendations(data)

    def get_state_name(self) -> str:
        return self._state.get_name()


STATE_MAP = {
    "Budgeting Mode": BudgetingMode,
    "Savings Mode": SavingsMode,
    "Investment Mode": InvestmentMode,
}
