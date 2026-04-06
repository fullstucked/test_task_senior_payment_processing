from presentation.ampq.v1.payments.dependencies import get_pending_tasks_uc, get_publisher, get_uow


async def handle_bad_events() -> None:
    """Handler for fetching unprocessed tasks in case of broker failiure."""
    ## NOT AN ACTUAL FASTSTREAM ENDPOINT SO VIA DEFAULT FACTORIES
    ### INSTEAD DEPENDENCIES
    uow = get_uow()
    publisher = get_publisher()

    uc = get_pending_tasks_uc(uow=uow, publisher=publisher)

    await uc()
