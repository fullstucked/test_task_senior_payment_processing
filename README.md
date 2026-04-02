# Async Payment Processing Service

<!--toc:start-->
- [Async Payment Processing Service](#async-payment-processing-service)
  - [**Overview**](#overview)
  - [**Tech Stack**](#tech-stack)
  - [**Project Structure**](#project-structure)
  - [**AMQP Architecture**](#amqp-architecture)
  - [**HTTP API Endpoints**](#http-api-endpoints)
    - [**Create Payment**](#create-payment)
    - [**Get Payment**](#get-payment)
  - [Environment Variables](#environment-variables)
  - [Setup & Run:](#setup-run)
    - [via Docker:](#via-docker)
  - [Improvements Roadmap](#improvements-roadmap)
<!--toc:end-->

> Test task for an asynchronous payment processing system with webhook notifications, event-driven architecture, and guaranteed message delivery. By @fullstucked

---

## **Overview**

This service consists from:

- **Domain Layer:** Pure business logic (`payment` aggregates, events, enums, errors).  
- **Application Layer:** Use cases (`CreatePayment`, `ProcessPayment`, `SendNotification`, etc.).  
- **Infrastructure Layer:** Persistence (SQLAlchemy UoW), messaging (RabbitMQ publisher/consumer).  
- **Presentation Layer:** HTTP API (FastAPI) and AMQP (FastStream).  
- **Event-Driven & Async:** RabbitMQ for message delivery with retry queues and DLQ.  
- **Idempotency Support:** Prevent duplicate payments.  

**Next steps**
- add task hanlded timing in outbox and fetch task which processed more than timeout/mark them as pending
- discuss an option to avoid publish from api and just fetch by consumer more frequent
- logger via structlog

---

## **Tech Stack**

- Python 3.11+  
- FastAPI – HTTP API framework  
- FastStream – Async RabbitMQ integration  
- SQLAlchemy – Database ORM + Unit of Work pattern  
- alembic - Migrations
- postgresql - Database
- RabbitMQ – Event broker  
- docker/docker-compose  - Containerization

---

## **Project Structure**
```
./src
└── payment_service
    ├── application
    │   ├── payment
    │   │   ├── dto
    │   │   │   ├── create.py
    │   │   │   └── read.py
    │   │   ├── use_cases
    │   │   │   ├── events
    │   │   │   │   ├── fetch_pendings.py
    │   │   │   │   ├── process_payment.py
    │   │   │   │   └── send_notification.py
    │   │   │   ├── create_payment.py
    │   │   │   └── get_payment_by_id.py
    │   │   ├── errors.py
    │   │   ├── event_bus.py
    │   │   └── uow.py
    │   └── shared
    │       ├── dto.py
    │       ├── errors.py
    │       ├── event_based_use_case.py
    │       ├── event_bus.py
    │       ├── uow.py
    │       └── use_case.py
    ├── bootstrap
    │   ├── api
    │   │   ├── hanlers
    │   │   │   └── exceptions
    │   │   │       └── domain
    │   │   │           └── payment.py
    │   │   ├── app_factory.py
    │   │   └── dependencies.py
    │   └── consumer
    │       └── app_factory.py
    ├── domain
    │   ├── payment
    │   │   ├── enums
    │   │   │   ├── currency.py
    │   │   │   └── status.py
    │   │   ├── value_objects
    │   │   │   ├── amount.py
    │   │   │   ├── description.py
    │   │   │   ├── id.py
    │   │   │   ├── idempotency_key.py
    │   │   │   ├── metadata.py
    │   │   │   ├── timestamp.py
    │   │   │   └── webhook_url.py
    │   │   ├── errors.py
    │   │   ├── event_repo.py
    │   │   ├── events.py
    │   │   ├── payment.py
    │   │   ├── repository.py
    │   │   └── service.py
    │   └── shared
    │       ├── generics
    │       │   └── stringable.py
    │       ├── entity.py
    │       ├── errors.py
    │       ├── event.py
    │       └── valueObject.py
    ├── infra
    │   ├── payment
    │   │   ├── db
    │   │   │   ├── repository.py
    │   │   │   └── table.py
    │   │   ├── outbox
    │   │   │   ├── repository.py
    │   │   │   └── table.py
    │   │   ├── publisher
    │   │   │   └── rabbit_publisher.py
    │   │   └── uow.py
    │   └── shared
    │       ├── enums
    │       │   └── status.py
    │       ├── events
    │       │   ├── queue
    │       │   │   ├── dlq.py
    │       │   │   ├── new_payment.py
    │       │   │   └── payment_notify.py
    │       │   ├── broker.py
    │       │   └── exchanges.py
    │       └── session.py
    ├── presentation
    │   ├── ampq
    │   │   └── v1
    │   │       ├── payments
    │   │       │   ├── events
    │   │       │   │   ├── fetch_events.py
    │   │       │   │   ├── notify_client.py
    │   │       │   │   └── process_payment.py
    │   │       │   ├── schemas
    │   │       │   │   ├── notification.py
    │   │       │   │   └── payment.py
    │   │       │   └── dependencies.py
    │   │       └── shared
    │   │           └── schemas
    │   │               └── base
    │   │                   └── base.py
    │   └── http
    │       └── v1
    │           └── payments
    │               ├── mappers
    │               │   ├── create.py
    │               │   └── read.py
    │               ├── schemas
    │               │   ├── create_payment.py
    │               │   └── get_payment.py
    │               ├── dependencies.py
    │               └── router.py
    ├── consumer.py
    └── main.py
```

- **domain:** Business rules, events, enums, errors.  
- **application:** Use cases and DTOs.  
- **infra:** Database, event publishing, and broker integration.  
- **presentation:** HTTP endpoints, AMQP consumers, schemas, and routers.  
- **setup:** App factory and entry points.  
- **bootstrap:** AMQP queues and exchanges setup, API+Cousumer factories.  

---

## **AMQP Architecture**

- **Exchanges:** `payments_exchange`, `payments_dlx` (dead-letter stores events and redirect to retry after time), dlx (dead letter).  
- **Queues:**
  - `new_payments_queue` → Payment processing  
  - `notify_payments_queue` → Webhook notifications  
  - Retry queues: 5s, 10s, 40s  
  - DLQ: For failed events  

- **Consumers:**  
  - `process_router` → Handles new payments  
  - `notify_router` → Sends webhook notifications  
  - `handle_bad_events` → Fetches unprocessed tasks on failure  

---

## **HTTP API Endpoints**

### **Create Payment**
```
POST /v1/payments
Headers:
Idempotency-Key: <unique_key>
Body:
{
"amount": 123.45,
"currency": "USD",
"description": "Invoice #123",
"metadata": {"order_id": "ABC123"},
"webhook_url": "https://example.com/webhook
"
}
```
**Response:**

```json
{
  "payment_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "PENDING",
  "created_at": "2026-04-02T12:34:56Z"
}
```
### **Get Payment**
```
GET /v1/payments/{payment_id}
```
**Response:**
```
{
  "payment_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "amount": 123.45,
  "currency": "USD",
  "description": "Invoice #123",
  "metadata": {"order_id": "ABC123"},
  "status": "PENDING",
  "key": "idempotency_key",
  "created_at": "2026-04-02T12:34:56Z",
  "processed_at": null
}
```
## Environment Variables


| Variable                | Default / Example                          | Description                                      |
|-------------------------|-------------------------------------------|---------------------------------------------------|
| `API_KEY`               | `supersecretapikey`                                  | HTTP API authentication key                      |
| `DB_USER`               | `payments_user`                            | Database user (alias for POSTGRES_USER)          |
| `DB_PASSWORD`           | `supersecret`                              | Database password (alias for POSTGRES_PASSWORD)  |
| `DB_NAME`               | `payments`                                 | Database name (alias for POSTGRES_DB)            |
| `DB_PORT`               | `5432`                                     | Database port                                    |
| `DB_TYPE`               | `postgresql+asyncpg`                       | SQLAlchemy database driver                       |
| `API_PORT`              | `8000`                                     | HTTP API port                                    |
| `BROKER_PORT`           | `5672`                                     | RabbitMQ port                                    |
| `BROKER_USER`           | `payments_user`                                      | RabbitMQ username                                |
| `BROKER_PASS`           | `supersecret`                                      | RabbitMQ password                                |
| `BROKER_URL`            | `"ampq://payments:supersecret@rabbitmq:5672/"`         | RabbitMQ connection URL                           |


## Setup & Run:
**Clone**
```
git clone  []
cd payments_test_task
```
**Rename .env.example to .env and redact content**

### via Docker:
**Setup**:
```
docker compose \
  --env-file .env \                                                                                                                                                                                              --env-file .env.development.local \
  -f infra/docker/docker-compose.yml \
  build
```

**Run**
```
docker compose \
  --env-file .env \
  -f infra/docker/docker-compose.yml \
  up
```


## Improvements Roadmap

1. **Testing**
   - Unit tests for domain logic, events, and use cases.
   - Integration tests covering DB operations, AMQP message handling, and HTTP API.
   - End-to-End tests simulating full payment workflow, including retries and DLQ.
   - High-load and stress tests for AMQP consumers and database under concurrent load.

3. **Scaling**
   - Scale consumers horizontally to handle higher throughput with multiple worker instances.
   - Consider auto-scaling consumers based on queue length or message backlog.

4. **Caching & Performance**
   - Cache frequently accessed payment data (e.g., status lookups, idempotency keys) in Redis/valkey to reduce DB load.

6. **Observability & Logging**
   - Include contextual metadata in logs (payment ID, event ID, attempt count).
   - Metrics collection for queues, DB latency, and API performance.
   - Distributed tracing for end-to-end payment workflow debugging.

7. **Infrastructure & DevOps**
   - CI/CD pipeline for tests, linting, and builds.
   - Secrets management for API keys and DB credentials.

9. **Future Enhancements**
   - Monitoring dashboards for queue backlogs and processing latencies.
