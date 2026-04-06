import os

from faststream.rabbit import RabbitBroker

broker = RabbitBroker(url=os.getenv('BROKER_URL'))
