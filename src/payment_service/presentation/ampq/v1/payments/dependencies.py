import os

from faststream import Depends
from faststream.rabbit.broker import RabbitBroker

from application.payment.use_cases.events.process_payment import ProcessPayment
from application.payment.use_cases.fetch_pendings import FetchPendingTasks
from application.payment.use_cases.events.send_notification import SendNotificationUseCase
from infra.payment.publisher.rabbit_publisher import EventPublisherAMQP
from infra.payment.uow import SqlAlchemyUnitOfWork
from infra.payment.webhooks.httpx_sender import HttpxWebhookSender


# -----------------------------
# factories
# -----------------------------
def get_uow():
    return SqlAlchemyUnitOfWork()


def get_broker():
    return RabbitBroker(url=os.getenv('BROKER_URL'))


def get_publisher():
    return EventPublisherAMQP()


def get_webhook_sender():
    return HttpxWebhookSender()


# -----------------------------
# Use cases
# -----------------------------
def get_process_payment_uc(
    uow=Depends(get_uow), publisher=Depends(get_publisher)
) -> ProcessPayment:
    return ProcessPayment(uow, event_bus=publisher)


def get_notification_event_uc() -> SendNotificationUseCase:
    return SendNotificationUseCase(webhook_sender=Depends(get_webhook_sender))


def get_pending_tasks_uc(
    uow=Depends(get_uow), publisher=Depends(get_publisher)
) -> FetchPendingTasks:
    return FetchPendingTasks(uow, event_bus=publisher)
