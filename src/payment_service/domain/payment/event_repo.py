from uuid import UUID
from abc import ABC, abstractmethod
from typing import Iterable

from domain.payment.events import PaymentDomainEvent


class PaymentEventRepository(ABC):
    """Event presistance abstraction for Payment entity"""

    @abstractmethod
    async def get_pendings(self, limit: int = 50) -> list[PaymentDomainEvent]:
        """
        Fetch last `limit` events
        """
        raise NotImplementedError

    @abstractmethod
    async def add(self, events: Iterable[PaymentDomainEvent]) -> None:
        """
        Saves new Payment event
        """
        raise NotImplementedError
    @abstractmethod
    async def mark_done(self, event_id: UUID) -> None:
        """
        Mark event as done
        """
        raise NotImplementedError

    async def mark_failed(self, event_id: UUID) -> None:
        """
        Mark event as failed
        """
        raise NotImplementedError
