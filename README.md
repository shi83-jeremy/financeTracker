# Finance Tracker 

A small basic finance tracker built with a domain model (Accounts, Transactions, Ledger), a PyQt GUI, and Excel storage via Pandas.

---

## Features

- Add **Income** and **Expense** transactions
- **Auto-create accounts** when a new account name is used
- View transactions for a given **month (YYYY-MM)** in a table
- View **Monthly Summary** (Income, Expense, Net)
- **Export** and **Import** Excel monthly reports
- Saves data through Excel file located in **storage** folder

---

## Requirements

- Python **3.10+**
- Packages:
  - `PyQt5`
  - `pandas`
  - `openpyxl` (read `.xlsx`)
  - `XlsxWriter` (write `.xlsx`)
- Code: pip install PyQt5 pandas openpyxl XlsxWriter