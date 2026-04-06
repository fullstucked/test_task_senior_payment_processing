from sqlalchemy.ext.asyncio import AsyncSession

from application.payment.interfaces.uow import AbstractPaymentUnitOfWork
from infra.payment.db.repository import SqlAlchemyPaymentRepository
from infra.payment.outbox.repository import SqlAlchemyOutboxRepository
from infra.shared.session import async_session_factory


class SqlAlchemyUnitOfWork(AbstractPaymentUnitOfWork):
    def __init__(self):
        self.session: AsyncSession | None = None

    async def __aenter__(self):
        self.session = async_session_factory()
        self.payments = SqlAlchemyPaymentRepository(self.session)
        self.outbox = SqlAlchemyOutboxRepository(self.session)

        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.session is None:
            return
        try:
            if exc:
                await self.rollback()
            # else:
            #     await self.commit() ## I prefere explict commit, but possible to toggle by uncommenting and removing others
        finally:
            await self.session.close()
            self.session = None

    async def commit(self) -> None:
        if not self.session:
            raise RuntimeError('Session not initialized')
        await self.session.commit()

    async def rollback(self) -> None:
        if not self.session:
            raise RuntimeError('Session not initialized')
        await self.session.rollback()
