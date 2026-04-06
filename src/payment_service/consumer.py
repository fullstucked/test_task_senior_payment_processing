import asyncio

from presentation.ampq.v1.payments.events.fetch_events import handle_bad_events
from bootstrap.consumer.app_factory import run_consumer


async def run_after_delay(delay_seconds, func):
    while True:
        await asyncio.sleep(delay_seconds)
        await func()


async def main():
    await asyncio.gather(run_consumer(), run_after_delay(10, handle_bad_events))


if __name__ == '__main__':
    asyncio.run(main())
