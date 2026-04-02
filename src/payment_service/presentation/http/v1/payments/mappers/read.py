from application.payment.dto.read import PaymentDetailedReadDTO
from presentation.http.v1.payments.schemas.get_payment import PaymentDetailResponse


def to_response(payment: PaymentDetailedReadDTO) -> PaymentDetailResponse:
    return PaymentDetailResponse(
        id=payment.id,
        key=payment.key,
        currency=payment.currency,
        amount=payment.amount,
        description=payment.description,
        created_at=payment.created_at,
        metadata=payment.metadata,
        status=payment.status,
        processed_at=payment.processed_at if payment.processed_at else None,
    )
