from presentation.ampq.v1.payments.dependencies import get_publisher
from presentation.ampq.v1.payments.dependencies import get_uow

from presentation.ampq.v1.payments.dependencies import get_pending_tasks_uc


async def handle_bad_events() -> None:
    """Handler for fetching unprocessed tasks in case of broker failiure."""
    uow = get_uow()
    publisher = get_publisher()
    uc = get_pending_tasks_uc(uow=uow, publisher=publisher)

    await uc()
