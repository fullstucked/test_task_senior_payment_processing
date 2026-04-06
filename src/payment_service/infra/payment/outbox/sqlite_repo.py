# In-memory implementation with SQLite database
# using in tests only, and shows intent without usnig dialect-related funcs
# like storing UUID as String

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Iterable, List
from uuid import UUID

from sqlalchemy import JSON, TIMESTAMP, Column, MetaData, String, Table
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select

from domain.payment.event_repo import PaymentEventRepository
from domain.payment.events import PaymentDomainEvent, rebuild_event
from infra.shared.enums.status import TaskStatus

metadata = MetaData()

outbox = Table(
    'outbox',
    metadata,
    Column('id', String, primary_key=True, unique=True),
    Column('type', String, nullable=False),
    Column('queue', String, nullable=False),
    Column('payload', JSON, nullable=True),
    Column('occured_at', TIMESTAMP(timezone=True), nullable=False),
    Column('status', String, nullable=False, default=TaskStatus.PENDING),
    Column('handled_at', TIMESTAMP(timezone=True), nullable=True),
)

engine = create_async_engine('sqlite+aiosqlite:///:memory:', echo=True)


class InMemoryOutboxRepository(PaymentEventRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _serialize_value(value: object) -> str | int | float | bool | datetime | None:
        """Serializes value to be JSON-compatible."""
        if isinstance(value, str):
            return value
        if isinstance(value, datetime):
            return str(value)
        if isinstance(value, (int, float, bool)):
            return value
        if value is None:
            return None
        return str(value)

    async def add(self, events: Iterable[PaymentDomainEvent]) -> None:
        for event in events:
            event_dict = asdict(event)
            event_data = {
                'type': event.__class__.__name__,
                'queue': f'{event.__class__.__event_group__()}.{event.__event_key__()}',
                'id': event.id,
                'occured_at': event.occured_at,
                'payload': {
                    k: self._serialize_value(v)
                    for k, v in event_dict.items()
                    if k not in ('id', 'type', 'occured_at', 'queue')
                },
            }

            # Insert the event into the outbox table
            await self.session.execute(
                outbox.insert().values(
                    id=str(event_data['id']),
                    type=event_data['type'],
                    queue=event_data['queue'],
                    payload=event_data['payload'],
                    occured_at=event_data['occured_at'],
                )
            )
        await self.session.commit()

    async def get_pendings(self, limit: int = 50) -> List[PaymentDomainEvent]:
        """Rebuilds PaymentDomain-based events from outbox table."""
        subq = (
            select(outbox.c.id)
            .where(outbox.c.status == TaskStatus.PENDING)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )

        rows = (await self.session.execute(subq)).scalars().all()
        if not rows:
            return []

        stmt = (
            outbox.update()
            .where(outbox.c.id.in_(rows))
            .values(status=TaskStatus.IN_PROCESS, handled_at=datetime.now(timezone.utc))
            .returning(outbox)
        )
        claimed = (await self.session.execute(stmt)).mappings().all()
        return [rebuild_event(row) for row in claimed]

    async def mark_done(self, event_id: UUID) -> None:
        await self.session.execute(
            outbox.update()
            .where(outbox.c.id == str(event_id))
            .values(status=TaskStatus.OK, handled_at=datetime.now(timezone.utc))
        )
        await self.session.commit()

    async def mark_failed(self, event_id: UUID) -> None:
        await self.session.execute(
            outbox.update().where(outbox.c.id == str(event_id)).values(status=TaskStatus.FAIL)
        )
        await self.session.commit()
