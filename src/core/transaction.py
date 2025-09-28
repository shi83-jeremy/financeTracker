from datetime import date
from abc import ABC, abstractmethod

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
    def effectiveAmount(self):
        raise NotImplementedError
    @abstractmethod
    def getInformation(self):
        raise NotImplementedError

class Income (Transaction):
    def __init__ (self, id, date, account, category, amount, notes, payor):
        super().__init__(id, date, account, category, amount, notes)
        self.payor = payor

    @property
    def party(self):
        return self.payor

    def effectiveAmount(self):
        return +self.amount
    def getInformation(self):
        raise NotImplementedError

class Expense (Transaction):
    def __init__ (self, id, date, account, category, amount, notes, payee):
        super().__init__(id, date, account, category, amount, notes)
        self.payee = payee
    
    @property
    def party(self):
        return self.payee
    
    def effectiveAmount(self):
        return -self.amount
    def getInformation(self):
        raise NotImplementedError