from domain.shared.errors import (
    DomainBusinessRuleError,
    DomainError,
    DomainInvariantError,
    DomainResourceNotFoundError,
    DomainTypeError,
    DomainValidationError,
)


class PaymentError(DomainError): ...


class PaymentInvariantError(PaymentError, DomainInvariantError): ...


class PaymentBusinessRuleError(PaymentError, DomainBusinessRuleError): ...


class PaymentExistsError(PaymentBusinessRuleError): ...


class PaymentResourceNotFoundError(PaymentError, DomainResourceNotFoundError): ...


class PaymentTypeError(PaymentError, DomainTypeError): ...


class PaymentValidationError(PaymentError, DomainValidationError): ...
