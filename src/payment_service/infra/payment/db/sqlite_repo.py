# In-memory implementation with SQLite database
# using in tests only, and shows intent without usnig dialect-related funcs
# like storing UUID as String

from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import JSON, TIMESTAMP, Column, MetaData, Numeric, String, Table
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select

from domain.payment.enums.currency import Currency
from domain.payment.enums.status import Status
from domain.payment.errors import PaymentResourceNotFoundError
from domain.payment.payment import Payment
from domain.payment.repository import PaymentRepository
from domain.payment.value_objects.amount import Amount
from domain.payment.value_objects.description import Description
from domain.payment.value_objects.id import PaymentId
from domain.payment.value_objects.idempotency_key import IdempotencyKey
from domain.payment.value_objects.metadata import Metadata
from domain.payment.value_objects.timestamp import Timestamp
from domain.payment.value_objects.webhook_url import WebhookUrl

metadata = MetaData()

payment_table = Table(
    'payments',
    metadata,
    Column('id', String, primary_key=True),
    Column('amount', Numeric(18, 2), nullable=False),
    Column('currency', String, nullable=False),
    Column('description', String, nullable=False),
    Column('metadata', JSON, nullable=False),
    Column('status', String, nullable=False),
    Column('idempotency_key', String, nullable=False),
    Column('created_at', TIMESTAMP(timezone=True), nullable=False),
    Column('processed_at', TIMESTAMP(timezone=True)),
    Column('webhook_url', String, nullable=False),
)

engine = create_async_engine('sqlite+aiosqlite:///:memory:', echo=True)


class InMemoryPaymentRepository(PaymentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, payment_id: PaymentId) -> Payment:
        stmt = select(payment_table).where(payment_table.c.id == str(payment_id.value))
        result = await self.session.execute(stmt)
        row = result.mappings().first()

        if not row:
            raise PaymentResourceNotFoundError(f'Payment not found: {payment_id.value}')

        return self._to_domain(row)

    async def get_by_key(self, key: IdempotencyKey) -> Optional[Payment]:
        stmt = select(payment_table).where(payment_table.c.idempotency_key == str(key.value))
        result = await self.session.execute(stmt)
        row = result.mappings().first()
        return self._to_domain(row) if row else None

    async def save(self, payment: Payment) -> None:
        stmt = insert(payment_table).values(
            id=str(payment.id.value),
            amount=payment.amount.value,
            currency=payment.currency.value,
            description=payment.description.value,
            metadata=payment.metadata.value,
            status=payment.status.value,
            idempotency_key=str(payment.key.value),
            created_at=payment.created_at.value,
            webhook_url=payment.webhook_url.value,
        )
        await self.session.execute(stmt)

    async def update(self, payment: Payment) -> None:
        stmt = (
            payment_table.update()
            .where(payment_table.c.id == str(payment.id.value))
            .values(status=payment.status.value, processed_at=payment.processed_at.value)  # type: ignore
        )
        await self.session.execute(stmt)
        await self.session.commit()

    def _to_domain(self, row) -> Payment:
        return Payment.rebuild(
            id=PaymentId.rebuild(UUID(row['id'])),
            amount=Amount.rebuild(Decimal(row['amount'])),
            currency=Currency(row['currency']),
            description=Description.rebuild(row['description']),
            metadata=Metadata.rebuild(row['metadata']),
            status=Status(row['status']),
            key=IdempotencyKey.rebuild(UUID(row['idempotency_key'])),
            webhook_url=WebhookUrl.rebuild(row['webhook_url']),
            created_at=Timestamp.rebuild(row['created_at']),
            processed_at=Timestamp.rebuild(row['processed_at']),
        )
