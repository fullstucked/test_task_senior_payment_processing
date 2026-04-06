import pytest

from domain.payment.errors import PaymentValidationError
from domain.payment.value_objects.description import Description


def test_description_valid():
    # Valid description (within length limits and only allowed characters)
    desc = Description('This is a valid description!')
    assert desc.value == 'This is a valid description!'


def test_description_too_short():
    # Too short (less than 10 characters)
    with pytest.raises(
        PaymentValidationError, match='Description length must be between 10 and 250'
    ):
        Description('Short')


def test_description_too_long():
    # Too long (more than 250 characters)
    long_description = 'x' * 251
    with pytest.raises(
        PaymentValidationError, match='Description length must be between 10 and 250'
    ):
        Description(long_description)


def test_description_invalid_characters():
    # Invalid characters (e.g., special characters that are not allowed)
    with pytest.raises(PaymentValidationError, match='Description contains invalid characters'):
        Description('Invalid @description!')


def test_description_valid_characters():
    # Valid characters (allowed punctuation)
    desc = Description('Valid description with commas, periods, and other valid characters!')
    assert desc.value == 'Valid description with commas, periods, and other valid characters!'


def test_description_empty():
    # Empty string (this should fail the length check)
    with pytest.raises(
        PaymentValidationError, match='Description length must be between 10 and 250'
    ):
        Description('')


def test_description_rebuild():
    # Test the rebuild method, ensuring object can be recreated without validation
    desc = Description('Valid description for rebuild!')
    rebuilt_desc = Description.rebuild(value='Valid description for rebuild!')
    assert rebuilt_desc == desc
