from domain.shared.errors import DomainError
from domain.shared.errors import DomainValidationError
from domain.shared.errors import DomainTypeError
from domain.shared.errors import DomainResourceNotFoundError
from domain.shared.errors import DomainBusinessRuleError
from domain.shared.errors import DomainInvariantError


class PaymentError(DomainError): ...


class PaymentInvariantError(PaymentError, DomainInvariantError): ...


class PaymentBusinessRuleError(PaymentError, DomainBusinessRuleError): ...


class PaymentExistsError(PaymentBusinessRuleError): ...


class PaymentResourceNotFoundError(PaymentError, DomainResourceNotFoundError): ...


class PaymentTypeError(PaymentError, DomainTypeError): ...


class PaymentValidationError(PaymentError, DomainValidationError): ...
