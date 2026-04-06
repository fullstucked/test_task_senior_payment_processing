from decimal import Decimal
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from domain.payment.enums.currency import Currency
from domain.payment.enums.status import Status
from domain.payment.payment import Payment
from domain.payment.value_objects.amount import Amount
from domain.payment.value_objects.description import Description
from domain.payment.value_objects.idempotency_key import IdempotencyKey
from domain.payment.value_objects.metadata import Metadata
from domain.payment.value_objects.webhook_url import WebhookUrl
from infra.payment.db.sqlite_repo import InMemoryPaymentRepository, engine, payment_table


@pytest.fixture
async def session():
    # Create the async session for the in-memory SQLite DB
    SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(payment_table.metadata.create_all)
    async with SessionLocal() as session:
        yield session


@pytest.mark.asyncio
async def test_in_memory_payment_repository(session):
    repo = InMemoryPaymentRepository(session)

    payment = Payment(
        amount=Amount(Decimal('100')),
        currency=Currency('USD'),
        description=Description('Test payment'),
        metadata=Metadata({'test1': 'test2'}),
        key=IdempotencyKey(UUID('f202f79b-f6a5-4fd1-a842-e8b1f610d748')),
        webhook_url=WebhookUrl('http://webhook.url'),
    )

    # Save the payment using the repository
    await repo.save(payment)

    # Fetch the payment by ID
    fetched_payment = await repo.get_by_id(payment.id)

    # Assert the payment is correctly fetched
    assert fetched_payment is not None
    assert fetched_payment.id == payment.id
    assert fetched_payment.amount == payment.amount
    assert fetched_payment.currency == payment.currency
    assert fetched_payment.description == payment.description
    assert fetched_payment.status == payment.status
    assert fetched_payment.key == payment.key

    fetched_payment = await repo.get_by_key(payment.key)

    # Assert the payment is correctly fetched
    assert fetched_payment is not None
    assert fetched_payment.id == payment.id
    assert fetched_payment.amount == payment.amount
    assert fetched_payment.currency == payment.currency
    assert fetched_payment.description == payment.description
    assert fetched_payment.status == payment.status
    assert fetched_payment.key == payment.key

    # Update the payment status
    payment.mark_as_succeeded()
    await repo.update(payment)

    # Fetch the updated payment
    updated_payment = await repo.get_by_id(payment.id)
    assert updated_payment.status == Status.OK
