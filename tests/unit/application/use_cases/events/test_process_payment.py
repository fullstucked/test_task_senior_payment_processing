from decimal import Decimal
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from application.payment.use_cases.events.process_payment import ProcessPayment
from domain.payment.enums.currency import Currency
from domain.payment.enums.status import Status
from domain.payment.errors import PaymentBusinessRuleError
from domain.payment.events import PaymentCreatedEvent
from domain.payment.payment import Payment
from domain.payment.value_objects.amount import Amount
from domain.payment.value_objects.description import Description
from domain.payment.value_objects.id import PaymentId
from domain.payment.value_objects.idempotency_key import IdempotencyKey
from domain.payment.value_objects.metadata import Metadata
from domain.payment.value_objects.timestamp import Timestamp
from domain.payment.value_objects.webhook_url import WebhookUrl


@pytest.mark.asyncio
@patch(
    'application.payment.use_cases.events.process_payment.random', return_value=0.5
)  # force success
@patch('application.payment.use_cases.events.process_payment.uniform', return_value=0)  # skip sleep
async def test_process_payment_success(mock_uniform, mock_random):

    payment_id = uuid4()
    payment = Payment.rebuild(
        id=PaymentId.rebuild(payment_id),
        amount=Amount.rebuild(Decimal('100')),
        currency=Currency.USD,
        description=Description.rebuild('Test Payment'),
        metadata=Metadata.rebuild({}),
        status=Status.PENDING,
        key=IdempotencyKey.rebuild(uuid4()),
        webhook_url=WebhookUrl.rebuild('http://example.com'),
        created_at=Timestamp.rebuild(None),
        processed_at=None,
    )

    ####### Mocks
    # Mock repo
    mock_payments_repo = AsyncMock()
    mock_payments_repo.get_by_id = AsyncMock(return_value=payment)
    mock_payments_repo.update = AsyncMock()

    # Mock UoW
    mock_uow = AsyncMock()
    mock_uow.__aenter__.return_value = mock_uow
    mock_uow.__aexit__.return_value = None
    mock_uow.payments = mock_payments_repo

    # Mock event bus
    mock_event_bus = AsyncMock()
    mock_event_bus.publish_payment_event = AsyncMock()

    ####### Mocks

    # Create fake event and run UC
    event = PaymentCreatedEvent(payment_id=payment_id)
    use_case = ProcessPayment(uow=mock_uow, event_bus=mock_event_bus)
    await use_case(event)

    # Assertions
    assert payment.status == Status.OK
    mock_event_bus.publish_payment_event.assert_awaited()
    mock_payments_repo.update.assert_awaited_once_with(payment=payment)


@pytest.mark.asyncio
@patch(
    'application.payment.use_cases.events.process_payment.random', return_value=0.95
)  # force failure
@patch('application.payment.use_cases.events.process_payment.uniform', return_value=0)  # skip sleep
async def test_process_payment_failure(mock_uniform, mock_random):
    # Prepare fake payment
    payment_id = uuid4()
    payment = Payment.rebuild(
        id=PaymentId.rebuild(payment_id),
        amount=Amount.rebuild(Decimal('100')),
        currency=Currency.USD,
        description=Description.rebuild('Test Payment'),
        metadata=Metadata.rebuild({}),
        status=Status.PENDING,
        key=IdempotencyKey.rebuild(uuid4()),
        webhook_url=WebhookUrl.rebuild('http://example.com'),
        created_at=Timestamp.rebuild(None),
        processed_at=None,
    )

    # Mock repo
    mock_payments_repo = AsyncMock()
    mock_payments_repo.get_by_id = AsyncMock(return_value=payment)
    mock_payments_repo.update = AsyncMock()

    # Mock UoW
    mock_uow = AsyncMock()
    mock_uow.__aenter__.return_value = mock_uow
    mock_uow.__aexit__.return_value = None
    mock_uow.payments = mock_payments_repo

    # Mock event bus
    mock_event_bus = AsyncMock()
    mock_event_bus.publish_payment_event = AsyncMock()

    # Create use case
    use_case = ProcessPayment(uow=mock_uow, event_bus=mock_event_bus)

    # Create fake event
    event = PaymentCreatedEvent(payment_id=payment_id)

    # Run use case
    await use_case(event)

    # Assertions
    assert payment.status == Status.FAIL
    mock_event_bus.publish_payment_event.assert_awaited()
    mock_payments_repo.update.assert_awaited_once_with(payment=payment)


