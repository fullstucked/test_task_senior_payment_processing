from faststream.rabbit import ExchangeType, RabbitExchange

payments_dlx = RabbitExchange(name='payments.dlx', type=ExchangeType.TOPIC)
