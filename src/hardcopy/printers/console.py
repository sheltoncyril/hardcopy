"""Dev/fallback printer: writes the receipt to stdout."""
from hardcopy.printers.base import Printer
from hardcopy.render import Receipt


class ConsolePrinter(Printer):
    def print(self, receipt: Receipt) -> None:
        print("┌" + "─" * 34 + "┐")
        for line in receipt.lines:
            print(f"│ {line:<32} │")
        if receipt.qr:
            print(f"│ [QR] {receipt.qr[:26]:<26} │")
        print("└" + "─" * 34 + "┘")
