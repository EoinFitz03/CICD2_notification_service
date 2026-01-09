# app/worker.py

import asyncio
import json
import os

import aio_pika

from app.database import SessionLocal
from app.models import NotificationDB  # ensures table exists

RABBIT_URL = os.environ["RABBIT_URL"]  # required
EXCHANGE_NAME = os.getenv("EXCHANGE_NAME", "events_topic")
QUEUE_NAME = os.getenv("QUEUE_NAME", "notification_events_queue")
BINDING_KEY = os.getenv("BINDING_KEY", "workout.*")


def store_notification(routing_key: str, payload_obj: dict) -> None:
    db = SessionLocal()
    try:
        row = NotificationDB(
            routing_key=routing_key,
            payload=json.dumps(payload_obj),
        )
        db.add(row)
        db.commit()
    finally:
        db.close()


async def main():
    connection = await aio_pika.connect_robust(RABBIT_URL)
    channel = await connection.channel()

    exchange = await channel.declare_exchange(
        EXCHANGE_NAME, aio_pika.ExchangeType.TOPIC, durable=True
    )

    queue = await channel.declare_queue(QUEUE_NAME, durable=True)
    await queue.bind(exchange, routing_key=BINDING_KEY)

    print(f"Notification worker listening: exchange={EXCHANGE_NAME}, key={BINDING_KEY}")

    async with queue.iterator() as q:
        async for message in q:
            async with message.process():
                payload = json.loads(message.body.decode("utf-8"))
                await asyncio.to_thread(store_notification, message.routing_key, payload)
                print("Stored:", message.routing_key, payload)


if __name__ == "__main__":
    asyncio.run(main())
