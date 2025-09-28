'''

'''
from datetime import date
from .account import Account
from .transaction import Transaction

class Ledger:

    def __init__(self):
        self._accounts: dict[str, Account] = {}
        self._transactions: dict[str, Transaction] = {}

    # Accounts
    def add_account(self, account):
        if account.name not in self._accounts:
            self._accounts[account.name] = account

    def get_account(self, name):
        return self._accounts.get(name)

    def list_accounts(self):
        return list(self._accounts.values())

    # Transactions
    def add_transaction(self, transaction):
        if transaction.account not in self._accounts:
            print("shit gone bad")
        self._transactions[transaction.id] = transaction

    def get_transaction(self, transactionID):
        return self._transactions.get(transactionID)

    from datetime import date

    def list_transactions(self, month):
        out = []
        for t in self._transactions.values():
            out.append(t)
        out.sort(key=lambda x: (x.date, x.id))
        return out


    def all_transactions(self):
        return self._transactions.values()
