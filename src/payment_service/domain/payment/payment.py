from domain.payment.enums.currency import Currency
from domain.payment.enums.status import Status
from domain.payment.errors import PaymentBusinessRuleError
from domain.payment.events import PaymentCreatedEvent, PaymentDomainEvent, PaymentProcessedEvent
from domain.payment.value_objects.amount import Amount
from domain.payment.value_objects.description import Description
from domain.payment.value_objects.id import PaymentId
from domain.payment.value_objects.idempotency_key import IdempotencyKey
from domain.payment.value_objects.metadata import Metadata
from domain.payment.value_objects.timestamp import Timestamp
from domain.payment.value_objects.webhook_url import WebhookUrl
from domain.shared.entity import Entity


class Payment(Entity[PaymentId, PaymentDomainEvent]):
    """
    Payment domain entity responsible for status updates, and event emmisions;
    Under wrapper(base Entity class) stores rebuild methods
    for perfomance improvements in case of rebuilding from ~Source of truth~
    """

    def __init__(
        self,
        amount: Amount,
        currency: Currency,
        description: Description,
        metadata: Metadata,
        key: IdempotencyKey,
        webhook_url: WebhookUrl,
        status: Status = Status.PENDING,
    ):
        id = PaymentId()
        super().__init__(id_=id)

        self.amount = amount
        self.currency = currency
        self.description = description
        self.metadata = metadata
        self.key = key
        self.status = status
        self.webhook_url = webhook_url

        self.created_at = Timestamp.now()
        self.processed_at: Timestamp | None = None

        self.record_event(PaymentCreatedEvent(payment_id=self.id.value))

    def __post_init__(self):
        if self.status != Status.PENDING and self.processed_at is None:
            raise PaymentBusinessRuleError(
                'Cannot presists processed payment without processing mark'
            )

    # ---------------------------------------------------------
    # Behavior
    # ---------------------------------------------------------
    def _ensure_pending(self):
        if self.status != Status.PENDING:
            raise PaymentBusinessRuleError('Already processed')

    def mark_as_succeeded(self) -> None:
        self._ensure_pending()

        self.status = Status.OK
        self.processed_at = Timestamp.now()

        self.record_event(
            PaymentProcessedEvent(
                payment_id=self.id.value,
                status=self.status,
                amount=self.amount.value,
                currency=self.currency,
                webhook_url=self.webhook_url.value,
            )
        )

    def mark_as_failed(self, reason: str) -> None:
        self._ensure_pending()

        self.status = Status.FAIL
        self.processed_at = Timestamp.now()

        self.record_event(
            PaymentProcessedEvent(
                payment_id=self.id.value,
                status=self.status,
                reason=reason,
                amount=self.amount.value,
                currency=self.currency,
                webhook_url=self.webhook_url.value,
            )
        )
