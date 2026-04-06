from uuid import UUID, uuid4

import pytest
from domain.payment.errors import PaymentTypeError
from domain.payment.value_objects.id import PaymentId


def test_payment_id_valid():
    # Valid UUID v4 for PaymentId
    payment_id = PaymentId(value=uuid4())
    assert isinstance(payment_id.value, UUID)
    assert payment_id.value.version == 4


def test_payment_id_invalid_uuid():
    # Invalid UUID version (e.g., UUID v3 or UUID v5)
    invalid_uuid = UUID('6fa459ea-ee8a-3ca4-894e-db77e160ed9c')  # v3
    with pytest.raises(PaymentTypeError, match='PaymentId must be UUID v4'):
        PaymentId(value=invalid_uuid)


def test_payment_id_rebuild():
    # Test rebuilding the PaymentId object
    valid_uuid = uuid4()
    payment_id = PaymentId(value=valid_uuid)
    rebuilt_payment_id = PaymentId.rebuild(value=valid_uuid)
    assert rebuilt_payment_id == payment_id
