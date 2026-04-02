from dataclasses import asdict
from datetime import datetime, timezone
from typing import Iterable
from uuid import UUID

from sqlalchemy import select, update

from domain.payment.event_repo import PaymentEventRepository
from domain.payment.events import PaymentDomainEvent, rebuild_event
from infra.shared.enums.status import TaskStatus

from .table import outbox


class SqlAlchemyOutboxRepository(PaymentEventRepository):
    def __init__(self, session):
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
            event_dict: dict[str, object] = asdict(event)
            event_data = {
                'type': event.__class__.__name__,
                'queue': f'{event.__class__.__event_group__()}.{event.__event_key__()}',
                'id': event.id,
                'occured_at': event.occured_at,
                'payload': {
                    k: self._serialize_value(v)
                    for k, v in event_dict.items()
                    if (
                        k.startswith('event_')
                        or k.startswith('__')
                        or k not in ('id', 'type', 'occured_at', 'queue')
                    )
                },
            }

            await self.session.execute(
                outbox.insert().values(
                    id=event_data['id'],
                    type=event_data['type'],
                    queue=event_data['queue'],
                    payload=event_data['payload'],
                    occured_at=event_data['occured_at'],
                )
            )

    async def get_pendings(self, limit: int = 50) -> list[PaymentDomainEvent]:
        """
        Rebuilds PaymentDomain-based events from outbox table
        """
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
            update(outbox)
            .where(outbox.c.id.in_(rows))
            .values(status=TaskStatus.IN_PROCESS, handled_at=datetime.now(timezone.utc))
            .returning(outbox)
        )
        claimed = (await self.session.execute(stmt)).mappings().all()
        return [rebuild_event(row) for row in claimed]

    async def mark_done(self, event_id: UUID) -> None:
        await self.session.execute(
            update(outbox)
            .where(outbox.c.id == event_id)
            .values(status=TaskStatus.OK, handled_at=datetime.now(timezone.utc))
        )

    async def mark_failed(self, event_id: UUID) -> None:
        await self.session.execute(
            update(outbox).where(outbox.c.id == event_id).values(status=TaskStatus.FAIL)
        )
