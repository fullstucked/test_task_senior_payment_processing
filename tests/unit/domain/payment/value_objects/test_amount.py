from decimal import Decimal

import pytest

from domain.payment.errors import PaymentTypeError, PaymentValidationError
from domain.payment.value_objects.amount import Amount


def test_amount_valid_decimal():
    # Valid amount (positive and with 2 decimal places)
    amount = Amount(Decimal('99.99'))
    assert amount.value == Decimal('99.99')


def test_amount_zero():
    # Amount should be greater than zero
    with pytest.raises(PaymentValidationError, match='Amount must be greater than zero'):
        Amount(Decimal('0'))


def test_amount_negative():
    # Amount cannot be negative
    with pytest.raises(PaymentValidationError, match='Amount must be greater than zero'):
        Amount(Decimal('-1.00'))


def test_amount_invalid_type():
    # Ensure that an invalid type raises the correct error
    with pytest.raises(PaymentTypeError, match='Amount must be a Decimal'):
        Amount('100.00')  # Passing a string instead of Decimal


def test_amount_more_than_two_decimal_places():
    # Ensure that Amount cannot have more than two decimal places
    with pytest.raises(
        PaymentValidationError, match='Amount cannot have more than 2 decimal places'
    ):
        Amount(Decimal('99.999'))  # 3 decimal places


def test_amount_valid_edge_case():
    # Edge case of the smallest valid positive amount (e.g., 0.01)
    amount = Amount(Decimal('0.01'))
    assert amount.value == Decimal('0.01')


def test_amount_rebuild():
    # Test rebuild method, ensuring the object can be recreated without running validations
    amount = Amount(Decimal('45.67'))
    rebuilt_amount = Amount.rebuild(value=Decimal('45.67'))
    assert rebuilt_amount == amount
