from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from domain.payment.errors import (
    PaymentBusinessRuleError,
    PaymentError,
    PaymentInvariantError,
    PaymentResourceNotFoundError,
)
from domain.shared.errors import (
    DomainBusinessRuleError,
    DomainInvariantError,
    DomainResourceNotFoundError,
)


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(PaymentResourceNotFoundError)
    async def payment_not_found_error(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'error': {
                    'type': exc.__class__.__name__,
                    'message': str(exc),
                }
            },
        )

    @app.exception_handler(DomainResourceNotFoundError)
    async def generic_not_found_error(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'error': {
                    'type': exc.__class__.__name__,
                    'message': str(exc),
                }
            },
        )

    @app.exception_handler(DomainBusinessRuleError)
    @app.exception_handler(PaymentBusinessRuleError)
    async def business_rule_error_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'error': {'type': exc.__class__.__name__}},
        )

    @app.exception_handler(PaymentInvariantError)
    @app.exception_handler(DomainInvariantError)
    async def generic_business_rule_error_handler(
        request: Request, exc: DomainBusinessRuleError | DomainInvariantError
    ):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'error': {'type': exc.__class__.__name__, 'message': str(exc)}},
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={'detail': 'value error'}
        )

    @app.exception_handler(PaymentError)
    async def genreic_payment_error(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={'Internal server error!'}
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'detail': 'Internal server error'},
        )
