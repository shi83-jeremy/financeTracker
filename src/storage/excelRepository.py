from pathlib import Path
from datetime import datetime, date
import pandas as pd

from core.ledger import Ledger
from core.account import Account
from core.transaction import Transaction
from .repository import LedgerRepository

SNAPSHOT_DEFAULT = Path("storage") / "excelTracker.xlsx"

class PandasExcelLedgerRepository(LedgerRepository):
    def __init__(self, _snapshot_path):
        if not _snapshot_path:
            self._snapshot_path = Path(SNAPSHOT_DEFAULT)
        else:
            self._snapshot_path = Path(_snapshot_path)
        self._snapshot_path.parent.mkdir(parents=True, exist_ok=True)

    # find party from excel (whether its income or expense, or payor and payee)
    @staticmethod
    def extractParty(row, is_income):
        if is_income:
            val = str(row.get("payor", "")).strip()
            if not val:
                raise ValueError(f"Missing 'payor' for INCOME row id={row.get('id')}")
            return val
        else:
            val = str(row.get("payee", "")).strip()
            if not val:
                raise ValueError(f"Missing 'payee' for EXPENSE row id={row.get('id')}")
            return val
    
    # find the amount for a specific row (not touched really)
    @staticmethod
    def findAmount(row):
        s = str(row.get("amount", "")).strip()
        if s == "":
            raise ValueError("Row is missing required 'amount' column (or it's blank).")
        return float(s)
    
    #converts a row of input into a transaction
    @staticmethod
    def convertToTransaction(row):
        transactionType = str(row["type"]).upper()
        d = row["date"]
        parsedDate = d if isinstance(d, date) else datetime.fromisoformat(str(d)).date()
        amount = PandasExcelLedgerRepository.findAmount(row)
        
        payor = payee = None
        if transactionType == "INCOME":
            payor = PandasExcelLedgerRepository.extractParty(row, True)
        elif transactionType == "EXPENSE":
            payee = PandasExcelLedgerRepository.extractParty(row, False)

        return Transaction.create(
            kind=transactionType,
            id=str(row["id"]),
            date=parsedDate,
            account=str(row["account"]),
            category=str(row.get("category", "")),
            amount=amount,
            notes=str(row.get("notes", "")),
            payor=payor,
            payee=payee,
        )

    # for reading excel file and reconstructing the ledger (account and transaction)
    def load(self):
        ledger = Ledger()
        if not self._snapshot_path.exists():
            return ledger
        try:
            with pd.ExcelFile(self._snapshot_path) as xls:
                if "Accounts" in xls.sheet_names:
                    accountDF = pd.read_excel(xls, "Accounts").fillna("")
                    for _, r in accountDF.iterrows():
                        ledger.addAccount(Account(name=str(r["name"]), type=str(r.get("type", "CASH"))))
                if "Transactions" in xls.sheet_names:
                    transactionDF = pd.read_excel(xls, "Transactions").fillna("")
                    for _, r in transactionDF.iterrows():
                        transaction = self.convertToTransaction(r.to_dict())
                        if not ledger.getAccount(transaction.account):
                            ledger.addAccount(Account(transaction.account))
                        ledger.addTransaction(transaction)
        except Exception as e:
            print(f"[WARN] Failed to load snapshot: {e}")
        return ledger

    # write the ledger to the excel
    def save(self, ledger):
        accounts = [{"name": a.name, "type": a.type} for a in ledger.listAccounts()]
        transactions = [t.record() for t in ledger.allTransactions()]
        self._snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        with pd.ExcelWriter(self._snapshot_path, engine="xlsxwriter") as xw:
            pd.DataFrame(accounts).to_excel(xw, sheet_name="Accounts", index=False)
            pd.DataFrame(transactions).to_excel(xw, sheet_name="Transactions", index=False)

    # =====================================================================================================
    # importing and exporting transaction files, not properly done

    # def importTransactions(self, path, ledger):
    #     pass
    # def exportReport(self, report, path):
    #     pass

    def importTransactions(self, path, ledger):
        path = Path(path)
        df = pd.read_excel(path)
        cols = set(df.columns)
        required = {"id", "date", "account", "category", "type", "amount", "notes", "payor", "payee"}
        missing = list(required - cols)
        if missing:
            raise ValueError(f"Missing required columns: {missing}. Expected schema: {sorted(required)}")
        added = 0
        for _, r in df.fillna("").iterrows():
            t = self.convertToTransaction(r.to_dict())
            if not ledger.getAccount(t.account):
                ledger.addAccount(Account(t.account))
            if ledger.getTransaction(t.id):
                continue
            ledger.addTransaction(t)
            added += 1
        return added

    def exportReport(self, report, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        summary_df = pd.DataFrame([{
            "month": report.month,
            "income": report.income,
            "expense": report.expense,
            "net": report.net,
        }])
        by_cat_df = pd.DataFrame(
            [{"category": c.category, "total": c.total, "count": c.count} for c in report.byCategory]
        )
        with pd.ExcelWriter(path, engine="xlsxwriter") as xw:
            summary_df.to_excel(xw, sheet_name="Summary", index=False)
            by_cat_df.to_excel(xw, sheet_name="ByCategory", index=False)
