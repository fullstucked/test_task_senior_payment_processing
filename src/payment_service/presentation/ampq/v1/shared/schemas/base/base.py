from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class EventData(BaseModel, Generic[T]):
    type: str
    id: str
    occured_at: datetime
    payload: T


def event(cls: type[T]) -> type[EventData[T]]:
    """Convert data model to EventSchema class"""
    return EventData[cls]
