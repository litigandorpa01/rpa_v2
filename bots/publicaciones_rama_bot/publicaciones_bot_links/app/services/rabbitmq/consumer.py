import json
import asyncio
import logging

import aio_pika

from app.constants import RABBITMQ_HOST,QUEUE_NAME,PREFETCH_COUNT
from app.services.scraper.publicaciones_scraper import PublicacionesScraper


class RabbitMQConsumer:
    """
    Clase asíncrona que encapsula la conexión a RabbitMQ y el procesamiento de mensajes.
    """
    def __init__(self):
        self.host = RABBITMQ_HOST
        self.queue_name = QUEUE_NAME
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
            logging.info(" Conexión a RabbitMQ establecida.")
        except Exception as e:
            logging.info(f"❌ Error conectando a RabbitMQ: {e}")
            raise

    async def callback(self, message: aio_pika.IncomingMessage):
        """
        Función que se ejecuta cuando se recibe un mensaje de RabbitMQ.
        """
        try:
            async with message.process():
                body = message.body.decode()
                data = json.loads(body)
             
                despa_liti = data.get("despa_liti")
                cod_despacho = data.get("cod_despacho")
                ultima_fecha = data.get("ultima_fecha")
                interval_days = data.get("interval_days")

                # Ejecutar el scraper con el process_id recibido
                logging.info(f"Se inicia Scrapper de {despa_liti} - {cod_despacho}")
                scraper = PublicacionesScraper(
                    despa_liti=despa_liti,
                    cod_despacho=cod_despacho,
                    ultima_fecha=ultima_fecha,
                    interval_days=interval_days
                )
                await scraper.run()


        except Exception as e:
            logging.error(f"❌ Error procesando mensaje: {str(e).splitlines()[0]}")
            await message.nack(requeue=False)

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