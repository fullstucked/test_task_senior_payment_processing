from sqlalchemy import JSON, TIMESTAMP, Column, Enum, Numeric, String, Table, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from domain.payment.enums.currency import Currency
from domain.payment.enums.status import Status
from infra.shared.session import metadata

payments = Table(
    'payments',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True),
    Column('amount', Numeric(18, 2), nullable=False),
    Column('currency', Enum(Currency, name='currency_enum'), nullable=False),
    Column('description', String, nullable=False),
    Column('metadata', JSON, nullable=False),
    Column('status', Enum(Status, name='status_enum'), nullable=False),
    Column('idempotency_key', UUID(as_uuid=True), nullable=False),
    Column('created_at', TIMESTAMP(timezone=True), nullable=False),
    Column('processed_at', TIMESTAMP(timezone=True)),
    Column('webhook_url', String, nullable=False),
    UniqueConstraint('idempotency_key', name='uq_payment_idempotency'),
)
