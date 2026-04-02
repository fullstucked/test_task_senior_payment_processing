import json
from dataclasses import asdict
from datetime import datetime
from typing import Iterable

import aio_pika

from application.payment.event_bus import AbstractPaymentEventBus
from domain.payment.events import PaymentDomainEvent
from infra.shared.events.broker import broker
from infra.shared.events.exchanges import payments_exchange


class EventPublisherAMQP(AbstractPaymentEventBus):
    """Event publisher for publishing domain events to RabbitMQ."""

    def __init__(self) -> None:
        """Initialize event publisher with RabbitMQ configuration."""
        self.broker = broker

    async def publish_payment_event(self, events: Iterable[PaymentDomainEvent]) -> None:
        """Publish event to RabbitMQ."""
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

    @staticmethod
    def _serialize_value(value: object) -> str | int | float | bool | datetime | None:
        """Serializes value to be JSON-compatible."""
        if isinstance(value, str):
            return value
        if isinstance(value, (int, float, bool)):
            return value
        if isinstance(value, datetime):
            return value.isoformat()
        if value is None:
            return None
        return str(value)

    def _parse_event_to_message(self, event: PaymentDomainEvent) -> aio_pika.Message:
        event_dict: dict[str, object] = asdict(event)
        event_data = {
            'type': event.__class__.__name__,
            'id': self._serialize_value(event.id),
            'occured_at': self._serialize_value(event.occured_at),
            'payload': {
                k: self._serialize_value(v)
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
