import uuid
from datetime import datetime, date
from core.transaction import Income, Expense, Transaction
from core.ledger import Ledger
from core.account import Account
from storage.repository import LedgerRepository

class TxDTO:
    def __init__(self, date ,account ,category, amount, party, type, notes):
        self.date = date
        self.account = account
        self.category = category
        self.amount = amount
        self.party = party
        self.type = type.upper()
        self.notes = notes

def _parse_date(s):
    if isinstance(s, date):
        return s
    return datetime.fromisoformat(s).date()

class TransactionService:
    def __init__(self, repo: LedgerRepository):
        self._repo = repo

    def add(self, dto: TxDTO) -> str:
        kind = dto.type
        ledger: Ledger = self._repo.load()
        if not ledger.get_account(dto.account):
            ledger.add_account(Account(dto.account))
        tx_id = str(uuid.uuid4())
        if kind == "INCOME":
            t: Transaction = Income(
                id=tx_id, date=_parse_date(dto.date), account=dto.account,
                category=dto.category, amount=dto.amount, payor=dto.party, notes=dto.notes
            )
        else:
            t = Expense(
                id=tx_id, date=_parse_date(dto.date), account=dto.account,
                category=dto.category, amount=dto.amount, payee=dto.party, notes=dto.notes
            )
        ledger.add_transaction(t)
        self._repo.save(ledger)
        return tx_id
