import pytest

from domain.payment.errors import PaymentTypeError
from domain.payment.value_objects.metadata import Metadata


def test_metadata_valid():
    # Valid metadata (dict of strings to serializable values)
    valid_metadata = {'key1': 'value1', 'key2': 123, 'key3': True}
    metadata = Metadata(value=valid_metadata)
    assert metadata.value == valid_metadata


def test_metadata_invalid_type():
    # Invalid type (value should be a dictionary)
    with pytest.raises(PaymentTypeError, match='Metadata must be a dictionary'):
        Metadata(value='Not a dict')  # Passing a string instead of a dictionary


def test_metadata_invalid_key_type():
    # Invalid key type (keys should be strings)
    with pytest.raises(PaymentTypeError, match='Not each field serializable'):
        Metadata(value={1: 'value'})  # Key is not a string


def test_metadata_rebuild():
    # Test rebuilding the Metadata object
    valid_metadata = {'key1': 'value1', 'key2': 123}
    metadata = Metadata(value=valid_metadata)
    rebuilt_metadata = Metadata.rebuild(value=valid_metadata)
    assert rebuilt_metadata == metadata
