from dataclasses import dataclass
from typing import override
from uuid import UUID

from application.payment.dto.read import PaymentDetailedReadDTO
from application.payment.interfaces.uow import AbstractPaymentUnitOfWork
from application.shared.dto import BaseDTO
from application.shared.use_cases.use_case import UseCaseInterface
from domain.payment.value_objects.id import PaymentId


@dataclass
class GetPaymentByIdDTO(BaseDTO):
    """
    Data transfer object which stores only id
    """

    id: UUID


class GetPaymentUseCase(UseCaseInterface[GetPaymentByIdDTO, PaymentDetailedReadDTO]):
    def __init__(self, uow: AbstractPaymentUnitOfWork):

        self._uow: AbstractPaymentUnitOfWork = uow

    @override
    async def __call__(self, dto: GetPaymentByIdDTO) -> PaymentDetailedReadDTO:
        id = PaymentId(dto.id)

        async with self._uow as uow:
            # In not found case raises `PaymentNotFoundError`
            payment = await uow.payments.get_by_id(payment_id=id)

            return PaymentDetailedReadDTO.from_domain(payment=payment)
