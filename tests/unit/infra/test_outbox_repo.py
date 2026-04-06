import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from domain.payment.events import PaymentDomainEvent
from domain.payment.value_objects.id import PaymentId
from infra.payment.outbox.sqlite_repo import InMemoryOutboxRepository, engine, metadata, outbox
from infra.shared.enums.status import TaskStatus


@pytest.fixture
async def session():
    SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    async with SessionLocal() as session:
        yield session


@pytest.mark.asyncio
async def test_add_event(session: AsyncSession):
    # Create the repository instance
    repo = InMemoryOutboxRepository(session)

    # Create a sample event
    event = PaymentDomainEvent(payment_id=PaymentId())

    # Add the event to the outbox
    await repo.add([event])

    # Check if the event was inserted into the outbox
    stmt = select(outbox).where(outbox.c.id == str(event.id))
    result = await session.execute(stmt)
    row = result.mappings().first()

    assert row is not None
    assert row['type'] == 'PaymentDomainEvent'
    assert row['queue'] == 'payments.*'
    assert row['payload'] is not None


@pytest.mark.asyncio
async def test_get_pending_events(session: AsyncSession):
    repo = InMemoryOutboxRepository(session)

    event1 = PaymentDomainEvent(payment_id=PaymentId())
    event2 = PaymentDomainEvent(payment_id=PaymentId())

    # Add both events to the outbox
    await repo.add([event1, event2])

    # Fetch the pending events
    pending_events = await repo.get_pendings(limit=2)

    assert len(pending_events) == 2
    assert all(isinstance(event, PaymentDomainEvent) for event in pending_events)


@pytest.mark.asyncio
async def test_mark_event_done(session: AsyncSession):
    repo = InMemoryOutboxRepository(session)

    event = PaymentDomainEvent(payment_id=PaymentId())

    # Add the event to the outbox
    await repo.add([event])

    # Mark the event as done
    await repo.mark_done(event.id)

    # Fetch the event from the database
    stmt = select(outbox).where(outbox.c.id == str(event.id))
    result = await session.execute(stmt)
    row = result.mappings().first()

    assert row is not None
    assert row['status'] == TaskStatus.OK


@pytest.mark.asyncio
async def test_mark_event_failed(session: AsyncSession):
    repo = InMemoryOutboxRepository(session)

    event = PaymentDomainEvent(payment_id=PaymentId())

    # Add the event to the outbox
    await repo.add([event])

    # Mark the event as failed
    await repo.mark_failed(event.id)

    # Fetch the event from the database
    stmt = select(outbox).where(outbox.c.id == str(event.id))
    result = await session.execute(stmt)
    row = result.mappings().first()

    assert row is not None
    assert row['status'] == TaskStatus.FAIL
