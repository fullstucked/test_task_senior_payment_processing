from dataclasses import dataclass
from decimal import Decimal
from typing import Any, override
from uuid import UUID

from application.payment.dto.create import PaymentCreateReadDTO
from application.payment.event_bus import AbstractPaymentEventBus
from application.payment.uow import AbstractPaymentUnitOfWork
from application.shared.dto import BaseDTO
from application.shared.use_case import UseCaseInterface
from domain.payment.enums.currency import Currency
from domain.payment.service import PaymentService
from domain.payment.value_objects.amount import Amount
from domain.payment.value_objects.description import Description
from domain.payment.value_objects.idempotency_key import IdempotencyKey
from domain.payment.value_objects.metadata import Metadata
from domain.payment.value_objects.webhook_url import WebhookUrl


@dataclass
class CreatePaymentDTO(BaseDTO):
    """
    Data transfer object to convert primitives to an actual value objects
    and build Payment aggregate
    """

    amount: Decimal
    currency: Currency
    key: UUID
    description: str
    metadata: dict[str, Any]
    webhook_url: str


class CreatePaymentUseCase(UseCaseInterface[CreatePaymentDTO, PaymentCreateReadDTO]):
    def __init__(self, uow: AbstractPaymentUnitOfWork, event_bus: AbstractPaymentEventBus):

        self._uow: AbstractPaymentUnitOfWork = uow
        self._event_bus: AbstractPaymentEventBus = event_bus

    @override
    async def __call__(self, dto: CreatePaymentDTO) -> PaymentCreateReadDTO:
        amount = Amount(dto.amount)
        currency = dto.currency
        key = IdempotencyKey(dto.key)
        descr = Description(dto.description)
        metadata = Metadata(dto.metadata)
        webhook = WebhookUrl(dto.webhook_url)

        async with self._uow as uow:
            service = PaymentService(repo=uow.payments)
            payment = await service.create(
                amount=amount,
                key=key,
                currency=currency,
                metadata=metadata,
                webhook_url=webhook,
                description=descr,
            )
            events = payment.pull_events()
            await uow.outbox.add(events)
            await uow.commit()

        await self._event_bus.publish_payment_event(events)

        return PaymentCreateReadDTO.from_domain(payment=payment)
