from domain.payment.enums.status import Status
import asyncio
from random import random, uniform
from typing import override

from application.payment.event_bus import AbstractPaymentEventBus
from application.payment.uow import AbstractPaymentUnitOfWork
from application.shared.event_based_use_case import EventDrivenUseCase
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

            if payment.status == Status.PENDING:
                await self._emulate_processing(payment=payment)

            await service.update_processed_payment(payment)

            if payment.status == Status.OK:
                await self._uow.outbox.mark_done(event.id)
            elif payment.status == Status.FAIL:
                await self._uow.outbox.mark_failed(event.id)

            events = payment.pull_events()
            await self._event_bus.publish_payment_event(events)
            
            await uow.outbox.add(events)
            await uow.commit()

            await self._event_bus.publish_payment_event(events)

    async def _emulate_processing(self, payment: Payment) -> None:
        await asyncio.sleep(uniform(2, 5))
        success = random() < 0.9

        if success:
            payment.mark_as_succeeded()
        else:
            payment.mark_as_failed(reason='simulated error')
