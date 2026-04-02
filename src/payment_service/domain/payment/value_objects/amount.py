from dataclasses import dataclass
from decimal import Decimal

from domain.payment.errors import PaymentTypeError, PaymentValidationError
from domain.shared.valueObject import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class Amount(ValueObject):
    """
    Class represent imutable count of money which should be processed
    via gatway;
    `Decimal` for precise value
    """

    value: Decimal

    def __post_init__(self) -> None:
        ValueObject.__post_init__(self)

        # Ensure value is Decimal
        if not isinstance(self.value, Decimal):
            raise PaymentTypeError('Amount must be a Decimal')

        # Greater than zero
        if self.value <= Decimal('0'):
            raise PaymentValidationError('Amount must be greater than zero')

        # Max 2 decimal places
        exponent = int(self.value.as_tuple().exponent)
        if exponent < -2:
            raise PaymentValidationError('Amount cannot have more than 2 decimal places')

    @classmethod
    def rebuild(cls, value: Decimal) -> 'Amount':  # type: ignore[direct override]
        obj = cls.__new__(cls)
        object.__setattr__(obj, 'value', value)
        return obj
