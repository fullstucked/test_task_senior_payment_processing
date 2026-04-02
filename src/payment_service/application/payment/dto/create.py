from __future__ import annotations

from dataclasses import dataclass

from domain.payment.payment import Payment


@dataclass(frozen=True, slots=True)
class PaymentCreateReadDTO:
    id: str
    status: str
    created_at: str

    @staticmethod
    def from_domain(payment: Payment) -> 'PaymentCreateReadDTO':
        return PaymentCreateReadDTO(
            id=str(payment.id.value),
            status=payment.status.value,
            created_at=payment.created_at.iso(),
        )
