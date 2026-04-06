import json
from dataclasses import asdict
from typing import Iterable

import aio_pika
from faststream.rabbit.annotations import RabbitBroker

from application.payment.interfaces.event_bus import AbstractPaymentEventBus
from domain.payment.events import PaymentDomainEvent
from infra.payment.publisher.exchanges.payments import payments_exchange
from infra.shared.events.broker import broker
from infra.shared.utils.serialize_values import _serialize_value


class EventPublisherAMQP(AbstractPaymentEventBus):
    """Event publisher for publishing domain events to RabbitMQ."""

    def __init__(self, broker: RabbitBroker = broker) -> None:
        self.broker = broker

    async def publish_payment_event(self, events: Iterable[PaymentDomainEvent]) -> None:
        """
        Publish event to RabbitMQ.
        routing and exchange via `__event_*` and `queue` pararms of Domain Event
        """
        await self.broker.connect()
        try:
            for event in events:
                message = self._parse_event_to_message(event)
                await self.broker.publish(
                    message=message,
                    routing_key=f'{event.__event_key__()}',
                    exchange=payments_exchange,
                )
        except Exception as e:
            raise e

    def _parse_event_to_message(self, event: PaymentDomainEvent) -> aio_pika.Message:
        """
        Helper which translate event content to actual message 
        """
        event_dict: dict[str, object] = asdict(event)
        event_data = {
            'type': event.__class__.__name__,
            'id': _serialize_value(event.id),
            'occured_at': _serialize_value(event.occured_at),
            'payload': {
                k: _serialize_value(v)
                for k, v in event_dict.items()
                if not k.startswith('event_')
                or k.startswith('__')
                or k not in ('id', 'type', 'occured_at', 'queue')
            },
        }

        message_body = json.dumps(event_data)

        message = aio_pika.Message(
            body=message_body.encode(),
            content_type='application/json',
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        return message
