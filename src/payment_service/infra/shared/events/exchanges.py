from faststream.rabbit import ExchangeType, RabbitExchange

payments_exchange = RabbitExchange('payments', type=ExchangeType.TOPIC)
payments_dlx = RabbitExchange('payments.dlx', type=ExchangeType.TOPIC)
