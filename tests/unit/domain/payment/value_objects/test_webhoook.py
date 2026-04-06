from urllib.parse import urlparse

import pytest

from domain.payment.errors import PaymentValidationError
from domain.payment.value_objects.webhook_url import WebhookUrl


def test_webhook_url_valid_https():
    # Valid URL with https
    url = WebhookUrl('https://valid.url.com')
    assert url.value == 'https://valid.url.com'
    parsed = urlparse(url.value)
    assert parsed.scheme == 'https'
    assert parsed.netloc == 'valid.url.com'


def test_webhook_url_valid_http():
    # Valid URL with http
    url = WebhookUrl('http://valid.url.com')
    assert url.value == 'http://valid.url.com'
    parsed = urlparse(url.value)
    assert parsed.scheme == 'http'
    assert parsed.netloc == 'valid.url.com'


def test_webhook_url_invalid_protocol():
    # Invalid protocol (ftp instead of http/https)
    with pytest.raises(PaymentValidationError, match='Webhook URL must be http or https'):
        WebhookUrl('ftp://invalid.url.com')


def test_webhook_url_no_host():
    # URL with no host
    with pytest.raises(PaymentValidationError, match='Webhook URL must be valid'):
        WebhookUrl('https://')


def test_webhook_url_localhost():
    # Localhost URL (should not be allowed)
    with pytest.raises(PaymentValidationError, match='Webhook URL cannot point to localhost'):
        WebhookUrl('http://localhost:8080')

    with pytest.raises(PaymentValidationError, match='Webhook URL cannot point to localhost'):
        WebhookUrl('https://127.0.0.1:8080')


def test_webhook_url_invalid_format():
    # Invalid URL format (missing domain or incorrect format)
    with pytest.raises(PaymentValidationError, match='Webhook URL must be valid'):
        WebhookUrl('http://-invalid-url')


def test_webhook_url_rebuild():
    # Test rebuilding the WebhookUrl object
    valid_url = 'https://valid.url.com'
    webhook_url = WebhookUrl(value=valid_url)
    rebuilt_webhook_url = WebhookUrl.rebuild(value=valid_url)
    assert rebuilt_webhook_url == webhook_url
