"""Printer sink interface."""
from abc import ABC, abstractmethod

from hardcopy.render import Receipt


class Printer(ABC):
    @abstractmethod
    def print(self, receipt: Receipt) -> None:
        """Raise on failure — the spooler handles retry/backoff."""
        ...
