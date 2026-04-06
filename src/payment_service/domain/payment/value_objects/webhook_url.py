from dataclasses import dataclass
from urllib.parse import urlparse
from validators import url as url_validate

from domain.payment.errors import PaymentValidationError
from domain.shared.valueObject import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class WebhookUrl(ValueObject):
    """
    Represents URL which should accept notifications about payment changes
    """

    value: str

    def __post_init__(self) -> None:
        ValueObject.__post_init__(self)

        parsed = urlparse(self.value)

        # Protocol ensuring
        if parsed.scheme not in ('http', 'https'):
            raise PaymentValidationError('Webhook URL must be http or https')

        # Local network violation prevention
        if parsed.hostname in ('localhost', '127.0.0.1'):
            raise PaymentValidationError('Webhook URL cannot point to localhost')

        # Complex validation ig host not startswith `-` for ex
        if not url_validate(self.value):
            raise PaymentValidationError('Webhook URL must be valid')

    @classmethod
    def rebuild(cls, value: str) -> 'WebhookUrl':  # type: ignore[override]
        obj = cls.__new__(cls)
        object.__setattr__(obj, 'value', value)
        return obj
