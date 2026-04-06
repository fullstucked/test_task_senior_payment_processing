from typing import override

from application.payment.interfaces.event_bus import AbstractPaymentEventBus
from application.payment.interfaces.uow import AbstractPaymentUnitOfWork


class FetchPendingTasks:
    def __init__(self, uow: AbstractPaymentUnitOfWork, event_bus: AbstractPaymentEventBus):
        self._uow: AbstractPaymentUnitOfWork = uow
        self._event_bus: AbstractPaymentEventBus = event_bus

    @override
    async def __call__(self):
        async with self._uow as uow:
            events = await uow.outbox.get_pendings()
            await self._event_bus.publish_payment_event(events)
