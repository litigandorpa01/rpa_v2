from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.services.tyba_service import TybaService
# from app.models.tyba_models import ProcessFileResponseModel

router = APIRouter(
    prefix="/tyba"
)

@router.post(
    "/upload/document",
    summary="Recibe un TXT, extrae los IDs, los convierte en JSON y guarda el TXT",
    # response_model=ProcessFileResponseModel
)
async def tyba_upload_route(file: UploadFile = File(...)):
    try:
        await TybaService.process_file(file)
        return 0
    except HTTPException as e:  
        raise e  # Manejo de errores específicos de FastAPI

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )
