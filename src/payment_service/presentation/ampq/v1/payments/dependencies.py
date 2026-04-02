import os

from faststream import Depends
from faststream.rabbit.broker import RabbitBroker

from application.payment.use_cases.events.fetch_pendings import FetchPendingTasks
from application.payment.use_cases.events.process_payment import ProcessPayment
from application.payment.use_cases.events.send_notification import SendNotificationUseCase
from infra.payment.publisher.rabbit_publisher import EventPublisherAMQP
from infra.payment.uow import SqlAlchemyUnitOfWork


# -----------------------------
# UoW factory
# -----------------------------
def get_uow():
    return SqlAlchemyUnitOfWork()


def get_broker():
    return RabbitBroker(url=os.getenv('BROKER_URL'))


def get_publisher():
    return EventPublisherAMQP()


# -----------------------------
# Use cases
# -----------------------------
def get_process_payment_uc(
    uow=Depends(get_uow), publisher=Depends(get_publisher)
) -> ProcessPayment:
    return ProcessPayment(uow, event_bus=publisher)


def get_notification_event_uc(uow=Depends(get_uow)) -> SendNotificationUseCase:
    return SendNotificationUseCase(uow)


def get_pending_tasks_uc(
    uow=Depends(get_uow), publisher=Depends(get_publisher)
) -> FetchPendingTasks:
    return FetchPendingTasks(uow, event_bus=publisher)
