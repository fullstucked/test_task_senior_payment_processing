from infra.payment.uow import SqlAlchemyUnitOfWork
from presentation.ampq.v1.payments.dependencies import get_uow
from faststream import AckPolicy, Depends
from faststream.rabbit import RabbitBroker, RabbitMessage, RabbitRouter

from application.payment.use_cases.events.send_notification import SendNotificationUseCase
from infra.shared.events.exchanges import payments_dlx, payments_exchange
from infra.shared.events.queue.dlq import dlq
from infra.shared.events.queue.payment_notify import (
    notify_payments_queue,
    payment_notify_retry_queue_5s,
    payment_notify_retry_queue_10s,
    payment_notify_retry_queue_40s,
)
from presentation.ampq.v1.payments.dependencies import get_broker, get_notification_event_uc
from presentation.ampq.v1.payments.schemas.notification import NotifyEvent, notify_event_to_domain

notify_router = RabbitRouter()


@notify_router.subscriber(
    queue=notify_payments_queue, exchange=payments_exchange, ack_policy=AckPolicy.MANUAL
)
async def handle_notify_client(
    msg: RabbitMessage,
    uc: SendNotificationUseCase = Depends(get_notification_event_uc),
    broker: RabbitBroker = Depends(get_broker),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> None:
    """Handler for sending notifications to webhook."""

    headers = msg.headers or {}
    attempt = headers.get('x-attempt', 0)

    notify_event = NotifyEvent.model_validate_json(msg.body)
    event = notify_event_to_domain(notify_event)

    try:
        await uc(event=event)

    except Exception:
        await broker.connect()
        MAX_RETRIES: int = 3
        if attempt < MAX_RETRIES:
            retry_queues = (
                payment_notify_retry_queue_5s,
                payment_notify_retry_queue_10s,
                payment_notify_retry_queue_40s,
            )
            await broker.publish(
                msg.body,
                exchange=payments_dlx,
                routing_key=retry_queues[attempt].routing_key,
                headers={'x-attempt': attempt + 1},
            )

        else:
            await broker.publish(
                msg.body, exchange=payments_dlx, routing_key=dlq.routing_key, headers={'x-attempt': attempt}
            )
            await uow.outbox.mark_failed(event_id=event.id)

    await msg.ack()
