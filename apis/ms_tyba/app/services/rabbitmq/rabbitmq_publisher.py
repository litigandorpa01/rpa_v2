import json
import asyncio
import logging
from app.services.rabbitmq.producer import RabbitMQProducer

import aiofiles

class RabbitMQPublisher:
    def __init__(self, file_name, batch_size,progress_queue):
        self.file_name = file_name
        self.batch_size = batch_size
        self.delay_publish = 10
        self.progress_queue = progress_queue  # Cola de progreso

    async def publish(self):
        """Lee el archivo JSON procesado y publica los IDs en RabbitMQ"""
        producer = RabbitMQProducer()
        await producer.connect()
        
        try:
            async with aiofiles.open(self.file_name, "r") as f:
                content = await f.read()
                processed_data = json.loads(content)

            total_ids = len(processed_data)
            
            for i in range(0, total_ids, self.batch_size):
                batch = processed_data[i:i + self.batch_size]
                await producer.publish_batch(batch)
                
                progress = {"published": i + len(batch), "total": total_ids}
                await self.progress_queue.put(progress)  # Enviar progreso

                logging.info(f"📤 Publicados {progress['published']} / {progress['total']} IDs")
                await asyncio.sleep(self.delay_publish)

            logging.info(f"✅ Publicación finalizada")

        except Exception as e:
            logging.error(f"❌ Error en publicación: {e}")

        finally:
            await self.progress_queue.put(None)  # Enviar None para indicar fin
            await asyncio.sleep(0)  # Asegura que la cola reciba el None antes de continuar
            await producer.close()
            
