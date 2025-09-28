from pathlib import Path
from storage.excelRepository import PandasExcelLedgerRepository
from services.transactions import TransactionService
from services.reporting import ReportingService
from interface.gui import run_gui

def main():
    here = Path(__file__).parent / "storage"
    repo_path = here / "excelTracker.xlsx"
    repo = PandasExcelLedgerRepository(_snapshot_path=repo_path)

    txsvc = TransactionService(repo)
    rpsvc = ReportingService(repo)
    run_gui(repo, txsvc, rpsvc)

if __name__ == "__main__":
    main()
