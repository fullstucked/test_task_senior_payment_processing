from decimal import Decimal
from uuid import UUID

from domain.payment.enums.currency import Currency
from domain.payment.enums.status import Status
from domain.payment.events import PaymentCreatedEvent, PaymentProcessedEvent
from domain.payment.payment import Payment
from domain.payment.value_objects.amount import Amount
from domain.payment.value_objects.description import Description
from domain.payment.value_objects.idempotency_key import IdempotencyKey
from domain.payment.value_objects.metadata import Metadata
from domain.payment.value_objects.webhook_url import WebhookUrl


def test_payment_creation_event():
    amount = Amount(Decimal('100.00'))
    currency = Currency('USD')
    description = Description('Payment for services')
    metadata = Metadata(value={'order_id': '12345'})
    key = IdempotencyKey(UUID('9b2252e4-0929-424d-a98c-719b4f64f085'))
    webhook_url = WebhookUrl('https://webhook.url')

    # Create the payment
    payment = Payment(
        amount=amount,
        currency=currency,
        description=description,
        metadata=metadata,
        key=key,
        webhook_url=webhook_url,
    )

    # Check that the event is recorded
    events = payment.get_events()
    assert len(events) == 1
    assert isinstance(events[0], PaymentCreatedEvent)
    assert events[0].payment_id == payment.id.value


def test_payment_mark_as_succeeded():
    amount = Amount(Decimal('100.00'))
    currency = Currency('USD')
    description = Description('Payment for services')
    metadata = Metadata(value={'order_id': '12345'})
    key = IdempotencyKey(UUID('9b2252e4-0929-424d-a98c-719b4f64f085'))
    webhook_url = WebhookUrl('https://webhook.url')

    # Create the payment
    payment = Payment(
        amount=amount,
        currency=currency,
        description=description,
        metadata=metadata,
        key=key,
        webhook_url=webhook_url,
    )

    # Mark as succeeded
    payment.mark_as_succeeded()

    # Check that the PaymentProcessedEvent is recorded
    events = payment.get_events()
    assert len(events) == 2  # One for creation and one for success
    assert isinstance(events[1], PaymentProcessedEvent)
    assert events[1].status == Status.OK
    assert events[1].payment_id == payment.id.value


def test_payment_mark_as_failed():
    amount = Amount(Decimal('100.00'))
    currency = Currency('USD')
    description = Description('Payment for services')
    metadata = Metadata(value={'order_id': '12345'})
    key = IdempotencyKey(UUID('9b2252e4-0929-424d-a98c-719b4f64f085'))
    webhook_url = WebhookUrl('https://webhook.url')

    # Create the payment
    payment = Payment(
        amount=amount,
        currency=currency,
        description=description,
        metadata=metadata,
        key=key,
        webhook_url=webhook_url,
    )

    # Mark as failed
    payment.mark_as_failed('Payment gateway error')

    # Check that the PaymentProcessedEvent is recorded
    events = payment.get_events()
    assert len(events) == 2  # One for creation and one for failure
    assert isinstance(events[1], PaymentProcessedEvent)
    assert events[1].status == Status.FAIL
    assert events[1].payment_id == payment.id.value
    assert events[1].reason == 'Payment gateway error'
