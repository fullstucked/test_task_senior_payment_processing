from domain.payment.enums.currency import Currency
from domain.payment.errors import PaymentExistsError
from domain.payment.payment import Payment
from domain.payment.repository import PaymentRepository
from domain.payment.value_objects.amount import Amount
from domain.payment.value_objects.description import Description
from domain.payment.value_objects.idempotency_key import IdempotencyKey
from domain.payment.value_objects.metadata import Metadata
from domain.payment.value_objects.webhook_url import WebhookUrl


class PaymentService:
    """
    Combine presistance with domain rules and events
    """

    def __init__(self, repo: PaymentRepository):
        self._repo: PaymentRepository = repo

    async def create(
        self,
        amount: Amount,
        currency: Currency,
        description: Description,
        metadata: Metadata,
        key: IdempotencyKey,
        webhook_url: WebhookUrl,
    ) -> Payment:
        """
        Pre-check existance by indempotency key - if not found
        new Payment created and saving
        """

        payment_exists = await self._repo.get_by_key(key)

        # or replace with same request same result logic
        if payment_exists:
            raise PaymentExistsError(message='PaymentExists')

        payment = Payment(
            amount=amount,
            currency=currency,
            description=description,
            metadata=metadata,
            key=key,
            webhook_url=webhook_url,
        )
        await self._repo.save(payment)

        return payment

    async def update_processed_payment(self, payment: Payment) -> Payment:
        """
        Wrapper for payment status and process_time updates
        """
        await self._repo.update(payment=payment)
        return payment
