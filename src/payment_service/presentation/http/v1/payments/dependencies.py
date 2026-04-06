from fastapi import Depends

from application.payment.use_cases.create_payment import CreatePaymentUseCase
from application.payment.use_cases.get_payment_by_id import GetPaymentUseCase
from infra.payment.publisher.rabbit_publisher import EventPublisherAMQP
from infra.payment.uow import SqlAlchemyUnitOfWork


# -----------------------------
# UoW factory
# -----------------------------
def get_uow():
    return SqlAlchemyUnitOfWork()


def get_publisher():
    return EventPublisherAMQP()


# -----------------------------
# Use cases
# -----------------------------
def get_create_payment_uc(
    uow=Depends(get_uow), publisher=Depends(get_publisher)
) -> CreatePaymentUseCase:
    return CreatePaymentUseCase(uow, publisher)


def get_get_payment_uc(uow=Depends(get_uow)) -> GetPaymentUseCase:
    return GetPaymentUseCase(uow)
