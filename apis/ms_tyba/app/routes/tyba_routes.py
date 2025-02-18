import uuid
from apis.ms_tyba.app.utils.task_manager import TaskManager
from app.models.tyba_models import ProcessFileResponseModel
from app.services.tyba_publish_service import TybaPublishService

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Query

router = APIRouter(prefix="/tyba")

@router.post(
    "/upload/file",
    summary="Recibe un TXT, extrae los IDs, los convierte en JSON y guarda el TXT",
    response_model=ProcessFileResponseModel
)
async def tyba_upload_route(
    file: UploadFile = File(...), batch_size: int = Query(..., gt=0, lt=2000),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    try:
        task_id = str(uuid.uuid4())
        publish_service = TybaPublishService(file, task_id, batch_size)
        
        # Procesar archivo y obtener la respuesta
        response, file_name = await publish_service.process_file()
        
        # Agregar tarea en segundo plano para publicar en RabbitMQ
        background_tasks.add_task(publish_service.publish_rabbitmq, file_name)

        return response 
    
    except HTTPException as e:  
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado: {str(e)}"
        )

        
@router.get("/status/{task_id}")
async def tyba_check_status(task_id: str):
    import logging
    """Consulta el estado de una tarea de publicación en RabbitMQ."""
    task_manager = TaskManager(task_id)  # Crear el gestor de tareas
    logging.info(task_manager.tasks)
    if task_id not in task_manager.tasks:
        raise HTTPException(status_code=404, detail="Task ID not found")
    return task_manager.tasks[task_id]
