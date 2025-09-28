from storage.repository import LedgerRepository, CategorySummary, Report

class ReportingService:
    def __init__(self, repo: LedgerRepository):
        self._repo = repo

    def monthlySummary(self, month):
        ledger = self._repo.load()
        txs = ledger.listTransactions(month=month)
        income = sum(t.effectiveAmount() for t in txs if t.effectiveAmount() > 0)
        expense = -sum(t.effectiveAmount() for t in txs if t.effectiveAmount() < 0)
        net = income - expense

        by = {}
        for t in txs:
            amt = abs(t.effectiveAmount())
            cs = by.get(t.category)
            if cs is None:
                by[t.category] = CategorySummary(t.category, amt, 1)
            else:
                cs.total += amt
                cs.count += 1

        return Report(month, income, expense, net, list(by.values()))

    def byCategory(self, month):
        return self.monthlySummary(month).byCategory
