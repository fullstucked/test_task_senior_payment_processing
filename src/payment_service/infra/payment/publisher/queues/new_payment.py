from faststream.rabbit import RabbitQueue
from faststream.rabbit import QueueType

new_payments_queue = RabbitQueue(
    name='new_payment', routing_key='new', durable=True, queue_type=QueueType.QUORUM
)
