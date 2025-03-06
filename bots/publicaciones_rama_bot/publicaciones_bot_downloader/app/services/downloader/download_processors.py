import logging
from pathlib import Path
from abc import ABC, abstractmethod

import fitz
import aiohttp
from playwright.async_api import async_playwright

from app.services.downloader.download_scrapper.sharepoint_downloader import Scraper

# Interfaz común para los procesadores de archivos
class FileProcessor(ABC):
    @abstractmethod
    async def download_file(self, file_url:str,file_name:str) -> str:
        pass
    
    @abstractmethod
    async def process_file(self, file_path:str) -> str:
        pass
    
# Procesador para archivos pdf
class PdfFilesProcessor(FileProcessor):
    async def download_file(self, file_name:str, file_url:str) -> str:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as response:
                    if response.status == 200:
                        file_path = Path(f"{file_name}.pdf")
                        with open(file_path, "wb") as archivo:
                            async for chunk in response.content.iter_chunked(8192):
                                archivo.write(chunk)
                        logging.info(f"✅ Archivo descargado correctamente: {file_name}")
                        return str(file_path.resolve())
                    else:
                        logging.error(f"❌ Error al descargar el archivo. Código de estado: {response.status}")
        except Exception as e:
            raise e

    async def process_file(self, file_path: str) -> dict:
        try:
            doc = fitz.open(file_path)
            enlaces = {}

            for pagina in doc:
                for enlace in pagina.get_links():
                    if "uri" in enlace:
                        rect = enlace["from"]  # Posición del enlace
                        texto = pagina.get_textbox(rect).strip()  # Extrae el texto del área del enlace
                        if texto:  # Evita guardar enlaces sin texto
                            enlaces[texto] = enlace["uri"]

            return enlaces
        except Exception as e:
            raise e
        
# Procesador para varios archivos en un sharePoint
class SharePointFilesProcessor(FileProcessor):
    async def download_file(self, file_name:str, file_url:str) -> str:
        try:
            logging.info(file_name)
            logging.info(file_url)
            async with async_playwright() as playwright:
                scraper = Scraper(file_url, file_name)
                file_path= await scraper.run_download(playwright)
                return str(file_path.resolve())
        except Exception as e:
            raise e   
