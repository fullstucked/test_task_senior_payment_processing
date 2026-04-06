from fastapi import FastAPI

from bootstrap.api.hanlers.exceptions.domain.payment import register_payment_domain_exception_handlers
from bootstrap.api.hanlers.exceptions.domain.shared import register_shared_domain_exception_handlers
from bootstrap.api.hanlers.exceptions.shared.runtime import register_runtime_exception_handlers


def register_exceptions(app: FastAPI):
    register_payment_domain_exception_handlers(app)
    register_shared_domain_exception_handlers(app)
    register_runtime_exception_handlers(app)
