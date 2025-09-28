class Account:
    def __init__(self, name: str, type: str = "CASH"):
        self.name = name
        self.type = type

    def __repr__(self) -> str:
        return f"Account(name={self.name!r}, type={self.type!r})"