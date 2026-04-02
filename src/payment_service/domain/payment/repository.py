from abc import ABC, abstractmethod

from domain.payment.payment import Payment
from domain.payment.value_objects.id import PaymentId
from domain.payment.value_objects.idempotency_key import IdempotencyKey


class PaymentRepository(ABC):
    """Basic presistance abstraction"""

    @abstractmethod
    async def get_by_id(self, payment_id: PaymentId) -> Payment:
        """
        Fetch Payment record by id
        raises `PaymentResourceNotFoundError` if not exists
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_key(self, key: IdempotencyKey) -> Payment | None:
        """
        Fetch Payment record by IdempotencyKey to avoid payment deduplication
        return `None` if not found
        """
        raise NotImplementedError

    @abstractmethod
    async def save(self, payment: Payment) -> None:
        """
        Saves new Payment record
        """
        raise NotImplementedError

    @abstractmethod
    async def update(self, payment: Payment) -> None:
        """
        Update processed Payment record, writes processed_at mark
        and update status
        """
        raise NotImplementedError
