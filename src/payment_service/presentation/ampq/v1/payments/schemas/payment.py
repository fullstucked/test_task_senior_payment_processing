from uuid import UUID

from pydantic import BaseModel

from domain.payment.events import PaymentCreatedEvent
from presentation.ampq.v1.shared.schemas.base.base import EventData, event


@event
class NewPaymentEvent(BaseModel):
    payment_id: UUID


def new_pay_to_domain(event=EventData[NewPaymentEvent]) -> PaymentCreatedEvent:
    return PaymentCreatedEvent(
        payment_id=event.payload.payment_id,  # type: ignore
        id=event.id,  # type:ignore
        occured_at=event.occured_at,
    )
