import json
import asyncio
import logging
import aio_pika
from app.constants import RABBITMQ_HOST, QUEUE_NAME

class RabbitMQProducer:
    def __init__(self):
        self.host = "localhost"
        self.queue_name = "tyba_queue"
        self.connection = None
        self.channel = None

    async def connect(self):
        """
        Establece la conexión y el canal con RabbitMQ.
        """
        try:
            self.connection = await aio_pika.connect_robust(
                host=self.host,
                port=5672
            )
            self.channel = await self.connection.channel()
                        
            # Declarar la cola como durable para que sobreviva a reinicios
            self.queue = await self.channel.declare_queue(self.queue_name, durable=True)
            logging.info(" Conexión a RabbitMQ establecida.")
        except Exception as e:
            logging.info(f"❌ Error conectando a RabbitMQ: {e}")
            raise

    async def publish_batch(self, messages):
        """Publica uno o más mensajes en la cola de RabbitMQ."""
        if not self.channel:
            await self.connect()

        try:
            if isinstance(messages, list):
                tasks = [
                    self.channel.default_exchange.publish(
                        aio_pika.Message(body=json.dumps(msg).encode(), delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
                        routing_key=self.queue_name
                    )
                    for msg in messages
                ]
                await asyncio.gather(*tasks)
            else:  # Si es un solo mensaje
                await self.channel.default_exchange.publish(
                    aio_pika.Message(body=json.dumps(messages).encode(), delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
                    routing_key=self.queue_name
                )
            logging.info(f"📤 Mensaje enviado: {messages}")
        except Exception as e:
            logging.error(f"❌ Error publicando mensaje: {e}")

    async def close(self):
        """Cierra la conexión con RabbitMQ."""
        if self.connection:
            await self.connection.close()
            logging.info("🔌 Conexión a RabbitMQ cerrada.")
