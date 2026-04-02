from presentation.ampq.v1.payments.events.process_payment import process_router
from presentation.ampq.v1.payments.events.notify_client import notify_router
import os

from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitExchange, RabbitQueue

from infra.shared.events.exchanges import payments_dlx, payments_exchange
from infra.shared.events.queue.dlq import dlq
from infra.shared.events.queue.new_payment import (
    new_payment_retry_queue_5s,
    new_payment_retry_queue_10s,
    new_payment_retry_queue_40s,
    new_payments_queue,
)
from infra.shared.events.queue.payment_notify import (
    notify_payments_queue,
    payment_notify_retry_queue_5s,
    payment_notify_retry_queue_10s,
    payment_notify_retry_queue_40s,
)


async def bind_queues_to_exch(
    broker: RabbitBroker, exch: RabbitExchange, queues: list[RabbitQueue]
):
    ch = (await broker.declare_exchange(exch),)

    for queue in queues:
        q = await broker.declare_queue(queue)
        await q.bind(ch[0], routing_key=queue.routing_key)


async def create_app() -> FastStream:

    broker = RabbitBroker(os.getenv('BROKER_URL'))
    await broker.connect()

    await bind_queues_to_exch(broker=broker, exch=payments_dlx, queues=[dlq])

    await bind_queues_to_exch(
        broker=broker,
        exch=payments_exchange,
        queues=[
            new_payments_queue,
            new_payment_retry_queue_5s,
            new_payment_retry_queue_10s,
            new_payment_retry_queue_40s,
        ],
    )

    await bind_queues_to_exch(
        broker=broker,
        exch=payments_exchange,
        queues=[
            notify_payments_queue,
            payment_notify_retry_queue_5s,
            payment_notify_retry_queue_10s,
            payment_notify_retry_queue_40s,
        ],
    )

    broker.include_router(notify_router)
    broker.include_router(process_router)

    app = FastStream(broker)

    return app


async def run_consumer():

    app = await create_app()
    await app.run()
