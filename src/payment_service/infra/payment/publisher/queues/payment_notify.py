from faststream.rabbit import RabbitQueue
from faststream.rabbit import QueueType

notify_payments_queue = RabbitQueue(
    name='payment_notification', routing_key='processed', durable=True, queue_type=QueueType.QUORUM
)
