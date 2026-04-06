from typing import Optional

from sqlalchemy import RowMapping, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

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
from infra.payment.db.table import payments


class SqlAlchemyPaymentRepository(PaymentRepository):
    """
    PostgreSQL implementation of repo
    to change DB replace insert postgres dialtect  with complimentary one
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, payment: Payment) -> None:
        """
        Saves an payment domain aggregate to db
        """

        stmt = insert(payments).values(
            id=payment.id.value,
            amount=payment.amount.value,
            currency=payment.currency.value,
            description=payment.description.value,
            metadata=payment.metadata.value,
            status=payment.status.value,
            idempotency_key=payment.key.value,
            created_at=payment.created_at.value,
            webhook_url=payment.webhook_url.value,
        )
        await self.session.execute(stmt)

    async def update(self, payment: Payment) -> None:
        """
        Updates payment status and timestamp when processed
        """
        stmt = (
            update(payments)
            .where(payments.c.id == payment.id.value)
            .values(status=payment.status.value, processed_at=payment.processed_at.value)  # type: ignore[via setter]
        )
        await self.session.execute(stmt)

    async def get_by_id(self, payment_id: PaymentId) -> Payment:
        """
        Handles payment by it ID
        """
        stmt = select(payments).where(payments.c.id == payment_id.value).with_for_update()
        result = await self.session.execute(stmt)
        row = result.mappings().first()

        if not row:
            raise PaymentResourceNotFoundError(f'Payment not found: {payment_id.value}')

        return self._to_domain(row)

    async def get_by_key(self, key: IdempotencyKey) -> Optional[Payment]:
        """
        Handeles payment by uinque Idempotency key
        """
        stmt = select(payments).where(payments.c.idempotency_key == key.value).with_for_update()
        result = await self.session.execute(stmt)
        row = result.mappings().first()
        return self._to_domain(row) if row else None

    def _to_domain(self, row: RowMapping) -> Payment:
        """
        Mapper from DB row to Domain aggregate
        """
        return Payment.rebuild(
            id=PaymentId.rebuild(row['id']),
            amount=Amount.rebuild(row['amount']),
            currency=Currency(row['currency']),
            description=Description.rebuild(row['description']),
            metadata=Metadata.rebuild(row['metadata']),
            status=Status(row['status']),
            key=IdempotencyKey.rebuild(row['idempotency_key']),
            webhook_url=WebhookUrl.rebuild(row['webhook_url']),
            created_at=Timestamp.rebuild(row['created_at']),
            processed_at=Timestamp.rebuild(row['processed_at']) if row['processed_at'] else None,
        )
