from faststream.rabbit import RabbitBroker
import os


broker = RabbitBroker(url=os.getenv('BROKER_URL'))
