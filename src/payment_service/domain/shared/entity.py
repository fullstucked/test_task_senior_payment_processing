from domain.shared.event import DomainEvent
from collections.abc import Hashable
from typing import Any, Generic, Hashable, Self, TypeVar, cast  # noqa: F811

# Id
T = TypeVar('T', bound=Hashable)

### Event Generic
E = TypeVar('E', bound=DomainEvent)


class Entity(Generic[T, E]):
    """
    Base class for domain entities, defined by a unique identity (`id`).
    - `id`: Identity that remains constant throughout the entity's lifecycle.
    - Entities are mutable, but are compared solely by their `id`.
    """

    def __new__(cls, *_args: Any, **_kwargs: Any) -> Self:
        if cls is Entity:
            raise TypeError('Base Entity cannot be instantiated directly.')
        return object.__new__(cls)

    def __init__(self, *, id_: T) -> None:
        self.id_ = id_
        self._events: list[E] = []

    def __post_init__(self): ...

    @classmethod
    def rebuild(cls, *, id: T, **attrs: Any) -> Self:
        """
        Rebuild an entity from persistence without running __init__
        or triggering invariant checks.
        """
        obj = cls.__new__(cls)

        # Set ID directly, bypassing immutability guard
        object.__setattr__(obj, 'id_', id)

        # Restore other attributes
        for name, value in attrs.items():
            object.__setattr__(obj, name, value)

        # Recreate empty event list (or load from storage if needed)
        object.__setattr__(obj, '_events', [])

        return obj

    @property
    def id(self) -> T:
        return self.id_

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Prevents modifying the `id` after it's set.
        Other attributes can be changed as usual.
        """
        if name == 'id_' and getattr(self, 'id_', None) is not None:
            raise AttributeError('Changing entity ID is not permitted.')
        object.__setattr__(self, name, value)

    def __eq__(self, other: object) -> bool:
        """
        Two entities are considered equal if they have the same `id`,
        regardless of other attribute values.
        """
        return type(self) is type(other) and cast(Self, other).id_ == self.id_

    def __hash__(self) -> int:
        """
        Generate a hash based on entity type and the immutable `id`.
        This allows entities to be used in hash-based collections and
        reduces the risk of hash collisions between different entity types.
        """
        return hash((type(self), self.id_))

    def __repr__(self) -> str:
        return f'<{type(self).__name__}(id_={self.id_!r})>'

    # ---------------------------------------------------------
    # Domain Events
    # ---------------------------------------------------------

    def record_event(self, event: E) -> None:
        """Record a domain event that occurred inside this entity."""
        self._events.append(event)

    def pull_events(self) -> list[E]:
        """
        Return and clear all recorded events.
        """
        events = self._events.copy()
        self._events.clear()
        return events

    def get_events(self) -> list[E]:
        """
        Return and all recorded events.
        """
        events = self._events.copy()
        return events
