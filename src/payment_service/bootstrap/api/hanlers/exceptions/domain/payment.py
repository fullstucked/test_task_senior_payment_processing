from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from domain.payment.errors import (
    PaymentBusinessRuleError,
    PaymentError,
    PaymentInvariantError,
    PaymentResourceNotFoundError,
)


def register_payment_domain_exception_handlers(app: FastAPI):

    @app.exception_handler(PaymentResourceNotFoundError)
    async def payment_not_found_error(request: Request, exc: PaymentResourceNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={'error': 'Payment not found.'}
        )

    @app.exception_handler(PaymentBusinessRuleError)
    async def business_rule_error_handler(request: Request, exc: PaymentBusinessRuleError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'error': 'Payment cannot be processed.', 'message': str(exc)},
        )

    @app.exception_handler(PaymentInvariantError)
    async def invariant_error_handler(request: Request, exc: PaymentInvariantError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={'error': {'message': str(exc)}}
        )

    @app.exception_handler(PaymentError)
    async def generic_payment_error(request: Request, exc: PaymentError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'error': 'Internal server error. Please try again later.'},
        )
