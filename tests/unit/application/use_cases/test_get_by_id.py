from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from application.payment.use_cases.get_payment_by_id import GetPaymentByIdDTO, GetPaymentUseCase
from domain.payment.enums.currency import Currency
from domain.payment.enums.status import Status
from domain.payment.errors import PaymentResourceNotFoundError
from domain.payment.payment import Payment
from domain.payment.value_objects.amount import Amount
from domain.payment.value_objects.description import Description
from domain.payment.value_objects.id import PaymentId
from domain.payment.value_objects.idempotency_key import IdempotencyKey
from domain.payment.value_objects.metadata import Metadata
from domain.payment.value_objects.timestamp import Timestamp
from domain.payment.value_objects.webhook_url import WebhookUrl


@pytest.mark.asyncio
async def test_get_payment_use_case_returns_payment():
    payment_id = uuid4()
    key = uuid4()

    fake_payment = Payment.rebuild(
        id=PaymentId(payment_id),
        amount=Amount.rebuild(100),
        currency=Currency.USD,
        description=Description.rebuild('Test Payment'),
        metadata=Metadata.rebuild({'foo': 'bar'}),
        status=Status.PENDING,
        key=IdempotencyKey.rebuild(key),
        webhook_url=WebhookUrl.rebuild('http://example.com'),
        created_at=Timestamp.now(),
        processed_at=None,
    )

    async def get_by_id_side_effect(payment_id):  # noqa
        return fake_payment

    # Mock repository
    mock_payments_repo = AsyncMock()
    mock_payments_repo.get_by_id = AsyncMock(side_effect=get_by_id_side_effect)

    # Mock UoW
    mock_uow = AsyncMock()
    mock_uow.payments = mock_payments_repo
    mock_uow.__aenter__.return_value = mock_uow
    mock_uow.__aexit__.return_value = None

    # Use case
    use_case = GetPaymentUseCase(uow=mock_uow)
    dto = GetPaymentByIdDTO(id=payment_id)

    result = await use_case(dto)

    # Assert values
    assert result.id == fake_payment.id.value
    assert result.amount == fake_payment.amount.value
    assert result.currency == fake_payment.currency.value
    assert result.description == fake_payment.description.value
    assert result.metadata == {
        key: str(value) for key, value in fake_payment.metadata.value.items()
    }
    assert result.status == fake_payment.status.value
    assert result.key == fake_payment.key.value
    assert result.created_at == fake_payment.created_at.value.isoformat()
    assert result.processed_at is None

    # Ensure repository was called with correct PaymentId
    mock_payments_repo.get_by_id.assert_awaited_once_with(payment_id=PaymentId(payment_id))


@pytest.mark.asyncio
async def test_get_payment_use_case_not_found():

    async def get_by_id_side_effect(payment_id: PaymentId):
        raise PaymentResourceNotFoundError('Not found')

    mock_payments_repo = AsyncMock()
    mock_payments_repo.get_by_id = AsyncMock(side_effect=get_by_id_side_effect)

    mock_uow = AsyncMock()
    mock_uow.payments = mock_payments_repo
    mock_uow.__aenter__.return_value = mock_uow
    mock_uow.__aexit__.return_value = None

    use_case = GetPaymentUseCase(uow=mock_uow)
    dto = GetPaymentByIdDTO(id=uuid4())

    with pytest.raises(PaymentResourceNotFoundError):
        await use_case(dto)

    # Ensure repository was called
    mock_payments_repo.get_by_id.assert_awaited_once()
