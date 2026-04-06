from faststream import AckPolicy, Depends
from faststream.rabbit import RabbitBroker, RabbitMessage, RabbitRouter

from application.payment.use_cases.events.send_notification import SendNotificationUseCase
from infra.shared.queues.retries import create_retry_queues
from infra.payment.uow import SqlAlchemyUnitOfWork
from infra.payment.publisher.queues.dlq import dlq
from infra.payment.publisher.exchanges.dead import payments_dlx
from infra.payment.publisher.queues.payment_notify import notify_payments_queue
from infra.payment.publisher.exchanges.payments import payments_exchange
from presentation.ampq.v1.payments.dependencies import get_uow
from presentation.ampq.v1.payments.dependencies import get_broker, get_notification_event_uc
from presentation.ampq.v1.payments.schemas.notification import NotifyEvent, notify_event_to_domain


notify_router = RabbitRouter()

DELAY_BASE = 5  # in seconds for exponential-time retries
MAX_ATTEMPTS = 3  # max retty_attempts

# Creating retry_routing_queues where message will be pushed
## in case unsuccess attempt
retry_routing_queues = create_retry_queues(
    base_queue=notify_payments_queue,
    after_expire_exch=payments_exchange,
    retry_base=DELAY_BASE,
    max_attempt=MAX_ATTEMPTS,
)


@notify_router.subscriber(
    queue=notify_payments_queue, exchange=payments_exchange, ack_policy=AckPolicy.MANUAL
)
async def handle_notify_client(
    msg: RabbitMessage,
    uc: SendNotificationUseCase = Depends(get_notification_event_uc),
    broker: RabbitBroker = Depends(get_broker),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> None:
    """Handler for events which should send notifications to webhook."""

    headers = msg.headers or {}
    attempt = headers.get('x-attempt', 0)

    notify_event = NotifyEvent.model_validate_json(msg.body)
    event = notify_event_to_domain(notify_event)

    async with uow:
        # Check if already handl
        ## because connected to external stuff and can be sensetive for retries
        claimed = await uow.outbox.mark_in_process(event_id=event.id)
        await uow.commit()

    if claimed or attempt > 0:
        try:
            await uc(event=event)
            async with uow:
                await uow.outbox.mark_done(event.id)
                await uow.commit()

        except Exception:
            # additional retries
            await broker.connect()
            if attempt < MAX_ATTEMPTS:
                await broker.publish(
                    msg.body,
                    exchange=payments_dlx,
                    routing_key=retry_routing_queues[attempt].routing_key,
                    headers={'x-attempt': attempt + 1},
                )

            else:
                async with uow:
                    await uow.outbox.mark_failed(event_id=event.id)
                    await uow.commit()

                await broker.publish(
                    msg.body,
                    exchange=payments_dlx,
                    routing_key=dlq.routing_key,
                    headers={'x-attempt': attempt},
                )

    await msg.ack()
