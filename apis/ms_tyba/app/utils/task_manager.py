import asyncio
import logging
from app.models.task_status_model import TaskStatusModel

class TaskManager:
    tasks = {}
    def __init__(self, task_id, delay_task=10):
        self.task_id = task_id
        self.delay_task = delay_task

    def create_task(self):
        """Crea una tarea con estado 'pending'"""
        self.tasks[self.task_id] = TaskStatusModel(status="pending", total=0, published=0)

    async def delete_task_after_delay(self):
        """Espera el tiempo especificado y luego elimina la tarea de la memoria"""
        await asyncio.sleep(self.delay_task)
        if self.task_id in self.tasks:
            del self.tasks[self.task_id]
            logging.info(f"🗑️ Tarea {self.task_id} eliminada de la memoria después de {self.delay_task} segundos")

    def update_task_status(self, status, total=0, published=0):
        """Actualiza el estado de la tarea"""
        if self.task_id in self.tasks:
            task = self.tasks[self.task_id]  # Accedemos al objeto
            task.status = status
            task.total = total
            task.published = published
        else:
            logging.warning(f"Tarea {self.task_id} no encontrada para actualizar el estado")

