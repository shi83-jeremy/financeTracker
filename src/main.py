from pathlib import Path
from storage.excelRepository import PandasExcelLedgerRepository
from services.reporting import ReportingService
from interface.gui import runGUI

def main():
    here = Path(__file__).parent / "storage"
    repo_path = here / "excelTracker.xlsx"
    repo = PandasExcelLedgerRepository(_snapshot_path=repo_path)

    rpsvc = ReportingService(repo)
    runGUI(repo, rpsvc)

if __name__ == "__main__":
    main()
