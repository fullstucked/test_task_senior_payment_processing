from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from domain.payment.enums.currency import Currency
from domain.payment.enums.status import Status
from domain.shared.event import DomainEvent

# For registry of events related to payment and future rebuilds
EVENT_REGISTRY: dict[str, type] = {}


def register_event(cls: type):
    EVENT_REGISTRY[cls.__name__] = cls
    return cls


def rebuild_event(row) -> PaymentDomainEvent:
    """
    Rebuild event from raw data
    """
    event_type = row['type']
    payload = row['payload']

    cls = EVENT_REGISTRY.get(event_type)
    if cls is None:
        raise ValueError(f'Unknown event type: {event_type}')

    # Inject metadata fields back into the payload
    payload['id'] = row['id']
    payload['occured_at'] = row['occured_at']

    return cls(**payload)


@register_event
@dataclass(slots=True)
class PaymentDomainEvent(DomainEvent):
    """
    Basic domain event class which stores
    __event_group__ param to handle
    by relative event handlers
    """

    __version__ = 1
    payment_id: UUID

    @classmethod
    def __event_group__(cls):
        return 'payments'

    @classmethod
    def __event_key__(cls) -> str:
        return '*'


@register_event
@dataclass(slots=True)
class PaymentCreatedEvent(PaymentDomainEvent):
    """
    Emmits at creation new
    """

    @classmethod
    def __event_key__(cls) -> str:
        return 'new'


@register_event
@dataclass(slots=True)
class PaymentProcessedEvent(PaymentDomainEvent):
    """
    Emmits at processing
    """

    amount: Decimal
    currency: Currency
    webhook_url: str

    status: Status
    reason: str | None = None

    @classmethod
    def __event_key__(cls) -> str:
        return 'processed'
