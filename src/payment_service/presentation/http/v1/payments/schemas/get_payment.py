from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from application.payment.use_cases.get_payment_by_id import GetPaymentByIdDTO
from domain.payment.enums.currency import Currency
from domain.payment.enums.status import Status


def to_application_lvl_dto(id):
    return GetPaymentByIdDTO(id=UUID(id))


class PaymentDetailResponse(BaseModel):
    payment_id: UUID = Field(..., alias='id', description='Unique payment ID')
    amount: Decimal = Field(..., description='Payment amount')
    currency: Currency = Field(..., description='Payment currency')
    description: str = Field(..., description='Payment description')
    metadata: dict[str, Any] = Field(default_factory=dict, description='Metadata')
    status: Status = Field(..., description='Payment status')
    key: UUID = Field(..., description='Idempotency key')
    created_at: datetime = Field(..., description='Creation timestamp')
    processed_at: Optional[datetime] = Field(None, description='Processed timestamp if complete')

    # model_config = ConfigDict(from_attributes=True)

    class Config:
        json_encoders = {Decimal: lambda v: str(v)}
