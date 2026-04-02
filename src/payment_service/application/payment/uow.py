from application.shared.uow import AbstractUnitOfWork
from domain.payment.event_repo import PaymentEventRepository
from domain.payment.repository import PaymentRepository


class AbstractPaymentUnitOfWork(AbstractUnitOfWork):
    """
    Base interface for payment-related uow repos
    """

    payments: PaymentRepository
    outbox: PaymentEventRepository
