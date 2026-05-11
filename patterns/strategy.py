"""
Strategy Pattern — Budgeting Strategies
SE-211 Lab 14: Personal Finance Management System
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class BudgetAllocation:
    needs: float
    wants: float
    savings: float
    investments: float
    label: str


class BudgetStrategy(ABC):
    """Abstract base class for all budgeting strategies."""

    @abstractmethod
    def calculate(self, income: float) -> BudgetAllocation:
        pass

    @abstractmethod
    def describe(self) -> str:
        pass


class FiftyThirtyTwentyStrategy(BudgetStrategy):
    """50/30/20 Rule: 50% needs, 30% wants, 20% savings."""

    def calculate(self, income: float) -> BudgetAllocation:
        return BudgetAllocation(
            needs=income * 0.50,
            wants=income * 0.30,
            savings=income * 0.20,
            investments=0.0,
            label="50/30/20 Rule"
        )

    def describe(self) -> str:
        return (
            "50% → Needs (rent, groceries, utilities)\n"
            "30% → Wants (dining, entertainment)\n"
            "20% → Savings & debt repayment"
        )


class ZeroBasedBudgetStrategy(BudgetStrategy):
    """Zero-Based: Every rupee is assigned a purpose (income - expenses = 0)."""

    def calculate(self, income: float) -> BudgetAllocation:
        return BudgetAllocation(
            needs=income * 0.55,
            wants=income * 0.20,
            savings=income * 0.15,
            investments=income * 0.10,
            label="Zero-Based Budgeting"
        )

    def describe(self) -> str:
        return (
            "55% → Needs\n"
            "20% → Wants\n"
            "15% → Savings\n"
            "10% → Investments\n"
            "Every rupee is intentionally assigned."
        )


class SeventySixteenTenStrategy(BudgetStrategy):
    """70/20/10: 70% living, 20% savings, 10% giving/investing."""

    def calculate(self, income: float) -> BudgetAllocation:
        return BudgetAllocation(
            needs=income * 0.70,
            wants=0.0,
            savings=income * 0.20,
            investments=income * 0.10,
            label="70/20/10 Rule"
        )

    def describe(self) -> str:
        return (
            "70% → Monthly expenses (living costs)\n"
            "20% → Savings\n"
            "10% → Investments or giving"
        )


class AggressiveSavingsStrategy(BudgetStrategy):
    """Aggressive: Maximize savings at 40%."""

    def calculate(self, income: float) -> BudgetAllocation:
        return BudgetAllocation(
            needs=income * 0.45,
            wants=income * 0.15,
            savings=income * 0.25,
            investments=income * 0.15,
            label="Aggressive Savings"
        )

    def describe(self) -> str:
        return (
            "45% → Needs\n"
            "15% → Wants\n"
            "25% → Savings\n"
            "15% → Investments\n"
            "Best for fast goal achievement."
        )


class BudgetContext:
    """Context class that uses a BudgetStrategy."""

    def __init__(self, strategy: BudgetStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: BudgetStrategy):
        self._strategy = strategy

    def get_allocation(self, income: float) -> BudgetAllocation:
        return self._strategy.calculate(income)

    def get_description(self) -> str:
        return self._strategy.describe()

    def get_label(self) -> str:
        return self._strategy.calculate(1).label


STRATEGIES = {
    "50/30/20 Rule": FiftyThirtyTwentyStrategy,
    "Zero-Based Budgeting": ZeroBasedBudgetStrategy,
    "70/20/10 Rule": SeventySixteenTenStrategy,
    "Aggressive Savings": AggressiveSavingsStrategy,
}