@pytest.mark.asyncio
@patch('application.payment.use_cases.events.process_payment.random', return_value=0.1)
@patch('application.payment.use_cases.events.process_payment.uniform', return_value=0)
async def test_process_payment_already_processed(mock_uniform, mock_random):
    # Payment already succeeded
    payment_id = uuid4()
    payment = Payment.rebuild(
        id=PaymentId.rebuild(payment_id),
        amount=Amount.rebuild(Decimal('100')),
        currency=Currency.USD,
        description=Description.rebuild('Test Payment'),
        metadata=Metadata.rebuild({}),
        status=Status.OK,  # already succeeded
        key=IdempotencyKey.rebuild(uuid4()),
        webhook_url=WebhookUrl.rebuild('http://example.com'),
        created_at=Timestamp.rebuild(None),
        processed_at=Timestamp.now(),
    )

    mock_payments_repo = AsyncMock()
    mock_payments_repo.get_by_id = AsyncMock(return_value=payment)
    mock_payments_repo.update = AsyncMock()

    mock_uow = AsyncMock()
    mock_uow.__aenter__.return_value = mock_uow
    mock_uow.__aexit__.return_value = None
    mock_uow.payments = mock_payments_repo

    mock_event_bus = AsyncMock()
    mock_event_bus.publish_payment_event = AsyncMock()

    use_case = ProcessPayment(uow=mock_uow, event_bus=mock_event_bus)
    event = PaymentCreatedEvent(payment_id=payment_id)

    with pytest.raises(PaymentBusinessRuleError):
        await use_case(event)

    # Assert: payment not re-processed
    assert payment.status == Status.OK
    mock_payments_repo.update.assert_not_awaited()
    mock_event_bus.publish_payment_event.assert_not_awaited()


@pytest.mark.asyncio
@patch('application.payment.use_cases.events.process_payment.random', return_value=0.5)
@patch('application.payment.use_cases.events.process_payment.uniform', return_value=0)
async def test_process_payment_service_failure(mock_uniform, mock_random):
    # Payment is pending
    payment_id = uuid4()
    payment = Payment.rebuild(
        id=PaymentId.rebuild(payment_id),
        amount=Amount.rebuild(Decimal('100')),
        currency=Currency.USD,
        description=Description.rebuild('Test Payment'),
        metadata=Metadata.rebuild({}),
        status=Status.PENDING,
        key=IdempotencyKey.rebuild(uuid4()),
        webhook_url=WebhookUrl.rebuild('http://example.com'),
        created_at=Timestamp.rebuild(None),
        processed_at=None,
    )

    mock_payments_repo = AsyncMock()
    mock_payments_repo.get_by_id = AsyncMock(return_value=payment)
    mock_payments_repo.update = AsyncMock()

    mock_uow = AsyncMock()
    mock_uow.__aenter__.return_value = mock_uow
    mock_uow.__aexit__.return_value = None
    mock_uow.payments = mock_payments_repo
    mock_uow.commit = AsyncMock(side_effect=RuntimeError('DB commit failed'))

    mock_event_bus = AsyncMock()
    mock_event_bus.publish_payment_event = AsyncMock()

    use_case = ProcessPayment(uow=mock_uow, event_bus=mock_event_bus)
    event = PaymentCreatedEvent(payment_id=payment_id)

    # Act and Assert
    with pytest.raises(RuntimeError):
        await use_case(event)
