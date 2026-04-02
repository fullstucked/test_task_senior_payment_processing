from uuid import UUID

from application.payment.dto.create import PaymentCreateReadDTO
from application.payment.use_cases.create_payment import CreatePaymentDTO
from presentation.http.v1.payments.schemas.create_payment import (
    CreatePaymentRequest,
    CreatePaymentResponse,
)


def to_dto(req: CreatePaymentRequest, key: str) -> CreatePaymentDTO:
    return CreatePaymentDTO(
        amount=req.amount,
        currency=req.currency,
        description=req.description,
        metadata=req.metadata,
        key=UUID(key),
        webhook_url=str(req.webhook_url),
    )


def to_response(payment: PaymentCreateReadDTO) -> CreatePaymentResponse:
    return CreatePaymentResponse(
        payment_id=payment.id, status=payment.status, created_at=payment.created_at
    )
