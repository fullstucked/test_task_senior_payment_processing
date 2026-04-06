from decimal import Decimal
from uuid import UUID

import pytest

from domain.payment.enums.currency import Currency
from domain.payment.enums.status import Status
from domain.payment.errors import PaymentBusinessRuleError
from domain.payment.payment import Payment
from domain.payment.value_objects.amount import Amount
from domain.payment.value_objects.description import Description
from domain.payment.value_objects.id import PaymentId
from domain.payment.value_objects.idempotency_key import IdempotencyKey
from domain.payment.value_objects.metadata import Metadata
from domain.payment.value_objects.timestamp import Timestamp
from domain.payment.value_objects.webhook_url import WebhookUrl


def test_unprocessed_payment_rebuild():
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

    # Rebuild the payment from its attributes
    rebuilt_payment = Payment.rebuild(
        id=PaymentId.rebuild(payment.id.value),
        amount=Amount.rebuild(payment.amount.value),
        currency=Currency(payment.currency),
        description=Description.rebuild(payment.description.value),
        metadata=Metadata.rebuild(payment.metadata.value),
        key=IdempotencyKey.rebuild(payment.key.value),
        status=Status(payment.status.value),
        processed_at=Timestamp.rebuild(None),
        webhook_url=WebhookUrl.rebuild(payment.webhook_url.value),
        created_at=Timestamp.rebuild(payment.created_at.value),
    )

    # Assert the rebuilt payment has the same properties as the original one
    assert rebuilt_payment.id == payment.id
    assert rebuilt_payment.amount == payment.amount
    assert rebuilt_payment.currency == payment.currency
    assert rebuilt_payment.description == payment.description
    assert rebuilt_payment.metadata == payment.metadata
    assert rebuilt_payment.key == payment.key
    assert rebuilt_payment.status == payment.status
    assert rebuilt_payment.webhook_url == payment.webhook_url
    assert rebuilt_payment.processed_at == payment.processed_at
    assert rebuilt_payment.created_at == payment.created_at


def test_payment_rebuild_with_processed_at():
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

    # Rebuild the payment from its attributes
    rebuilt_payment = Payment.rebuild(
        id=PaymentId.rebuild(payment.id.value),
        amount=Amount.rebuild(payment.amount.value),
        currency=Currency(payment.currency),
        description=Description.rebuild(payment.description.value),
        metadata=Metadata.rebuild(payment.metadata.value),
        key=IdempotencyKey.rebuild(payment.key.value),
        status=Status(payment.status.value),
        webhook_url=WebhookUrl.rebuild(payment.webhook_url.value),
        processed_at=Timestamp.rebuild(Timestamp.now()),
        created_at=Timestamp.rebuild(payment.created_at.value),
    )

    # Assert the rebuilt payment has the same properties as the original one
    assert rebuilt_payment.id == payment.id
    assert rebuilt_payment.amount == payment.amount
    assert rebuilt_payment.currency == payment.currency
    assert rebuilt_payment.description == payment.description
    assert rebuilt_payment.metadata == payment.metadata
    assert rebuilt_payment.key == payment.key
    assert rebuilt_payment.status == payment.status
    assert rebuilt_payment.webhook_url == payment.webhook_url
    if payment.processed_at:
        assert rebuilt_payment.processed_at == payment.processed_at
    assert rebuilt_payment.created_at == payment.created_at


def test_mark_as_succeeded_invalid_state():
    # Test marking as succeeded when not in PENDING state
    payment = Payment(
        amount=Amount(Decimal('100.00')),
        currency='USD',
        description=Description('Payment test descr'),
        metadata=Metadata({'key': 'value'}),
        key=IdempotencyKey(UUID('9b2252e4-0929-424d-a98c-719b4f64f085')),
        webhook_url=WebhookUrl('https://webhook.url'),
        status=Status.OK,
    )

    with pytest.raises(PaymentBusinessRuleError, match='Already processed'):
        payment.mark_as_succeeded()


def test_mark_as_failed_invalid_state():
    # Test marking as failed when not in PENDING state
    payment = Payment(
        amount=Amount(Decimal('100.00')),
        currency='USD',
        description=Description('Payment test descr'),
        metadata=Metadata({'key': 'value'}),
        key=IdempotencyKey(UUID('9b2252e4-0929-424d-a98c-719b4f64f085')),
        webhook_url=WebhookUrl('https://webhook.url'),
        status=Status.OK,
    )

    with pytest.raises(PaymentBusinessRuleError, match='Already processed'):
        payment.mark_as_failed('Some failure reason')


def test_entity_equality():
    # Same ID, same entity type
    payment1 = Payment(
        amount=Amount(Decimal('100.00')),
        currency='USD',
        description=Description('Payment test'),
        metadata=Metadata({'key': 'value'}),
        key=IdempotencyKey(UUID('9b2252e4-0929-424d-a98c-719b4f64f085')),
        webhook_url=WebhookUrl('https://webhook.url'),
    )
    payment2 = Payment.rebuild(
        id=payment1.id,
        amount=payment1.amount,
        currency=payment1.currency,
        description=payment1.description,
        metadata=payment1.metadata,
        key=payment1.key,
        webhook_url=payment1.webhook_url,
    )

    assert payment1 == payment2  # Same ID, same type


def test_entity_inequality():
    # Different IDs, different entities
    payment1 = Payment(
        amount=Amount(Decimal('100.00')),
        currency='USD',
        description=Description('Payment test'),
        metadata=Metadata({'key': 'value'}),
        key=IdempotencyKey(UUID('9b2252e4-0929-424d-a98c-719b4f64f085')),
        webhook_url=WebhookUrl('https://webhook.url'),
    )
    payment2 = Payment(
        amount=Amount(Decimal('100.00')),
        currency='USD',
        description=Description('Payment test'),
        metadata=Metadata({'key': 'value'}),
        key=IdempotencyKey(UUID('9b2252e4-0929-424d-a98c-719b4f64f085')),
        webhook_url=WebhookUrl('https://webhook.url'),
    )

    assert payment1 != payment2  # Different entities
