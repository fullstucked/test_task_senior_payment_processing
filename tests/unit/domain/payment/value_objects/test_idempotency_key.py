from uuid import UUID, uuid4

import pytest

from domain.payment.errors import PaymentTypeError
from domain.payment.value_objects.idempotency_key import IdempotencyKey


def test_idempotency_key_valid():
    # Valid UUID v4 for IdempotencyKey
    idempotency_key = IdempotencyKey(value=uuid4())
    assert isinstance(idempotency_key.value, UUID)
    assert idempotency_key.value.version == 4


def test_idempotency_key_invalid_uuid():
    # Invalid UUID version (e.g., UUID v3 or UUID v5)
    invalid_uuid = UUID('6fa459ea-ee8a-3ca4-894e-db77e160ed9c')  # v3
    with pytest.raises(PaymentTypeError, match='IdempotencyKey must be UUID v4'):
        IdempotencyKey(value=invalid_uuid)


def test_idempotency_key_rebuild():
    # Test rebuilding the IdempotencyKey object
    valid_uuid = uuid4()
    idempotency_key = IdempotencyKey(value=valid_uuid)
    rebuilt_idempotency_key = IdempotencyKey.rebuild(value=valid_uuid)
    assert rebuilt_idempotency_key == idempotency_key
