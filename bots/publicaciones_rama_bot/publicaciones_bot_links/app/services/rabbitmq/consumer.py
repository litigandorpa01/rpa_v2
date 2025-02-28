import asyncio
import logging

import aio_pika

from app.constants import RABBITMQ_HOST,SUB_QUEUE_NAME,PREFETCH_COUNT
from app.services.publicaciones_service import PublicacionesService

class RabbitMQConsumer:
    """
    Clase asíncrona que encapsula la conexión a RabbitMQ y el procesamiento de mensajes.
    """
    def __init__(self):
        self.host = RABBITMQ_HOST
        self.queue_name = SUB_QUEUE_NAME
        self.prefetch_count=PREFETCH_COUNT
        self.connection = None
        self.channel = None
        self.queue = None

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
            
            # Configurar prefetch para limitar la cantidad de mensajes sin confirmar.
            await self.channel.set_qos(prefetch_count=self.prefetch_count)
            
            # Declarar la cola como durable para que sobreviva a reinicios
            self.queue = await self.channel.declare_queue(self.queue_name, durable=True)
            logging.info("Conectado a RabbitMQ - Consumer")
        except Exception as e:
            logging.info(f"❌ Error conectando a RabbitMQ: {e}")
            raise

    async def callback(self, message: aio_pika.IncomingMessage):
        """
        Función que se ejecuta cuando se recibe un mensaje de RabbitMQ.
        """
        try:
            body = message.body.decode()
            service = PublicacionesService(body)
            await service.execute()

            # Si todo salió bien, confirmar el mensaje manualmente
            await message.ack()

        except Exception as e:
            logging.error(f"❌ Error procesando mensaje: {e}")
            try:
                await message.nack(requeue=False)  # NACK solo si no se procesó correctamente
            except aio_pika.exceptions.MessageProcessError:
                logging.warning("⚠️ Intento de NACK en un mensaje ya procesado.")

    async def start_consuming(self):
        """
        Inicia el proceso de consumo de mensajes de forma asíncrona.
        """
        # Si el canal o la cola no están establecidos, se realiza la conexión
        if self.channel is None or self.queue is None:
            logging.info("El canal o la cola no están establecidos. Conectando...")
            await self.connect()

        # Configuramos el consumidor pasándole la función callback
        await self.queue.consume(self.callback)
        logging.info("🎧 Esperando mensajes...")

        # Mantener el proceso en ejecución para seguir consumiendo mensajes
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logging.info("👋 Interrupción manual. Cerrando conexión...")
            await self.connection.close()