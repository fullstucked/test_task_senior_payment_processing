from abc import ABC, abstractmethod
from typing import Iterable

from domain.shared.event import DomainEvent


class AbstractEventBus(ABC):
    """Interface for event publisher to publish domain events."""

    @abstractmethod
    async def publish_event(self, events: Iterable[DomainEvent]) -> None:
        """Publish multiple events in order."""
        raise NotImplementedError
