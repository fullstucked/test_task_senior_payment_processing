from fastapi import APIRouter, Body, Depends, Header

from application.payment.use_cases.create_payment import CreatePaymentUseCase
from application.payment.use_cases.get_payment_by_id import GetPaymentUseCase
from presentation.http.v1.payments.dependencies import get_create_payment_uc, get_get_payment_uc
from presentation.http.v1.payments.mappers.create import to_response as create_responce_mapper
from presentation.http.v1.payments.mappers.read import to_response as read_responce_mapper
from presentation.http.v1.payments.schemas.create_payment import (
    CreatePaymentRequest,
    CreatePaymentResponse,
)
from presentation.http.v1.payments.schemas.get_payment import (
    PaymentDetailResponse,
    to_application_lvl_dto,
)

router = APIRouter(prefix='/v1/payments', tags=['payments'])


@router.get('/{payment_id}', response_model=PaymentDetailResponse)
async def get_payment(payment_id: str, uc: GetPaymentUseCase = Depends(get_get_payment_uc)):
    """
    Retrieve a payment by its ID.
    """
    payment = await uc(dto=to_application_lvl_dto(payment_id))
    return read_responce_mapper(payment)


@router.post('/', response_model=CreatePaymentResponse)
async def create_payment(
    data: CreatePaymentRequest = Body(
        ...,
        examples=[
            {
                'name': 'default',
                'summary': 'Example payment',
                'description': 'A sample payment request demonstrating all fields',
                'value': {
                    'amount': 123.45,
                    'currency': 'USD',
                    'description': 'Invoice 123',
                    'metadata': {'order_id': 'ABC123'},
                    'webhook_url': 'https://example.com/webhook',
                },
            }
        ],
    ),
    uc: CreatePaymentUseCase = Depends(get_create_payment_uc),
    idempotency_key: str = Header(
        ..., alias='Idempotency-Key', description='Unique idempotency key for this payment request'
    ),
):
    """
    Create a new payment with idempotency support.
    """
    payment = await uc(data._to_application_lvl_dto(key=idempotency_key))
    return create_responce_mapper(payment)
