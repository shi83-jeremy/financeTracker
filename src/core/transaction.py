from datetime import date, datetime
from abc import ABC, abstractmethod
from uuid import uuid4

from .account import Account

# to make sure a date is returned and parsed into one if not a date
def _parse_date(s):
    if isinstance(s, date):
        return s
    return datetime.fromisoformat(str(s)).date()

class Transaction(ABC):
    defaultCurrency = "CAD"
    baseTax = 1.13

    def __init__ (self, id, date, account, category, amount, notes):
        self.id = id
        self.date = date
        self.account = account
        self.category = category
        self._amount = 0.0
        self.amount = amount
        self.notes = notes
        
    @property
    def amount(self):
        return self._amount
    @amount.setter
    def amount(self, value):
        value = float(value)
        if (value <= 0):
            value = 0.0
        self._amount = value
    
    @abstractmethod
    def effectiveAmount(self): ...
    @abstractmethod
    def getInformation(self): ...
    @abstractmethod
    def record(self): ...

    # returns correct class 
    @classmethod
    def create(cls, *, kind, id, date, account, category, amount, notes="", payor=None, payee=None):

        k = str(kind).upper()
        if k == "INCOME":
            if payor is None:
                raise ValueError("payor is required for INCOME")
            return Income(id, _parse_date(date), account, category, amount, payor, notes)
        elif k == "EXPENSE":
            if payee is None:
                raise ValueError("payee is required for EXPENSE")
            return Expense(id, _parse_date(date), account, category, amount, payee, notes)
        else:
            raise ValueError(f"Unknown kind: {kind!r}")

    # adds account to ledger if doesn't exist
    @classmethod
    def ensureAccount(cls, ledger, account):
        if not ledger.getAccount(account):
            ledger.addAccount(Account(account))

    # load excel and create transaction income
    @classmethod
    def recordIncome(cls, repo, *, date, account, category, amount, payor, notes=""):
        ledger = repo.load()
        cls.ensureAccount(ledger, account)
        transaction = cls.create(
            kind="INCOME",
            id=str(uuid4()),
            date=date,
            account=account,
            category=category,
            amount=float(amount),
            notes=notes,
            payor=payor,
        )
        ledger.addTransaction(transaction)
        repo.save(ledger)
        return transaction.id

    # load excel and create transaction expense
    @classmethod
    def recordExpense(cls, repo, *, date, account, category, amount, payee, notes=""):
        ledger = repo.load()
        cls.ensureAccount(ledger, account)
        transaction = cls.create(
            kind="EXPENSE",
            id=str(uuid4()),
            date=date,
            account=account,
            category=category,
            amount=float(amount),
            notes=notes,
            payee=payee,
        )
        ledger.addTransaction(transaction)
        repo.save(ledger)
        return transaction.id

class Income (Transaction):
    def __init__ (self, id, date, account, category, amount, payor, notes):
        super().__init__(id, date, account, category, amount, notes)
        self.payor = payor

    @property
    def party(self):
        return self.payor

    def effectiveAmount(self):
        return +self.amount
    def getInformation(self):
        raise NotImplementedError
    def record(self):
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "account": self.account,
            "category": self.category,
            "type": "INCOME",
            "amount": float(self.amount),
            "notes": self.notes,
            "payor": self.payor,
            "payee": "",
        }


class Expense (Transaction):
    def __init__ (self, id, date, account, category, amount, payee, notes):
        super().__init__(id, date, account, category, amount, notes)
        self.payee = payee
    
    @property
    def party(self):
        return self.payee
    
    def effectiveAmount(self):
        return -self.amount
    def getInformation(self):
        raise NotImplementedError
    def record(self):
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "account": self.account,
            "category": self.category,
            "type": "EXPENSE",
            "amount": float(self.amount),
            "notes": self.notes,
            "payor": "",         
            "payee": self.payee,
        }
