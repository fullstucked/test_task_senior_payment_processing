from faststream.rabbit import RabbitQueue
from faststream.rabbit import QueueType

new_payments_queue = RabbitQueue(
    name='new_payment', routing_key='new', durable=True, queue_type=QueueType.QUORUM
)

new_payment_retry_queue_5s = RabbitQueue(
    name='payments.retry.5s',
    routing_key='retry.5s',
    durable=True,
    queue_type=QueueType.QUORUM,
    arguments={
        'x-message-ttl': 5000,
        'x-dead-letter-exchange': 'payments',
        'x-dead-letter-routing-key': 'new',
        'x-overflow': 'reject-publish',
        'x-dead-letter-strategy': 'at-least-once',
    },
)

new_payment_retry_queue_10s = RabbitQueue(
    name='payments.retry.10s',
    routing_key='retry.10s',
    durable=True,
    queue_type=QueueType.QUORUM,
    arguments={
        'x-message-ttl': 10000,
        'x-dead-letter-exchange': 'payments',
        'x-dead-letter-routing-key': 'new',
        'x-overflow': 'reject-publish',
        'x-dead-letter-strategy': 'at-least-once',
    },
)

new_payment_retry_queue_40s = RabbitQueue(
    name='payments.retry.40s',
    routing_key='retry.40s',
    durable=True,
    queue_type=QueueType.QUORUM,
    arguments={
        'x-message-ttl': 40000,
        'x-overflow': 'reject-publish',
        'x-dead-letter-exchange': 'payments',
        'x-dead-letter-routing-key': 'new',
        'x-dead-letter-strategy': 'at-least-once',
    },
)
