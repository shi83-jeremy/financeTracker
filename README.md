# Finance Tracker 

A small basic finance tracker built with a domain model (Accounts, Transactions, Ledger), a PyQt GUI, and Excel storage via Pandas.

---

## Features

- Add **Income** and **Expense** transactions (with **Payor**/**Payee**).
- **Auto-create accounts** when a new account name is used.
- View transactions for a given **month (YYYY-MM)** in a table.
- One-click **Monthly Summary** (Income, Expense, Net).
- **Export** a monthly report to Excel (Summary & ByCategory sheets).
- **Import** transactions from an `.xlsx` file that matches the app schema.
- Strict, predictable Excel schema (no legacy `party` / `_amount` columns).

---

## Requirements

- Python **3.10+**
- Packages:
  - `PyQt5`
  - `pandas`
  - `openpyxl` (read `.xlsx`)
  - `XlsxWriter` (write `.xlsx`)

Install:

```bash
pip install PyQt5 pandas openpyxl XlsxWriter