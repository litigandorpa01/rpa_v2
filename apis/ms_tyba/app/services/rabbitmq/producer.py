import json
import asyncio
import logging
from app.constants import RABBITMQ_HOST, QUEUE_NAME

import aio_pika

class RabbitMQProducer:
    """
    Clase asíncrona que encapsula la conexión a RabbitMQ y la publicación de mensajes.
    """
    def __init__(self):
        self.host = RABBITMQ_HOST
        self.queue_name = QUEUE_NAME
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

            # Declarar la cola como durable para asegurar que los mensajes persistan.
            await self.channel.declare_queue(self.queue_name, durable=True)
            logging.info("✅ Conexión a RabbitMQ establecida.")
        except Exception as e:
            logging.error(f"❌ Error conectando a RabbitMQ: {e}")
            raise

    async def publish(self, process_id: str):
        """
        Publica un mensaje en la cola con el process_id proporcionado.
        """
        if self.channel is None:
            logging.info("🔄 No hay conexión activa, reconectando...")
            await self.connect()

        try:
            message = json.dumps({"process_id": process_id})
            await self.channel.default_exchange.publish(
                aio_pika.Message(body=message.encode(), delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
                routing_key=self.queue_name
            )
            logging.info(f"📤 Mensaje enviado con process_id: {process_id}")
        except Exception as e:
            logging.error(f"❌ Error al publicar mensaje: {e}")

    async def close(self):
        """
        Cierra la conexión con RabbitMQ.
        """
        if self.connection:
            await self.connection.close()
            logging.info("🔌 Conexión a RabbitMQ cerrada.")

# Ejemplo de uso
async def main():
    producer = RabbitMQProducer()
    await producer.connect()
    await producer.publish("123456")  # Reemplazar con el process_id real
    await producer.close()

if __name__ == "__main__":
    asyncio.run(main())
 