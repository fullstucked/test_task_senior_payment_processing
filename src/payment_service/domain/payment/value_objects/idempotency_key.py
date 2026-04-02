from dataclasses import dataclass
from uuid import UUID

from domain.payment.errors import PaymentTypeError
from domain.shared.valueObject import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class IdempotencyKey(ValueObject):
    """
    Payment Idemporency key should prevent duplicates
    """

    value: UUID

    def __post_init__(self) -> None:
        ValueObject.__post_init__(self)

        # Ensure key representation as UUID4
        if self.value.version != 4:
            raise PaymentTypeError('IdempotencyKey must be UUID v4')

    @classmethod
    def rebuild(cls, value: UUID) -> 'IdempotencyKey':  # type: ignore[override]
        obj = cls.__new__(cls)
        object.__setattr__(obj, 'value', value)
        return obj
