import re
from dataclasses import dataclass

from domain.payment.errors import PaymentValidationError
from domain.shared.valueObject import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class Description(ValueObject):
    """
    Payment Description
    """

    value: str

    def __post_init__(self) -> None:
        ValueObject.__post_init__(self)

        MIN_LEN = 10
        MAX_LEN = 250

        # Lenth limits
        if not (MIN_LEN <= len(self.value) <= MAX_LEN):
            raise PaymentValidationError(
                f'Description length must be between {MIN_LEN} and {MAX_LEN}'
            )

        # Characters validation
        if not re.fullmatch(r'^[\w\s.,\-!?()]+$', self.value):
            raise PaymentValidationError('Description contains invalid characters')

    @classmethod
    def rebuild(cls, value: str) -> 'Description':  # type: ignore[override]
        obj = cls.__new__(cls)
        object.__setattr__(obj, 'value', value)
        return obj
