from sqlalchemy import JSON, TIMESTAMP, Column, Enum, Index, String, Table
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

    # Adding indexes for performance improvements
    Index('ix_outbox_status', 'status'),  # Index on 'status' for quick filtering
    Index('ix_outbox_handled_at', 'handled_at'),  # Index on 'handled_at' for time-based queries
    Index('ix_outbox_status_handled_at', 'status', 'handled_at'),  # Composite index for filtering by status and handled_at
)
