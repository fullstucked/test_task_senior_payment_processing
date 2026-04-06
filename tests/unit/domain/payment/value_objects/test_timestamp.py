from datetime import datetime, timezone

import pytest

from domain.payment.errors import PaymentTypeError
from domain.payment.value_objects.timestamp import Timestamp


def test_timestamp_valid():
    # Valid timestamp (current time)
    timestamp = Timestamp(value=datetime.now(timezone.utc))
    assert isinstance(timestamp.value, datetime)
    assert timestamp.value.tzinfo is not None  # Ensure it's timezone-aware


def test_timestamp_invalid_type():
    # Invalid timestamp type (should be datetime)
    with pytest.raises(PaymentTypeError, match='Timestamp must be datetime'):
        Timestamp(value='2023-01-01T00:00:00Z')  # Passing a string instead of datetime


def test_timestamp_timezone_aware():
    # Ensure that the timestamp is timezone-aware
    timestamp = Timestamp(value=datetime.now(timezone.utc))
    assert timestamp.value.tzinfo is not None  # Should be timezone-aware


def test_timestamp_timezone_naive():
    # Naive datetime should raise an error
    naive_timestamp = datetime.now()  # This is a naive datetime (no timezone)
    with pytest.raises(PaymentTypeError, match='Timestamp must be timezone-aware'):
        Timestamp(value=naive_timestamp)


def test_timestamp_rebuild():
    # Test rebuilding the Timestamp object
    valid_timestamp = datetime.now(timezone.utc)
    timestamp = Timestamp(value=valid_timestamp)
    rebuilt_timestamp = Timestamp.rebuild(value=valid_timestamp)
    assert rebuilt_timestamp == timestamp


def test_timestamp_iso_format():
    # Test the iso method for the Timestamp
    timestamp = Timestamp(value=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
    assert timestamp.iso() == '2023-01-01T12:00:00+00:00'
