from fastapi import APIRouter, HTTPException, BackgroundTasks

from app.utils.task_manager import TaskManager
from app.services.publicaciones_service import PublicacionesService
from app.models.publicaciones_models   import PubStartRequest, PubStartResponse

router = APIRouter(prefix="/publicaciones")

@router.post(
    "/start",
    summary="Recibe batch e intervalo y retorna un task para monitorear el proceso de publicación",
    response_model=PubStartResponse
)
async def publicaciones_start(
    request:PubStartRequest, background_tasks: BackgroundTasks
):
    try:
        # Crear una instancia del servicio
        service = PublicacionesService()
        
        #Consumir servicio de publicacion
        task_id, total_dispatch= await service.start_publication(
            request.batch_size, request.batch_pub_time, request.interval_days, background_tasks
        )
        
        return PubStartResponse(task_id=task_id, total_dispatch=total_dispatch)
    
    except HTTPException as e:  
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado: {str(e)}"
        )

        
@router.get("/so/{task_id}")
async def tyba_check_status(task_id: str):
    """Consulta el estado de una tarea de publicación en RabbitMQ."""
    service = PublicacionesService()
    return await service.get_task_status(task_id)