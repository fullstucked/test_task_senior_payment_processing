from sqlalchemy import JSON, TIMESTAMP, Column, Enum, String, Table
from sqlalchemy.dialects.postgresql import UUID

from infra.shared.enums.status import TaskStatus
from infra.shared.session import metadata

outbox = Table(
    'outbox',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, unique=True),
    Column('type', String, nullable=False),
    Column('queue', String, nullable=False),
    Column('payload', JSON, nullable=True),
    Column('occured_at', TIMESTAMP(timezone=True), nullable=False),
    Column( 'status', Enum(TaskStatus, name='task_status_enum'), nullable=False, default=TaskStatus.PENDING),
    Column('handled_at', TIMESTAMP(timezone=True), nullable=True),
)
