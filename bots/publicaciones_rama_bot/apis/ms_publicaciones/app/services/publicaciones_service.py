import uuid
import logging
import asyncio

from fastapi import BackgroundTasks

from app.utils.task_manager import TaskManager
from app.services.rabbitmq.producer import RabbitMQProducer
from app.repositories.publicaciones_repositorie import PublicacionesRepository

class PublicacionesService:
    def __init__(self):
        self.repositorie = PublicacionesRepository()
        self.producer = RabbitMQProducer()

    async def start_publication(
        self, batch_size: int, batch_pub_time: int, interval_days: int, background_tasks: BackgroundTasks
    ):
        """Inicia la publicación en segundo plano y devuelve el task_id y el total de publicaciones."""
        try:
            # Generar un task_id único
            task_id = str(uuid.uuid4())
            
            # Obtener el total de publicaciones
            dispatchs = await self.repositorie.fetch_publicaciones(interval_days)
            total_dispatch = len(dispatchs)
            
            # Crear una instancia de TaskManager para esta tarea
            task_manager = TaskManager(task_id)
            task_manager.create_task(task_id, total_dispatch)  # Pasar task_id y total_dispatch
            
            # Ejecutar la publicación en segundo plano
            background_tasks.add_task(
                self._publish_messages, task_manager, dispatchs, batch_size, batch_pub_time
            )
            
            # Devolver el task_id y el total de publicaciones
            return task_id, total_dispatch
        
        except Exception as e:
            logging.error(f"Error al iniciar la publicación: {str(e)}")
            raise e

    async def _publish_messages(self, task_manager: TaskManager, dispatchs: list, batch_size: int, batch_pub_time: int):
        """Publica los mensajes en lotes y actualiza el estado de la tarea."""
        try:
            # Actualizar el estado de la tarea a "processing"
            task_manager.update_task_status(task_manager.task_id, "processing")
            
            # Conectar al producer de RabbitMQ
            await self.producer.connect()

            # Publicar los mensajes en lotes
            for i in range(0, len(dispatchs), batch_size):
                batch = dispatchs[i:i + batch_size]
                logging.info(f"Publicando lote {i // batch_size + 1} con {len(batch)} mensajes")

                for message in batch:
                    await self.producer.publish_message(message)
                    # Actualizar el número de publicaciones realizadas
                    task_manager.update_task_status(task_manager.task_id, "processing", published=i + len(batch))

                # Esperar el tiempo especificado antes de publicar el siguiente lote
                if i + batch_size < len(dispatchs):
                    logging.info(f"Esperando {batch_pub_time} segundos antes del siguiente lote...")
                    await asyncio.sleep(batch_pub_time)

            # Actualizar el estado de la tarea a "completed"
            task_manager.update_task_status(task_manager.task_id, "completed", published=len(dispatchs))
            
        except Exception as e:
            logging.error(f"Error durante la publicación: {str(e)}")
            # Actualizar el estado de la tarea a "failed"
            task_manager.update_task_status(task_manager.task_id, "failed", published=i + len(batch))
            raise e
        finally:
            # Cerrar la conexión con RabbitMQ
            await self.producer.close()

    async def get_task_status(self, task_id: str):
        """Obtiene el estado de una tarea."""
        task_manager = TaskManager(task_id)  # Crear una instancia para acceder a la tarea
        if task_id not in task_manager.tasks:
            raise "Task ID not found"
        return task_manager.tasks[task_id]