
from faststream import FastStream

from bootstrap.consumer.utils.queue_binds import bind_queues_to_exch, bind_queues_with_retry_to_exch
from infra.payment.publisher.exchanges.dead import payments_dlx
from infra.payment.publisher.exchanges.payments import payments_exchange
from infra.payment.publisher.queues.new_payment import new_payments_queue
from infra.payment.publisher.queues.payment_notify import notify_payments_queue
from infra.payment.publisher.queues.dlq import dlq
from presentation.ampq.v1.payments.events.process_payment import process_router
from presentation.ampq.v1.payments.dependencies import get_broker
from presentation.ampq.v1.payments.events.notify_client import notify_router
from presentation.ampq.v1.payments.events.notify_client import (
    DELAY_BASE as NOTIFY_DELAY_BASE,
    MAX_ATTEMPTS as NOTIFY_MAX_ATTEMPTS,
)
from presentation.ampq.v1.payments.events.process_payment import (
    DELAY_BASE as PROCESS_DELAY_BASE,
    MAX_ATTEMPTS as PROCESS_MAX_ATTEMTS,
)

async def create_app() -> FastStream:
    """
    Default app factory with creating retry queues
    """

    broker = get_broker()
    await broker.connect()

    ### Dead letter queue
    await bind_queues_to_exch(broker=broker, exch=payments_dlx, queues=[dlq])

    ### New payment creation
    await bind_queues_with_retry_to_exch(
        broker=broker,
        exch=payments_exchange,
        dead_exch=payments_dlx,
        base_queue=new_payments_queue,
        retry_base=PROCESS_DELAY_BASE,
        max_attempt=PROCESS_MAX_ATTEMTS,
    )

    # Notification_creation
    await bind_queues_with_retry_to_exch(
        broker=broker,
        exch=payments_exchange,
        dead_exch=payments_dlx,
        base_queue=notify_payments_queue,
        retry_base=NOTIFY_DELAY_BASE,
        max_attempt=NOTIFY_MAX_ATTEMPTS,
    )

    broker.include_router(notify_router)
    broker.include_router(process_router)

    app = FastStream(broker)

    return app


async def run_consumer():
    app = await create_app()
    await app.run()
