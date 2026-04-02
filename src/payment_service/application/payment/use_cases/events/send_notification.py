from application.payment.uow import AbstractPaymentUnitOfWork
from datetime import datetime
from typing import override

import httpx

from application.shared.event_based_use_case import EventDrivenUseCase
from domain.payment.enums.status import Status
from domain.payment.events import PaymentProcessedEvent


class SendNotificationUseCase(EventDrivenUseCase[PaymentProcessedEvent]):
    def __init__(self, uow: AbstractPaymentUnitOfWork):
        self._uow: AbstractPaymentUnitOfWork = uow

    @override
    async def __call__(self, event: PaymentProcessedEvent, timeout=5):

        if event.status != Status.OK:
            payload = {
                'payment_id': event.payment_id,
                'status': event.status.value,
                'reason': event.reason,
            }
        else:
            payload = {
                'payment_id': event.payment_id,
                'status': event.status.value,
                'amount': event.amount,
                'currency': event.currency,
            }
        payload_dict = {k: self._serialize_value(v) for k, v in payload.items()}
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                resp = await client.post(event.webhook_url, json=payload_dict)

                if resp.status_code < 300:
                    return True
                    await self._uow.outbox.mark_done(event.id)

            except Exception as exc:
                raise exc

    @staticmethod
    def _serialize_value(value: object) -> str | int | float | bool | datetime | None:
        """Serializes value to be JSON-compatible."""
        if isinstance(value, str):
            return value
        if isinstance(value, (int, float, bool)):
            return value
        if isinstance(value, datetime):
            return value.isoformat()
        if value is None:
            return None
        return str(value)
