from unittest.mock import AsyncMock
import pytest

from application.payment.use_cases.fetch_pendings import FetchPendingTasks


@pytest.mark.asyncio
async def test_fetch_pending_tasks():
    # Prepare fake pending events
    fake_events = ['event1', 'event2']

    # Mock outbox repo
    mock_outbox_repo = AsyncMock()
    mock_outbox_repo.get_pendings = AsyncMock(return_value=fake_events)

    # Mock event bus
    mock_event_bus = AsyncMock()
    mock_event_bus.publish_payment_event = AsyncMock()

    # Mock Unit of Work
    mock_uow = AsyncMock()
    mock_uow.outbox = mock_outbox_repo
    mock_uow.__aenter__.return_value = mock_uow
    mock_uow.__aexit__.return_value = None

    # Create use case
    use_case = FetchPendingTasks(uow=mock_uow, event_bus=mock_event_bus)

    # Run use case
    await use_case()

    # Assertions
    mock_outbox_repo.get_pendings.assert_awaited_once()
    mock_event_bus.publish_payment_event.assert_awaited_once_with(fake_events)


@pytest.mark.asyncio
async def test_fetch_pending_tasks_empty():
    mock_outbox_repo = AsyncMock()
    mock_outbox_repo.get_pendings = AsyncMock(return_value=[])

    mock_event_bus = AsyncMock()
    mock_event_bus.publish_payment_event = AsyncMock()

    mock_uow = AsyncMock()
    mock_uow.outbox = mock_outbox_repo
    mock_uow.__aenter__.return_value = mock_uow
    mock_uow.__aexit__.return_value = None

    use_case = FetchPendingTasks(uow=mock_uow, event_bus=mock_event_bus)

    await use_case()

    mock_outbox_repo.get_pendings.assert_awaited_once()
    mock_event_bus.publish_payment_event.assert_awaited_once_with([])


@pytest.mark.asyncio
async def test_fetch_pending_tasks_raises():
    mock_outbox_repo = AsyncMock()
    mock_outbox_repo.get_pendings = AsyncMock(side_effect=Exception('DB error'))

    mock_event_bus = AsyncMock()
    mock_event_bus.publish_payment_event = AsyncMock()

    mock_uow = AsyncMock()
    mock_uow.outbox = mock_outbox_repo
    mock_uow.__aenter__.return_value = mock_uow
    mock_uow.__aexit__.return_value = None

    use_case = FetchPendingTasks(uow=mock_uow, event_bus=mock_event_bus)

    with pytest.raises(Exception) as exc:
        await use_case()

    assert str(exc.value) == 'DB error'
    mock_outbox_repo.get_pendings.assert_awaited_once()
    mock_event_bus.publish_payment_event.assert_not_awaited()
