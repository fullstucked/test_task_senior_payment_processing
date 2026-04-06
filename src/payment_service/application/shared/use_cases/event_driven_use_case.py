from abc import ABC
from typing import Generic, TypeVar

from domain.shared.event import DomainEvent

Event = TypeVar('Event', bound=DomainEvent)


class EventDrivenUseCase(ABC, Generic[Event]):
    async def __call__(self, event: Event) -> None:
        raise NotImplementedError
