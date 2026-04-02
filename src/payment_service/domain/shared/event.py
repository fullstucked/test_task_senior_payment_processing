from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass(slots=True, kw_only=True)
class DomainEvent:
    """
    Base domain event class identified by it's ID;
    also stores emmiting timing
    """

    id: UUID = field(default_factory=uuid4)
    occured_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
