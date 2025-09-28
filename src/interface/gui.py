# finance_tracker/interface/gui_qt.py
# sys.path bootstrap (optional if you run as a module)
import sys
from pathlib import Path
PKG_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = PKG_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PyQt5.QtWidgets import (
    QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog,
    QMessageBox, QHBoxLayout, QVBoxLayout
)
from PyQt5.QtCore import Qt
import sys as _sys

from src.core.transaction import Transaction
from src.storage.repository import LedgerRepository
from src.services.transactions import TransactionService, TxDTO
from src.services.reporting import ReportingService

class FinanceWindow(QWidget):
    def __init__(self, repo: LedgerRepository, txsvc: TransactionService, rpsvc: ReportingService):
        super().__init__()
        self.repo = repo
        self.txsvc = txsvc
        self.rpsvc = rpsvc
        self._build_ui()

    def _build_ui(self):
        self.setWindowTitle("Finance Tracker!!!!!!!!!!!!!!!!!!!!!")
        self.resize(1000, 560)
        root = QVBoxLayout(self)

        grid = QGridLayout()
        r = 0
        self.date_edit = QLineEdit()
        self.account_edit = QLineEdit()
        self.type_combo = QComboBox(); self.type_combo.addItems(["EXPENSE", "INCOME"])
        self.category_edit = QLineEdit()
        self.amount_edit = QLineEdit()
        self.party_edit = QLineEdit()
        self.notes_edit = QLineEdit()
        self.month_edit = QLineEdit()

        grid.addWidget(QLabel("Date (YYYY-MM-DD)"), r, 0); grid.addWidget(self.date_edit, r, 1)
        grid.addWidget(QLabel("Account"), r, 2); grid.addWidget(self.account_edit, r, 3)
        grid.addWidget(QLabel("Type"), r, 4); grid.addWidget(self.type_combo, r, 5); r += 1

        grid.addWidget(QLabel("Category"), r, 0); grid.addWidget(self.category_edit, r, 1)
        grid.addWidget(QLabel("Amount"), r, 2); grid.addWidget(self.amount_edit, r, 3)
        grid.addWidget(QLabel("Party (Payee for Expense, Payor for Income)"), r, 4); grid.addWidget(self.party_edit, r, 5); r += 1

        grid.addWidget(QLabel("Notes"), r, 0); grid.addWidget(self.notes_edit, r, 1, 1, 5); r += 1

        row = QHBoxLayout()
        self.add_btn = QPushButton("Add")
        self.import_btn = QPushButton("Import Excel")
        row.addWidget(self.add_btn); row.addWidget(self.import_btn)
        row.addSpacing(10)
        row.addWidget(QLabel("Month (YYYY-MM)")); row.addWidget(self.month_edit)
        self.summary_btn = QPushButton("Show Summary")
        self.export_btn = QPushButton("Export Month")
        row.addWidget(self.summary_btn); row.addWidget(self.export_btn); row.addStretch()

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["Date", "Account", "Category", "Party", "Type", "Amount", "Notes"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        self.status_label = QLabel(""); self.status_label.setAlignment(Qt.AlignLeft)
        self.status_label.setStyleSheet("color: #444; padding: 4px;")

        root.addLayout(grid); root.addLayout(row); root.addWidget(self.table); root.addWidget(self.status_label)

        self.add_btn.clicked.connect(self._on_add)
        self.import_btn.clicked.connect(self._on_import)
        self.summary_btn.clicked.connect(self._on_summary)
        self.export_btn.clicked.connect(self._on_export)

    # ---- Handlers ----
    def _on_add(self):
        try:
            dto = TxDTO(
                date=self.date_edit.text().strip(),
                account=self.account_edit.text().strip(),
                category=self.category_edit.text().strip(),
                amount=float(self.amount_edit.text()),
                party=self.party_edit.text().strip(),
                type=self.type_combo.currentText(),
                notes=self.notes_edit.text().strip(),
            )
            tx_id = self.txsvc.add(dto)
            self._set_status(f"Added transaction {tx_id[:8]}")
            self._refresh_table_if_month()
        except Exception as e:
            self._error(str(e))

    def _on_import(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choose Excel file", filter="Excel (*.xlsx)")
        if not path: return
        try:
            ledger = self.repo.load()
            n = self.repo.import_transactions(path, ledger)
            self.repo.save(ledger)
            self._set_status(f"Imported {n} transactions.")
            self._refresh_table_if_month()
        except Exception as e:
            self._error(str(e))

    def _on_summary(self):
        month = self.month_edit.text().strip()
        if not month:
            self._error("Enter month as YYYY-MM"); return
        try:
            report = self.rpsvc.monthly_summary(month)
            ledger = self.repo.load()
            txs = ledger.list_transactions(month=month)
            self._fill_table(txs)
            QMessageBox.information(
                self, "Monthly Summary",
                f"Month: {report.month}\nIncome: {report.income:.2f}\n"
                f"Expense: {report.expense:.2f}\nNet: {report.net:.2f}"
            )
        except Exception as e:
            self._error(str(e))

    def _on_export(self):
        month = self.month_edit.text().strip()
        if not month:
            self._error("Enter month as YYYY-MM"); return
        try:
            report = self.rpsvc.monthly_summary(month)
            path, _ = QFileDialog.getSaveFileName(self, "Save Report", f"{month}.xlsx", filter="Excel (*.xlsx)")
            if path:
                self.repo.export_report(report, path)
                self._set_status(f"Saved report to {path}")
        except Exception as e:
            self._error(str(e))

    # ---- Helpers ----
    def _fill_table(self, txs: list[Transaction]):
        self.table.setRowCount(0)
        for t in txs:
            ttype = "INCOME" if t.effectiveAmount() > 0 else "EXPENSE"
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, val in enumerate([
                t.date.isoformat(), t.account, t.category, t.party, ttype,
                f"{abs(t.effectiveAmount()):.2f}", t.notes
            ]):
                item = QTableWidgetItem(val)
                if col in (0, 5):
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(row, col, item)

    def _refresh_table_if_month(self):
        month = self.month_edit.text().strip()
        if not month: return
        ledger = self.repo.load()
        txs = ledger.list_transactions(month=month)
        self._fill_table(txs)

    def _set_status(self, msg: str): self.status_label.setText(msg)
    def _error(self, msg: str): QMessageBox.critical(self, "Error", msg)

def run_gui(repo: LedgerRepository, txsvc: TransactionService, rpsvc: ReportingService):
    app = QApplication.instance() or QApplication(sys.argv)
    win = FinanceWindow(repo, txsvc, rpsvc); win.show(); app.exec_()
