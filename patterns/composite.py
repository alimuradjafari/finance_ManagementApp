"""
Composite Pattern — Financial Account Hierarchy
SE-211 Lab 14: Personal Finance Management System

Allows treating individual accounts and groups of accounts uniformly.
"""

from abc import ABC, abstractmethod
from typing import List


class FinancialComponent(ABC):
    """Abstract component in the Composite tree."""

    @abstractmethod
    def get_balance(self) -> float:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def display(self, indent: int = 0) -> str:
        pass


class Account(FinancialComponent):
    """Leaf node — a single financial account."""

    def __init__(self, name: str, balance: float, account_type: str):
        self._name = name
        self._balance = balance
        self._type = account_type
        self._transactions: List[dict] = []

    def deposit(self, amount: float, description: str = ""):
        self._balance += amount
        self._transactions.append({"type": "credit", "amount": amount, "desc": description})

    def withdraw(self, amount: float, description: str = ""):
        if amount > self._balance:
            raise ValueError(f"Insufficient funds in {self._name}")
        self._balance -= amount
        self._transactions.append({"type": "debit", "amount": amount, "desc": description})

    def get_balance(self) -> float:
        return self._balance

    def get_name(self) -> str:
        return self._name

    def get_type(self) -> str:
        return self._type

    def display(self, indent: int = 0) -> str:
        prefix = "  " * indent
        return f"{prefix}💳 {self._name} ({self._type}): PKR {self._balance:,.2f}"


class AccountGroup(FinancialComponent):
    """Composite node — a group of accounts (e.g., 'All Savings Accounts')."""

    def __init__(self, name: str):
        self._name = name
        self._children: List[FinancialComponent] = []

    def add(self, component: FinancialComponent):
        self._children.append(component)

    def remove(self, component: FinancialComponent):
        self._children.remove(component)

    def get_balance(self) -> float:
        return sum(child.get_balance() for child in self._children)

    def get_name(self) -> str:
        return self._name

    def get_children(self) -> List[FinancialComponent]:
        return self._children

    def display(self, indent: int = 0) -> str:
        prefix = "  " * indent
        lines = [f"{prefix}📁 {self._name}: PKR {self.get_balance():,.2f}"]
        for child in self._children:
            lines.append(child.display(indent + 1))
        return "\n".join(lines)


class PortfolioManager:
    """Manages the entire financial portfolio using the Composite structure."""

    def __init__(self, owner_name: str):
        self.root = AccountGroup(f"{owner_name}'s Portfolio")
        self._setup_default_structure()

    def _setup_default_structure(self):
        self.savings_group = AccountGroup("Savings Accounts")
        self.checking_group = AccountGroup("Checking Accounts")
        self.investment_group = AccountGroup("Investment Accounts")

        self.root.add(self.savings_group)
        self.root.add(self.checking_group)
        self.root.add(self.investment_group)

    def add_account(self, group: str, name: str, balance: float) -> Account:
        account = Account(name, balance, group)
        target = {
            "savings": self.savings_group,
            "checking": self.checking_group,
            "investment": self.investment_group,
        }.get(group.lower(), self.savings_group)
        target.add(account)
        return account

    def get_total_balance(self) -> float:
        return self.root.get_balance()

    def get_summary(self) -> dict:
        return {
            "total": self.root.get_balance(),
            "savings": self.savings_group.get_balance(),
            "checking": self.checking_group.get_balance(),
            "investments": self.investment_group.get_balance(),
        }

    def display_tree(self) -> str:
        return self.root.display()
