from typing import override

from application.payment.interfaces.webhook_sender import WebhookSender
from application.shared.utils.serialize_values import _serialize_value
from application.shared.use_cases.event_driven_use_case import EventDrivenUseCase
from domain.payment.enums.status import Status
from domain.payment.events import PaymentProcessedEvent


class SendNotificationUseCase(EventDrivenUseCase[PaymentProcessedEvent]):
    def __init__(self, webhook_sender: WebhookSender):
        self.webhook_sender = webhook_sender

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

        payload_dict = {k: _serialize_value(v) for k, v in payload.items()}

        await self.webhook_sender.send(url=event.webhook_url, payload=payload_dict, timeout=timeout)
