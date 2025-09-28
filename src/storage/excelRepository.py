# finance_tracker/persistence/excel_repo.py
import sys
from pathlib import Path
from datetime import datetime, date
import pandas as pd
'''
PKG_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = PKG_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
'''
from core.ledger import Ledger
from core.account import Account
from core.transaction import Transaction, Income, Expense
from .repository import LedgerRepository, Report

SNAPSHOT_DEFAULT = Path("storage") / "excelTracker.xlsx"
class PandasExcelLedgerRepository(LedgerRepository):
    def __init__(self, _snapshot_path):
        if not _snapshot_path:
            self._snapshot_path = Path(SNAPSHOT_DEFAULT)
        else:
            self._snapshot_path = Path(_snapshot_path)
        self._snapshot_path.parent.mkdir(parents=True, exist_ok=True)

    # ---- helpers ----
    @staticmethod
    def _tx_to_row(t):
        row = {
            "id": t.id,
            "date": t.date.isoformat(),
            "account": t.account,
            "category": t.category,
            "type": "INCOME" if isinstance(t, Income) else "EXPENSE",
            "amount": t._amount,
            "notes": t.notes,
            "payor": "",
            "payee": ""
        }
        if isinstance(t, Income):
            row["payor"] = t.payor
        else:
            row["payee"] = t.payee
        return row

    @staticmethod
    def _row_counterparty(row: dict, is_income: bool) -> str:
        # Preferred explicit columns:
        if is_income and str(row.get("payor", "")).strip():
            return str(row["payor"])
        if (not is_income) and str(row.get("payee", "")).strip():
            return str(row["payee"])
        # Back-compat: a single 'party' column
        if str(row.get("party", "")).strip():
            return str(row["party"])
        # Last resort: try the other one if present
        other = row.get("payee" if is_income else "payor", "")
        return str(other) if str(other).strip() else ""
    
    @staticmethod
    def _row_amount(row: dict) -> float:
        # Accept both 'amount' and legacy '_amount'
        if "amount" in row and str(row["amount"]).strip() != "":
            return float(row["amount"])
        if "_amount" in row and str(row["_amount"]).strip() != "":
            return float(row["_amount"])
        raise ValueError("Row is missing 'amount' (or legacy '_amount').")
    
    @staticmethod
    def _row_to_tx(row: dict) -> Transaction:
        is_income = str(row["type"]).upper() == "INCOME"
        d = row["date"]
        d_parsed = d if isinstance(d, date) else datetime.fromisoformat(str(d)).date()
        amt = PandasExcelLedgerRepository._row_amount(row)
        cp = PandasExcelLedgerRepository._row_counterparty(row, is_income)

        if is_income:
            return Income(
                id=str(row["id"]),
                date=d_parsed,
                account=str(row["account"]),
                category=str(row.get("category", "")),
                amount=amt,
                payor=cp,
                notes=str(row.get("notes", "")),
            )
        else:
            return Expense(
                id=str(row["id"]),
                date=d_parsed,
                account=str(row["account"]),
                category=str(row.get("category", "")),
                amount=amt,
                payee=cp,
                notes=str(row.get("notes", "")),
            )

    # ---- interface impl ----
    def load(self):
        ledger = Ledger()
        if not self._snapshot_path.exists():
            return ledger
        try:
            with pd.ExcelFile(self._snapshot_path) as xls:
                if "Accounts" in xls.sheet_names:
                    df_a = pd.read_excel(xls, "Accounts").fillna("")
                    for _, r in df_a.iterrows():
                        ledger.add_account(Account(name=str(r["name"]), type=str(r.get("type", "CASH"))))
                if "Transactions" in xls.sheet_names:
                    df_t = pd.read_excel(xls, "Transactions").fillna("")
                    for _, r in df_t.iterrows():
                        t = self._row_to_tx(r.to_dict())
                        if not ledger.get_account(t.account):
                            ledger.add_account(Account(t.account))
                        ledger.add_transaction(t)
        except Exception as e:
            print(f"[WARN] Failed to load snapshot: {e}")
        return ledger

    def save(self, ledger: Ledger) -> None:
        accounts = [{"name": a.name, "type": a.type} for a in ledger.list_accounts()]
        txs = [self._tx_to_row(t) for t in ledger.all_transactions()]
        self._snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        with pd.ExcelWriter(self._snapshot_path, engine="xlsxwriter") as xw:
            pd.DataFrame(accounts).to_excel(xw, sheet_name="Accounts", index=False)
            pd.DataFrame(txs).to_excel(xw, sheet_name="Transactions", index=False)

    def import_transactions(self, path, ledger):
        path = Path(path)
        df = pd.read_excel(path)
        required = {"id", "date", "account", "category", "type", "amount", "notes"}
        # party column is flexible (party OR payee/payor), so not in required
        missing = list(required - set(df.columns))
        if missing:
            raise ValueError(f"Missing required columns: {missing}. 'party' OR ('payee'/'payor') is also expected.")
        added = 0
        for _, r in df.fillna("").iterrows():
            t = self._row_to_tx(r.to_dict())
            if not ledger.get_account(t.account):
                ledger.add_account(Account(t.account))
            if ledger.get_transaction(t.id):
                continue
            ledger.add_transaction(t)
            added += 1
        return added

    def export_report(self, report, path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        summary_df = pd.DataFrame([{
            "month": report.month,
            "income": report.income,
            "expense": report.expense,
            "net": report.net,
        }])
        by_cat_df = pd.DataFrame(
            [{"category": c.category, "total": c.total, "count": c.count} for c in report.by_category]
        )
        with pd.ExcelWriter(path, engine="xlsxwriter") as xw:
            summary_df.to_excel(xw, sheet_name="Summary", index=False)
            by_cat_df.to_excel(xw, sheet_name="ByCategory", index=False)
