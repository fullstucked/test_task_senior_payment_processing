from dataclasses import asdict
from datetime import datetime, timezone
from typing import Iterable
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from domain.payment.event_repo import PaymentEventRepository
from domain.payment.events import PaymentDomainEvent, rebuild_event
from infra.shared.enums.status import TaskStatus
from infra.shared.utils.serialize_values import _serialize_value
from infra.payment.outbox.table import outbox


class SqlAlchemyOutboxRepository(PaymentEventRepository):
    """
    PostgreSQL implementation of outbox repository
    to change DB replace insert postgres dialtect  with complimentary one
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, events: Iterable[PaymentDomainEvent]) -> None:
        """
        Writes domain event to db
        """
        for event in events:
            event_dict: dict[str, object] = asdict(event)
            event_data = {
                'type': event.__class__.__name__,
                'queue': f'{event.__class__.__event_group__()}.{event.__event_key__()}',
                'id': event.id,
                'occured_at': event.occured_at,
                'payload': {
                    k: _serialize_value(v)
                    for k, v in event_dict.items()
                    if (  ### non-payload fields skips
                        k.startswith('event_')
                        or k.startswith('__')
                        or k not in ('id', 'type', 'occured_at', 'queue')
                    )
                },
            }

            stmt = insert(outbox).values(
                id=event_data['id'],
                type=event_data['type'],
                queue=event_data['queue'],
                payload=event_data['payload'],
                occured_at=event_data['occured_at'],
                handled_at=None,
            )
            await self.session.execute(stmt)

    async def mark_done(self, event_id: UUID) -> None:
        """
        Marks task as done
        """
        await self.session.execute(
            update(outbox).where(outbox.c.id == event_id).values(status=TaskStatus.OK)
        )

    async def mark_failed(self, event_id: UUID) -> None:
        """
        Marks task as failed
        """
        await self.session.execute(
            update(outbox).where(outbox.c.id == event_id).values(status=TaskStatus.FAIL)
        )

    async def get_pendings(self, limit: int = 50) -> list[PaymentDomainEvent]:
        """
        Rebuilds unprocessed PaymentDomain-based events from outbox table
        """

        subq = (
            select(outbox.c.id)
            .where(outbox.c.status == TaskStatus.PENDING)
            .limit(limit)
            .with_for_update(
                skip_locked=True
            )  # Lock rows to prevent other processes from picking them up
        )
        rows = (await self.session.execute(subq)).scalars().all()
        if not rows:
            return []

        # Set querried tasks as in_process to avoid processing duplicates
        stmt = (
            update(outbox)
            .where(outbox.c.id.in_(rows))
            .values(status=TaskStatus.IN_PROCESS, handled_at=datetime.now(timezone.utc))
            .returning(outbox)
        )
        claimed = (await self.session.execute(stmt)).mappings().all()
        return [rebuild_event(row) for row in claimed]

    async def mark_in_process(self, event_id: UUID) -> bool:
        """
        Retrieve and lock an event for sensetive communication content like
        external things or client notification
        should prevent duplicated messages in similar cases.

        If event is not `PENDING`, return None.
        """
        now = datetime.now(timezone.utc)

        # Subquery to lock the row if in PENDING state
        subq = (
            select(outbox.c.id)
            .where(outbox.c.id == event_id)
            .where(outbox.c.status == TaskStatus.PENDING)
            .with_for_update(skip_locked=True)
            .limit(1)
        )

        # Try to lock the row and retrieve it
        row = await self.session.execute(subq)
        row = row.scalars().first()

        if not row:
            # Either not found or already processed/locked
            return False

        stmt = (
            update(outbox)
            .where(outbox.c.id == event_id)
            .values(status=TaskStatus.IN_PROCESS, handled_at=now)
        )
        await self.session.execute(stmt)

        return True

