import httpx

from application.shared.errors import NonRetryableError, RetryableError


class HttpxWebhookSender:
    async def send(self, url: str, payload: dict, timeout: int = 5) -> None:
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                resp = await client.post(url, json=payload)

                if resp.status_code >= 500:
                    raise RetryableError(f'Server error: {resp.status_code}')

                if resp.status_code >= 400:
                    raise NonRetryableError(f'Client error: {resp.status_code}')

            except httpx.TimeoutException as exc:
                raise RetryableError('Timeout') from exc

            except httpx.RequestError as exc:
                raise RetryableError('Network error') from exc
