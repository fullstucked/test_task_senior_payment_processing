from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from domain.payment.enums.status import Status
from domain.payment.events import PaymentProcessedEvent
from presentation.ampq.v1.shared.schemas.base.base import EventData, event


@event
class NotifyEvent(BaseModel):
    payment_id: UUID
    amount: Decimal
    currency: str
    webhook_url: str
    status: Status
    reason: str | None = None


def notify_event_to_domain(event=EventData[NotifyEvent]) -> PaymentProcessedEvent:
    return PaymentProcessedEvent(
        payment_id=event.payload.payment_id,  # type: ignore
        amount=event.payload.amount,  # type: ignore
        currency=event.payload.currency,  # type: ignore
        reason=event.payload.reason,  # type: ignore
        status=event.payload.status,  # type: ignore
        webhook_url=event.payload.webhook_url,  # type: ignore
        id=event.id,  # type: ignore
        occured_at=event.occured_at,
    )
