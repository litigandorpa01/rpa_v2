import logging
from abc import ABC, abstractmethod
from app.services.downloader.download_processors import FileProcessor, PdfFilesProcessor ,SharePointFilesProcessor

import aiohttp

# Interfaz "Factory"
class ProcessorFactory(ABC):
    """Fábrica abstracta para crear procesadores."""
    @abstractmethod
    def create_processor(self, file_extension: str) -> FileProcessor:
        """Crea y devuelve un procesador según el tipo de archivo en el que se desea guardar."""
        pass
    
    @abstractmethod
    async def get_file_type(self, file_url: str) -> FileProcessor:
        """Obtiene el tipo de contenido del archivo en la URL dada."""
        pass

class FileDownloadFactory(ProcessorFactory):
    """Fábrica concreta que implementa la creación de procesadores."""
    def create_processor(self, file_extension: str) -> FileProcessor:
        if "application/pdf" in file_extension:
            logging.info("Procesador para pdf")
            return PdfFilesProcessor()
        elif "text/html" or file_extension:
            logging.info("Procesador para filas en SharePoint")
            return SharePointFilesProcessor()
        else:
            raise ValueError(f"Tipo de archivo no soportado: {file_extension}")

    async def get_file_type(self,file_url: str) -> str:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(file_url, allow_redirects=True) as response:
                    if response.status == 200:
                        return response.headers.get("Content-Type", "desconocido")
                    else:
                        logging.error(f"❌ Error al obtener la cabecera. Código de estado: {response.status}")
        except aiohttp.ClientError as e:
            logging.error(f"❌ Error de conexión al obtener Content-Type: {e}")