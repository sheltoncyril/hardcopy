"""Real printer via python-escpos. One class, both transports."""
from hardcopy.printers.base import Printer
from hardcopy.render import Receipt


class EscposPrinter(Printer):
    def __init__(self, cfg: dict) -> None:
        self.cfg = cfg  # printer section of config.yaml

    def _connect(self):
        from escpos.printer import Network, Usb

        if self.cfg["type"] == "usb":
            u = self.cfg["usb"]
            return Usb(u["vendor_id"], u["product_id"])
        n = self.cfg["network"]
        return Network(n["host"], port=n.get("port", 9100))

    def print(self, receipt: Receipt) -> None:
        p = self._connect()  # connect per print: survives printer power-cycles
        try:
            for line in receipt.lines:
                p.text(line + "\n")
            if receipt.qr:
                p.qr(receipt.qr, size=6, center=True)
            p.cut()
        finally:
            p.close()
