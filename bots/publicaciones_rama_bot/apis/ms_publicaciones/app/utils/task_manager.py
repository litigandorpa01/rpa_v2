import asyncio
import logging
from app.models.task_status_model import TaskStatusModel

class TaskManager:
    tasks = {}  # Diccionario compartido para todas las instancias
    
    def __init__(self, task_id: str = None, delay_task: int = 10):
        """
        Constructor opcional para inicializar el task_id y delay_task.
        Si no se proporciona task_id, se puede usar el TaskManager sin él.
        """
        self.task_id = task_id
        self.delay_task = delay_task

    def create_task(self, task_id: str, total: int):
        """Crea una tarea con estado 'pending'."""
        self.tasks[task_id] = TaskStatusModel(status="pending", total=total, published=0)

    def update_task_status(self, task_id: str, status: str, published: int = 0):
        """Actualiza el estado de la tarea."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = status
            task.published = published
        else:
            logging.warning(f"Tarea {task_id} no encontrada para actualizar el estado")

    async def delete_task_after_delay(self, task_id: str):
        """Elimina la tarea después de un retraso."""
        await asyncio.sleep(self.delay_task)
        if task_id in self.tasks:
            del self.tasks[task_id]
            logging.info(f"🗑️ Tarea {task_id} eliminada de la memoria después de {self.delay_task} segundos")