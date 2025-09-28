from datetime import date
from .account import Account

class Ledger:
    def __init__(self):
        self._accounts = {}
        self._transactions = {}

    # Accounts
    def addAccount(self, account):
        if account.name not in self._accounts:
            self._accounts[account.name] = account

    def getAccount(self, name):
        return self._accounts.get(name)

    def listAccounts(self):
        return list(self._accounts.values())

    # Transactions
    def addTransaction(self, transaction):
        if transaction.account not in self._accounts:
            print("shit gone bad")
        self._transactions[transaction.id] = transaction

    def getTransaction(self, transactionID):
        return self._transactions.get(transactionID)

    # lists the transactions based on the month so u can get monthly report
    def listTransactions(self, month):
        year = mon = None
        if month:
            y_str, m_str = month.strip().split("-", 1)
            year, mon = int(y_str), int(m_str)
            if not (1 <= mon <= 12):
                raise ValueError("month must be 'YYYY-MM'")

        txs = [
            t for t in self._transactions.values()
            if (year is None or (t.date.year == year and t.date.month == mon))
        ]
        txs.sort(key=lambda t: (t.date, t.id))
        return txs
    
    def allTransactions(self):
        return self._transactions.values()
