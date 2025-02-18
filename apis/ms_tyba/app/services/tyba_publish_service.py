import asyncio
from app.utils.task_manager import TaskManager
from app.utils.tyba_file_processor import TybaFileProcessor
from app.services.rabbitmq.rabbitmq_publisher import RabbitMQPublisher
from app.models.tyba_models import ProcessFileResponseModel,InvalidIDsModel

class TybaPublishService:
    def __init__(self, file, task_id, batch_size):
        self.file = file
        self.task_id = task_id
        self.batch_size = batch_size
        self.task_manager = TaskManager(task_id)  # Instanciamos el gestor de tareas
        self.progress_queue = asyncio.Queue()  # Agregar la cola de progreso

    async def process_file(self):
        """Procesa el archivo y devuelve el nombre del archivo procesado y los resultados"""
        file_processor = TybaFileProcessor(self.file)
        file_name, total_ids, invalid_ids_count, invalid_ids = await file_processor.process_file()

        # Creamos la respuesta con el resultado del procesamiento
        response = ProcessFileResponseModel(
            task_id=self.task_id,
            file_name=file_name,
            total_ids=total_ids + invalid_ids_count,
            invalid_ids=InvalidIDsModel(count=invalid_ids_count, ids=invalid_ids)
        )
        return response,file_name

    async def publish_rabbitmq(self, file_name):
        """Publica los datos procesados en RabbitMQ y actualiza estado en vivo"""
        self.task_manager.create_task()
        publisher = RabbitMQPublisher(file_name, self.batch_size, self.progress_queue)

        # Inicia la publicación y el monitoreo en paralelo
        publish_task = asyncio.create_task(publisher.publish())
        monitor_task = asyncio.create_task(self.monitor_progress())
        await publish_task
        await monitor_task

    async def monitor_progress(self):
        """Monitorea la cola de progreso y actualiza el estado de la tarea"""
        while True:
            progress = await self.progress_queue.get()
            if progress is None:
                await self.task_manager.delete_task_after_delay()
                self.progress_queue.task_done()  # Marcar tarea como completada
                del self.progress_queue
                break
            self.task_manager.update_task_status("processing", progress["total"], progress["published"])  

        
