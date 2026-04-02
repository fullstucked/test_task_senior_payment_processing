class DomainError(Exception):
    """
    Base class for all domain-specific errors.
    """

    def __init__(self, message: str, context: dict | None = None):
        super().__init__(message)
        self.context = context or {}

    def __repr__(self) -> str:
        if not self.context:
            return f"{self.__class__.__name__}('{self.args[0]}')"
        ctx = ', '.join(f'{k}={v!r}' for k, v in self.context.items())
        return f"{self.__class__.__name__}('{self.args[0]}', context={{ {ctx} }})"


class DomainInvariantError(DomainError):
    """Raised when a domain invariant is violated."""

    pass


class DomainValidationError(DomainError):
    """Raised when validation of a value object fails."""

    pass


class DomainTypeError(DomainError):
    """Raised when a value has incorrect type or format."""

    pass


class DomainBusinessRuleError(DomainInvariantError):
    """Raised when a business rule is violated."""

    pass


class DomainResourceNotFoundError(DomainError):
    """Raised when a domain resource is not found."""

    pass
