from dataclasses import dataclass, field
from uuid import UUID, uuid4

from domain.payment.errors import PaymentTypeError
from domain.shared.valueObject import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class PaymentId(ValueObject):
    """
    Payment unique Identifier
    """

    value: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        ValueObject.__post_init__(self)

        # Ensure that ID represened as UUID4
        if self.value.version != 4:
            raise PaymentTypeError('PaymentId must be UUID v4')

    @classmethod
    def rebuild(cls, value: UUID) -> 'PaymentId':  # type: ignore[override]
        obj = cls.__new__(cls)
        object.__setattr__(obj, 'value', value)
        return obj
