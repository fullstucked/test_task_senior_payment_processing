from faststream import AckPolicy, Depends
from faststream.rabbit import RabbitBroker, RabbitMessage, RabbitRouter

from application.payment.use_cases.events.process_payment import ProcessPayment
from domain.payment.errors import PaymentBusinessRuleError
from infra.payment.uow import SqlAlchemyUnitOfWork
from infra.payment.publisher.exchanges.payments import payments_exchange
from infra.shared.queues.retries import create_retry_queues
from infra.payment.publisher.queues.dlq import dlq
from infra.payment.publisher.exchanges.dead import payments_dlx
from infra.payment.publisher.queues.new_payment import new_payments_queue
from presentation.ampq.v1.payments.dependencies import get_broker, get_process_payment_uc, get_uow
from presentation.ampq.v1.payments.schemas.payment import NewPaymentEvent, new_pay_to_domain

process_router = RabbitRouter()


DELAY_BASE = 5  # in seconds for exponential-time retries
MAX_ATTEMPTS = 3  # max retty_attempts

retry_routing_queues = create_retry_queues(
    after_expire_exch=payments_exchange,
    base_queue=new_payments_queue,
    retry_base=DELAY_BASE,
    max_attempt=MAX_ATTEMPTS,
)


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
    async with uow:
        claimed = await uow.outbox.mark_in_process(event.id)
    if claimed or attempt > 0 and attempt < MAX_ATTEMPTS:
        try:
            await uc(event=event)

            async with uow:
                await uow.outbox.mark_done(event.id)
                await uow.commit()

        except PaymentBusinessRuleError as e:
            # Already processed
            if e == PaymentBusinessRuleError('Already processed'):
                pass

        except Exception:
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
                    msg.body, exchange=payments_dlx, queue=dlq, headers={'x-attempt': attempt}
                )

    await msg.ack()
