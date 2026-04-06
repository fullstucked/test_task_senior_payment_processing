from abc import ABC, abstractmethod


class WebhookSender(ABC):
    """
    some descr
    """

    @abstractmethod
    async def send(self, url: str, payload: dict, timeout: int = 5) -> None:
        """
        descr 2
        """
        raise NotImplementedError
