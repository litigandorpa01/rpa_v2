import json
import logging
import aio_pika

from app.constants import RABBITMQ_HOST, PUB_QUEUE_NAME

class RabbitMQProducer:
    """
    Clase para enviar mensajes a RabbitMQ de manera asíncrona.
    """

    def __init__(self):
        self.host = RABBITMQ_HOST
        self.queue_name = PUB_QUEUE_NAME
        self.connection = None
        self.channel = None

    async def connect(self):
        """
        Establece la conexión con RabbitMQ.
        """
        try:
            self.connection = await aio_pika.connect_robust(
                host=self.host,
                port=5672
            )
            self.channel = await self.connection.channel()
            
            self.queue = await self.channel.declare_queue(self.queue_name, durable=True)
            logging.info("Conectado a RabbitMQ - Producer")
        except Exception as e:
            logging.error(f"❌ Error conectando al Producer: {e}")
            raise

    async def publish_message(self, message: dict):
        """
        Publica un mensaje en la cola de RabbitMQ.
        """
        try:
            message_body = json.dumps(message).encode()
            logging.info(message_body)

            
            await self.channel.default_exchange.publish(
                aio_pika.Message(body=message_body, delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
                routing_key=self.queue_name,
            )
            logging.info(f"📤 Mensaje enviado a {self.queue_name}: {message}")
        except Exception as e:
            logging.error(f"❌ Error enviando mensaje: {e}")

    async def close(self):
        """
        Cierra la conexión con RabbitMQ.
        """
        if self.connection:
            await self.connection.close()
            logging.info("🔌 Conexión con RabbitMQ cerrada")
