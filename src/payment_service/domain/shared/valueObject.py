from abc import ABC
from dataclasses import dataclass, fields
from functools import cached_property
from typing import Any, final


@dataclass(frozen=True, slots=True, repr=False)
class ValueObject(ABC):
    """Base class for immutable value objects."""

    def __post_init__(self):
        if type(self) is ValueObject:
            raise TypeError('ValueObject cannot be instantiated directly')

        fs = fields(self)
        if not fs:
            raise TypeError(f'{type(self).__name__} must define at least one field')

        for f in fs:
            value = getattr(self, f.name)
            if self._is_mutable(value):
                raise TypeError(f"Field '{f.name}' in {type(self).__name__} must be immutable")

    @classmethod
    def rebuild(cls, **kwargs):
        """Rebuild a value object from stored data without running invariants."""
        obj = cls.__new__(cls)
        for f in fields(cls):
            object.__setattr__(obj, f.name, kwargs[f.name])
        return obj

    @staticmethod
    def _is_mutable(value: Any) -> bool:
        try:
            setattr(value, '_mut_test', True)
            delattr(value, '_mut_test')
            return True
        except Exception:
            return False

    @cached_property
    @final
    def _value(self):
        f = fields(self)[0]
        return getattr(self, f.name)

    def __repr__(self):
        cls = type(self).__name__
        visible = [(f.name, getattr(self, f.name)) for f in fields(self) if f.repr]

        if not visible:
            return f'{cls}(<hidden>)'

        if len(visible) == 1:
            return f'{cls}({visible[0][1]!r})'

        args = ', '.join(f'{k}={v!r}' for k, v in visible)
        return f'{cls}({args})'
