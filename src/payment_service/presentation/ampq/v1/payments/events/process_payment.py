from presentation.ampq.v1.payments.dependencies import get_uow
from infra.payment.uow import SqlAlchemyUnitOfWork
from faststream import AckPolicy, Depends
from faststream.rabbit import RabbitBroker, RabbitMessage, RabbitRouter

from application.payment.use_cases.events.process_payment import ProcessPayment
from infra.shared.events.exchanges import payments_dlx, payments_exchange
from infra.shared.events.queue.dlq import dlq
from infra.shared.events.queue.new_payment import (
    new_payment_retry_queue_5s,
    new_payment_retry_queue_10s,
    new_payment_retry_queue_40s,
    new_payments_queue,
)
from presentation.ampq.v1.payments.dependencies import get_broker, get_process_payment_uc
from presentation.ampq.v1.payments.schemas.payment import NewPaymentEvent, new_pay_to_domain

process_router = RabbitRouter()


@process_router.subscriber(
    queue=new_payments_queue, exchange=payments_exchange, ack_policy=AckPolicy.MANUAL
)
async def handle_payment_processing(
    msg: RabbitMessage,
    uc: ProcessPayment = Depends(get_process_payment_uc),
    broker: RabbitBroker = Depends(get_broker),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> None:
    """Handler for processing new payment events."""

    headers = msg.headers or {}
    attempt = headers.get('x-attempt', 0)

    processed_event = NewPaymentEvent.model_validate_json(msg.body)
    event = new_pay_to_domain(processed_event)
    try:
        await uc(event=event)

    except Exception:
        await broker.connect()
        MAX_RETRIES: int = 3
        if attempt < MAX_RETRIES:
            retry_routing_queues = (
                new_payment_retry_queue_5s,
                new_payment_retry_queue_10s,
                new_payment_retry_queue_40s,
            )
            await broker.publish(
                msg.body,
                exchange=payments_dlx,
                routing_key=retry_routing_queues[attempt].routing_key,
                headers={'x-attempt': attempt + 1},
            )
        else:
            await broker.publish(
                msg.body, exchange=payments_dlx, queue=dlq, headers={'x-attempt': attempt}
            )
            await uow.outbox.mark_failed(event_id=event.id)

    await msg.ack()
