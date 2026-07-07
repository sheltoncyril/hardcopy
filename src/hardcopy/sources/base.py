"""Source plugin interface. Implement this + emit Events = new notification source."""
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from hardcopy.models import Event


class Source(ABC):
    name: str

    @abstractmethod
    def events(self) -> AsyncIterator[Event]:
        """Yield normalized events forever. Pollers sleep internally;
        push sources (webhooks) yield as payloads arrive."""
        ...
