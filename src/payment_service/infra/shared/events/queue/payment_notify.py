from faststream.rabbit import RabbitQueue
from faststream.rabbit import QueueType

notify_payments_queue = RabbitQueue(
    name='payment_notification',
    routing_key='processed',
    durable=True,
    queue_type=QueueType.QUORUM,
)

payment_notify_retry_queue_5s = RabbitQueue(
    name='notification.retry.5s',
    routing_key='notify.retry.5s',
    durable=True,
    queue_type=QueueType.QUORUM,
    arguments={
        'x-message-ttl': 5000,
        'x-dead-letter-exchange': 'payments',
        'x-dead-letter-routing-key': 'processed',
        'x-overflow': 'reject-publish',
        'x-dead-letter-strategy': 'at-least-once',
    },
)

payment_notify_retry_queue_10s = RabbitQueue(
    name='notification.retry.10s',
    routing_key='notify.retry.10s',
    durable=True,
    queue_type=QueueType.QUORUM,
    arguments={
        'x-message-ttl': 10000,
        'x-dead-letter-exchange': 'payments',
        'x-dead-letter-routing-key': 'processed',
        'x-overflow': 'reject-publish',
        'x-dead-letter-strategy': 'at-least-once',
    },
)

payment_notify_retry_queue_40s = RabbitQueue(
    name='notification.retry.40s',
    routing_key='notify.retry.40s',
    durable=True,
    queue_type=QueueType.QUORUM,
    arguments={
        'x-message-ttl': 40000,
        'x-dead-letter-exchange': 'payments',
        'x-dead-letter-routing-key': 'processed',
        'x-overflow': 'reject-publish',
        'x-dead-letter-strategy': 'at-least-once',
    },
)

