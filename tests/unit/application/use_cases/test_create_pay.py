from decimal import Decimal
from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4

import pytest

from application.payment.use_cases.create_payment import CreatePaymentDTO, CreatePaymentUseCase
from domain.payment.enums.currency import Currency
from domain.payment.errors import PaymentExistsError
from domain.payment.payment import Payment
from domain.payment.value_objects.amount import Amount
from domain.payment.value_objects.description import Description
from domain.payment.value_objects.idempotency_key import IdempotencyKey
from domain.payment.value_objects.metadata import Metadata
from domain.payment.value_objects.webhook_url import WebhookUrl


@pytest.mark.asyncio
async def test_create_payment_use_case_input_data():
    dto = CreatePaymentDTO(
        amount=Decimal(100),
        currency=Currency.USD,
        key=uuid4(),
        description='Test payment',
        metadata={'foo': 'bar'},
        webhook_url='http://example.com/webhook',
    )

    fake_payment = Payment(
        amount=Amount(dto.amount),
        currency=dto.currency,
        description=Description(dto.description),
        metadata=Metadata(dto.metadata),
        key=IdempotencyKey(dto.key),
        webhook_url=WebhookUrl(dto.webhook_url),
    )

    mock_uow = AsyncMock()
    mock_uow.__aenter__.return_value = mock_uow
    mock_uow.__aexit__.return_value = None
    mock_event_bus = AsyncMock()

    with patch( 'domain.payment.service.PaymentService.create', AsyncMock(return_value=fake_payment)):
        result = await CreatePaymentUseCase(uow=mock_uow, event_bus=mock_event_bus)(dto)

    # fields in return DTO comparation with payment aggregate
    assert result.id == str(fake_payment.id.value)
    assert result.status == fake_payment.status.value
    assert result.created_at == fake_payment.created_at.iso()


@pytest.mark.asyncio
async def test_create_payment_use_case_workflow():
    dto = CreatePaymentDTO(
        amount=Decimal(100),
        currency=Currency.USD,
        key=uuid4(),
        description='Test payment',
        metadata={},
        webhook_url='http://example.com/webhook',
    )

    mock_payments_repo = AsyncMock()
    mock_payments_repo.get_by_key = AsyncMock(return_value=None)
    mock_payments_repo.save = AsyncMock()

    mock_outbox_repo = AsyncMock()

    mock_uow = AsyncMock()
    mock_uow.__aenter__.return_value = mock_uow
    mock_uow.__aexit__.return_value = None
    mock_uow.payments = mock_payments_repo
    mock_uow.outbox = mock_outbox_repo

    mock_event_bus = AsyncMock()

    use_case = CreatePaymentUseCase(uow=mock_uow, event_bus=mock_event_bus)

    await use_case(dto)

    # Assert workflow steps
    mock_payments_repo.get_by_key.assert_awaited_once()
    mock_payments_repo.save.assert_awaited_once()
    mock_uow.commit.assert_awaited_once()
    mock_event_bus.publish_payment_event.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_payment_use_case_duplicate_key():
    dto = CreatePaymentDTO(
        amount=Decimal(100),
        currency=Currency.USD,
        key=uuid4(),
        description='Test duplicate key',
        metadata={},
        webhook_url='http://example.com/webhook',
    )

    # Mock repo returns a payment for the same key
    mock_payments_repo = AsyncMock()
    mock_payments_repo.get_by_key = AsyncMock(
        return_value=Payment(
            amount=Amount(dto.amount),
            currency=dto.currency,
            description=Description(dto.description),
            metadata=Metadata(dto.metadata),
            key=IdempotencyKey(dto.key),
            webhook_url=WebhookUrl(dto.webhook_url),
        )
    )

    mock_uow = AsyncMock()
    mock_uow.payments = mock_payments_repo
    mock_uow.__aenter__.return_value = mock_uow
    mock_uow.__aexit__.return_value = None
    mock_event_bus = AsyncMock()

    use_case = CreatePaymentUseCase(uow=mock_uow, event_bus=mock_event_bus)

    with pytest.raises(PaymentExistsError):
        await use_case(dto)


@pytest.mark.asyncio
async def test_create_payment_use_case_events_content():
    dto = CreatePaymentDTO(
        amount=Decimal('42.00'),
        currency=Currency.EUR,
        key=uuid4(),
        description='Event content test',
        metadata={'meta': 'data'},
        webhook_url='http://example.com/webhook',
    )

    mock_payments_repo = AsyncMock()
    mock_payments_repo.get_by_key = AsyncMock(return_value=None)
    mock_payments_repo.save = AsyncMock()

    mock_uow = AsyncMock()
    mock_uow.payments = mock_payments_repo
    mock_uow.__aenter__.return_value = mock_uow
    mock_uow.__aexit__.return_value = None

    mock_event_bus = AsyncMock()

    use_case = CreatePaymentUseCase(uow=mock_uow, event_bus=mock_event_bus)
    result = await use_case(dto)

    # Check events are properly generated and match DTO payment
    events = mock_event_bus.publish_payment_event.call_args[0][0]
    for event in events:
        from domain.payment.events import PaymentCreatedEvent

        assert isinstance(event, PaymentCreatedEvent)
        assert event.payment_id == UUID(result.id)
