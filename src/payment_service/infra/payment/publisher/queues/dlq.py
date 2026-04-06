from faststream.rabbit import QueueType
from faststream.rabbit import RabbitQueue

dlq = RabbitQueue(name='payments.dlq', durable=True, queue_type=QueueType.QUORUM)

