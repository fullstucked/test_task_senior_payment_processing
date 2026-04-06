import asyncio
from random import random, uniform
from typing import override

from application.payment.interfaces.event_bus import AbstractPaymentEventBus
from application.payment.interfaces.uow import AbstractPaymentUnitOfWork
from application.shared.use_cases.event_driven_use_case import EventDrivenUseCase
from domain.payment.events import PaymentCreatedEvent
from domain.payment.payment import Payment
from domain.payment.service import PaymentService
from domain.payment.value_objects.id import PaymentId


class ProcessPayment(EventDrivenUseCase[PaymentCreatedEvent]):
    def __init__(self, uow: AbstractPaymentUnitOfWork, event_bus: AbstractPaymentEventBus):
        self._uow: AbstractPaymentUnitOfWork = uow
        self._event_bus: AbstractPaymentEventBus = event_bus

    @override
    async def __call__(self, event: PaymentCreatedEvent):
        async with self._uow as uow:
            service = PaymentService(repo=uow.payments)
            payment = await uow.payments.get_by_id(PaymentId(event.payment_id))

            await self._emulate_processing(payment=payment)
            await service.update_processed_payment(payment)

            events = payment.pull_events()
            await uow.outbox.add(events)
            await uow.commit()

        try:
            await self._event_bus.publish_payment_event(events)
        except Exception:
            pass

    async def _emulate_processing(self, payment: Payment) -> None:
        await asyncio.sleep(uniform(2, 5))
        success = random() < 0.9

        if success:
            payment.mark_as_succeeded()
        else:
            payment.mark_as_failed(reason='simulated error')
