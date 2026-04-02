from dataclasses import dataclass, field
from datetime import datetime, timezone

from domain.payment.errors import PaymentTypeError
from domain.shared.valueObject import ValueObject


@dataclass(frozen=True, slots=True)
class Timestamp(ValueObject):
    """
    Represent datetime object, timezone awared
    """

    value: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        ValueObject.__post_init__(self)

        # Type ensure
        if not isinstance(self.value, datetime):
            raise PaymentTypeError('Timestamp must be datetime')

        # Timezone awareness
        if self.value.tzinfo is None:
            raise PaymentTypeError('Timestamp must be timezone-aware')

    @classmethod
    def now(cls) -> 'Timestamp':
        """Return Timestamp obj with current datetime"""
        return cls(datetime.now(timezone.utc))

    def iso(self) -> str:
        """Returns datetime in iso format"""
        return self.value.isoformat()

    @classmethod
    def rebuild(cls, value: datetime) -> 'Timestamp':  # type: ignore[override]
        obj = cls.__new__(cls)
        object.__setattr__(obj, 'value', value)
        return obj
