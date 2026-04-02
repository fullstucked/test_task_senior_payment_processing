from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from domain.payment.errors import PaymentTypeError
from domain.shared.generics.stringable import Stringable
from domain.shared.valueObject import ValueObject

# Ensure that obj can be represented as str
T = TypeVar('T', bound=Stringable)


@dataclass(frozen=True, slots=True, repr=False)
class Metadata(ValueObject, Generic[T]):
    """
    Metadata represents JSON object which stores additional info for Payment
    """

    value: dict[str, T]

    def __post_init__(self):
        ValueObject.__post_init__(self)

        if not isinstance(self.value, dict):
            raise PaymentTypeError('Metadata must be a dictionary')

        # Ensure serialization ability for each field in dict
        if not all(isinstance(k, str) for k in self.value):
            raise PaymentTypeError('Not each field serializable')

    @classmethod
    def rebuild(cls, value: dict[str, Any]) -> 'Metadata':  # type: ignore[override]
        obj = cls.__new__(cls)
        object.__setattr__(obj, 'value', value)
        return obj
