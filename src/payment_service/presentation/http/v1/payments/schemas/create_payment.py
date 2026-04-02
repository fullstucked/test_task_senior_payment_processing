from application.payment.use_cases.create_payment import CreatePaymentDTO
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from domain.payment.enums.currency import Currency


class CreatePaymentRequest(BaseModel):
    amount: Decimal = Field(
        ...,
        gt=Decimal(0),
        description='Amount must be greater than 0',
        json_schema_extra={'example': 123.45},
    )
    currency: Currency = Field(
        ..., description='Payment currency', json_schema_extra={'example': 'USD'}
    )
    description: str = Field(
        ..., description='Payment description', json_schema_extra={'example': 'Invoice 123'}
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description='Additional metadata',
        json_schema_extra={'example': {'order_id': 'ABC123'}},
    )
    webhook_url: HttpUrl = Field(
        ...,
        description='Webhook callback URL',
        json_schema_extra={'example': 'https://example.com/webhook'},
    )

    model_config = ConfigDict(from_attributes=True)

    def _to_application_lvl_dto(self, key) -> CreatePaymentDTO:
        return CreatePaymentDTO(
            amount=self.amount,
            currency=self.currency,
            key=UUID(key),
            description=self.description,
            metadata=self.metadata,
            webhook_url=str(self.webhook_url),
        )


class CreatePaymentResponse(BaseModel):
    payment_id: UUID = Field(
        ...,
        description='Unique payment ID',
        json_schema_extra={'example': 'f47ac10b-58cc-4372-a567-0e02b2c3d479'},
    )
    status: str = Field(..., description='Payment status', json_schema_extra={'example': 'PENDING'})
    created_at: datetime = Field(
        ..., description='Creation timestamp', json_schema_extra={'example': '2026-04-02T12:34:56Z'}
    )

    model_config = ConfigDict(from_attributes=True)
