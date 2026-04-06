from abc import ABC, abstractmethod
from typing import Iterable

from domain.payment.events import PaymentDomainEvent


class AbstractPaymentEventBus(ABC):
    """Interface for event publisher to publish domain events."""

    @abstractmethod
    async def publish_payment_event(self, events: Iterable[PaymentDomainEvent]) -> None:
        """Publish multiple events in order."""
        raise NotImplementedError
