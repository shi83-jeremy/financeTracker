import sys
from pathlib import Path
PKG_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = PKG_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PyQt5.QtWidgets import (
    QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog,
    QMessageBox, QHBoxLayout, QVBoxLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer

from src.core.transaction import Transaction

class FinanceWindow(QWidget):
    def __init__(self, repo, rpsvc):
        super().__init__()
        self.repo = repo
        self.rpsvc = rpsvc
        self.buildUI()

    def buildUI(self):
        self.setWindowTitle("Finance Tracker!!!!!!!!!!!!!!!!!!!!!")
        self.resize(1000, 560)
        root = QVBoxLayout(self)

        # top grid for inputs
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
        grid.addWidget(QLabel("Party"), r, 4); grid.addWidget(self.party_edit, r, 5); r += 1
        grid.addWidget(QLabel("Notes"), r, 0); grid.addWidget(self.notes_edit, r, 1, 1, 5); r += 1

        # bottom row for actions
        bottomRow = QHBoxLayout()

        # add button and confirmation label for it (left side)
        self.add_btn = QPushButton("Add")
        bottomRow.addWidget(self.add_btn)
        self.inline_status = QLabel("")
        self.inline_status.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.inline_status.setStyleSheet("color:#000000; padding-left:8px;")
        self.inline_status.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        bottomRow.addWidget(self.inline_status, 1)

        # everything else (right side)
        self.import_btn = QPushButton("Import Excel")
        self.month_label = QLabel("Month (YYYY-MM)")
        self.month_edit.setFixedWidth(120)
        self.summary_btn = QPushButton("Show Summary")
        self.export_btn = QPushButton("Export Month")

        bottomRight = QHBoxLayout()
        bottomRight.addWidget(self.import_btn)
        bottomRight.addSpacing(12)
        bottomRight.addWidget(self.month_label)
        bottomRight.addWidget(self.month_edit)
        bottomRight.addSpacing(12)
        bottomRight.addWidget(self.summary_btn)
        bottomRight.addWidget(self.export_btn)

        bottomRow.addLayout(bottomRight)

        # displaying transactions table
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["Date", "Account", "Category", "Party", "Type", "Amount", "Notes"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        #bottom confirmation label
        self.status_label = QLabel(""); self.status_label.setAlignment(Qt.AlignLeft)
        self.status_label.setStyleSheet("color: #444; padding: 4px;")

        #add all onto root
        root.addLayout(grid)
        root.addLayout(bottomRow)
        root.addWidget(self.table)
        root.addWidget(self.status_label)

        self.add_btn.clicked.connect(self.addTransaction)
        self.import_btn.clicked.connect(self.importExcel)
        self.summary_btn.clicked.connect(self.summarizeTable)
        self.export_btn.clicked.connect(self.exportExcel)

    # creates a transaction and adds it
    def addTransaction(self):
        try:
            if self.type_combo.currentText().upper() == "INCOME":
                tx_id = Transaction.recordIncome(
                    self.repo,
                    date=self.date_edit.text().strip(),
                    account=self.account_edit.text().strip(),
                    category=self.category_edit.text().strip(),
                    amount=float(self.amount_edit.text()),
                    payor=(self.counterparty_edit.text().strip() if hasattr(self, "counterparty_edit")
                        else self.party_edit.text().strip()),
                    notes=self.notes_edit.text().strip(),
                )
            else:
                tx_id = Transaction.recordExpense(
                    self.repo,
                    date=self.date_edit.text().strip(),
                    account=self.account_edit.text().strip(),
                    category=self.category_edit.text().strip(),
                    amount=float(self.amount_edit.text()),
                    payee=(self.counterparty_edit.text().strip() if hasattr(self, "counterparty_edit")
                        else self.party_edit.text().strip()),
                    notes=self.notes_edit.text().strip(),
                )
            self.displayConfirmation(f" Added transaction {tx_id[:8]}")
            self.refreshTable()
        except Exception as e:
            self.error(str(e))

    # def importExcel(self):
    #     pass
    def importExcel(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choose Excel file", filter="Excel (*.xlsx)")
        if not path: return
        try:
            ledger = self.repo.load()
            n = self.repo.importTransactions(path, ledger)
            self.repo.save(ledger)
            self.displayConfirmation(f"Imported {n} transactions.")
            self.refreshTable()
        except Exception as e:
            self.error(str(e))

    #summary button for filling table in and showing summary of monthly expenses/incomes
    def summarizeTable(self):
        month = self.month_edit.text().strip()
        if not month:
            self.error("Enter month as YYYY-MM"); return
        try:
            report = self.rpsvc.monthlySummary(month)
            ledger = self.repo.load()
            txs = ledger.listTransactions(month=month)
            self.fillTable(txs)
            QMessageBox.information(
                self, "Monthly Summary",
                f"Month: {report.month}\nIncome: {report.income:.2f}\n"
                f"Expense: {report.expense:.2f}\nNet: {report.net:.2f}"
            )
        except Exception as e:
            self.error(str(e))

    # def exportExcel(self):
    #     pass
    def exportExcel(self):
        month = self.month_edit.text().strip()
        if not month:
            self.error("Enter month as YYYY-MM"); return
        try:
            report = self.rpsvc.monthlySummary(month)
            path, _ = QFileDialog.getSaveFileName(self, "Save Report", f"{month}.xlsx", filter="Excel (*.xlsx)")
            if path:
                self.repo.exportReport(report, path)
                self.displayConfirmation(f"Saved report to {path}")
        except Exception as e:
            self.error(str(e))

    #fill the table in based on transaction type
    def fillTable(self, txs):
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

    def refreshTable(self):
        month = self.month_edit.text().strip()
        if not month: return
        ledger = self.repo.load()
        txs = ledger.listTransactions(month=month)
        self.fillTable(txs)

    def displayConfirmation(self, msg: str):
        #self.status_label.setText(msg) #for bottom confirmation line

        self.inline_status.setText(msg)
        QTimer.singleShot(4000, self.inline_status.clear)   #clears confirmation message after 4s

    def error(self, msg): 
        QMessageBox.critical(self, "Error", msg)

def runGUI(repo, rpsvc):
    app = QApplication.instance() or QApplication(sys.argv)
    win = FinanceWindow(repo, rpsvc)
    win.show()
    app.exec_()
