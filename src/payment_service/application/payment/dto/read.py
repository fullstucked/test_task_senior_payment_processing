from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from domain.payment.payment import Payment


@dataclass(frozen=True, slots=True)
class PaymentDetailedReadDTO:
    id: UUID
    amount: Decimal
    currency: str
    description: str
    key: UUID
    metadata: dict[str, str]
    status: str
    created_at: str
    processed_at: str | None

    @staticmethod
    def from_domain(payment: Payment) -> 'PaymentDetailedReadDTO':
        return PaymentDetailedReadDTO(
            id=payment.id.value,
            amount=payment.amount.value,
            currency=payment.currency.value,
            description=payment.description.value,
            metadata={key: str(value) for key, value in payment.metadata.value.items()},
            key=payment.key.value,
            status=payment.status.value,
            created_at=payment.created_at.value.isoformat(),
            processed_at=payment.processed_at.value.isoformat() if payment.processed_at else None,
        )
