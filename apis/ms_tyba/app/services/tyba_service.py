import re
import json
import aiofiles
import logging
from fastapi import UploadFile, HTTPException, status
# from app.models.tyba_models import ProcessFileResponseModel, InvalidIDsModel

class TybaService:
    @staticmethod
    async def process_file(file: UploadFile):
        try:
            # Leer contenido del archivo
            content = await file.read()
            text_content = content.decode("utf-8")  # Convertir bytes a string

            logging.info(f"Nombre del archivo recibido: {file.filename}")
            logging.info(f"Contenido del archivo: {text_content}")


        except Exception as e:
            logging.error(f"Error al procesar el archivo: {str(e)}")
            raise e