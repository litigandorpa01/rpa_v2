import logging
import hashlib
import asyncio
from pathlib import Path
from urllib.parse import urlparse

from app.services.downloader.download_factory import ProcessorFactory

class FileManager():
    def __init__(self,factory: ProcessorFactory):
        self.factory = factory
    
    def create_output_folder(self, fecha: str, url_hash: str, base_dir: str = "downloads") -> Path:
        folder_name = url_hash[:10]
        output_path = Path(base_dir) / fecha / folder_name
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path
    
    async def url_to_hash(self, url: str) -> str:
        await asyncio.sleep(0)
        hash_obj = hashlib.sha256(url.encode('utf-8'))
        return hash_obj.hexdigest()
    
    async def process_file(self, file_path: str, file_extension, url:str) -> dict:
        try:
            logging.info(file_extension)
            processor = self.factory.create_processor(file_extension)
            file_type = await processor.get_file_type()
            return await processor.process_file(file_path, url, file_type)
        except Exception as e:
            logging.error(f"Error procesando {file_path}: {e}")

    async def download_file(self, fecha:str, file_name: str, file_url: str) -> str:
        try:
            file_url = file_url.strip()  # Elimina espacios en blanco accidentales

            # Verifica si la URL es válida
            parsed_url = urlparse(file_url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError(f"URL inválida: {file_url}")

            # Agrega parámetro de descarga si es SharePoint
            if "my.sharepoint.com" in file_url:
                file_url += "&download=1"

            file_extension = await self.factory.get_file_type(file_url)

            processor = self.factory.create_processor(file_extension)

            # Si el archivo es HTML de SharePoint, quita el parámetro de descarga
            if "text/html" in file_extension and "my.sharepoint.com" in file_url:
                file_url = file_url.replace("&download=1", "")

            #Creacion de folder
            url_hash=await self.url_to_hash(file_url)
            output_dir = self.create_output_folder(fecha, url_hash)
            
            return await processor.download_file(file_name, file_url, output_dir), file_extension
        
        except Exception as e:
            logging.error(f"Error al descargar {file_name} desde {file_url}: {e}")