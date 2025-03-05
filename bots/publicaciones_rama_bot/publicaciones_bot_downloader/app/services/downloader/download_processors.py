import logging
from abc import ABC, abstractmethod

import aiohttp
from playwright.async_api import async_playwright

from app.services.downloader.download_scrapper.sharepoint_downloader import Scraper

# Interfaz común para los procesadores de archivos
class FileProcessor(ABC):
    @abstractmethod
    async def download_file(self, file_url:str,file_name:str) -> str:
        pass

# Procesador para archivos pdf
class PdfFilesProcessor(FileProcessor):
    async def download_file(self, file_name:str, file_url:str) -> str:
        return 0
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as response:
                    if response.status == 200:
                        with open(f"{file_name}.pdf", "wb") as archivo:
                            async for chunk in response.content.iter_chunked(8192):
                                archivo.write(chunk)
                        logging.info(f"✅ Archivo descargado correctamente: {file_name}")
                    else:
                        logging.error(f"❌ Error al descargar el archivo. Código de estado: {response.status}")

            return file_url
        
        except Exception as e:
            raise e

# Procesador para varios archivos en un sharePoint
class SharePointFilesProcessor(FileProcessor):
    async def download_file(self, file_name:str, file_url:str) -> str:
        logging.info(file_name)
        logging.info(file_url)
        async with async_playwright() as playwright:
            scraper = Scraper(file_url, file_name)
            await scraper.run_download(playwright)
            
