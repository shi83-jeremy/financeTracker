from abc import ABC, abstractmethod
from core.ledger import Ledger

class LedgerRepository(ABC):
    @abstractmethod
    def load(self): ...
    @abstractmethod
    def save(self, ledger: Ledger): ...
    @abstractmethod
    def import_transactions(self, path: str, ledger: Ledger): ...
    @abstractmethod
    def export_report(self, report: "Report", path: str): ...

class CategorySummary:
    def __init__(self, category: str, total: float, count: int):
        self.category = category
        self.total = float(total)
        self.count = int(count)

class Report:
    def __init__(self, month, income, expense, net, by_category):
        self.month = month
        self.income = income
        self.expense = expense
        self.net = net
        self.by_category = by_category
