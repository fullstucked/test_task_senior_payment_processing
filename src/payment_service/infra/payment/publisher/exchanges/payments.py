from faststream.rabbit import ExchangeType, RabbitExchange

payments_exchange = RabbitExchange(name='payments', type=ExchangeType.TOPIC)
