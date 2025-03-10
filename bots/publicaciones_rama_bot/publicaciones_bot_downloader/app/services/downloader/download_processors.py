import re
import os
import logging
from pathlib import Path
from abc import ABC, abstractmethod

import fitz
import zipfile
import rarfile
import aiohttp
from playwright.async_api import async_playwright

from app.constants import DOCUMENTS_FOLDER,SHARE_POINT_FOLDER
from app.services.downloader.download_scrapper.sharepoint_downloader import Scraper

class FileProcessor(ABC):
    @abstractmethod
    async def download_file(self, file_url: str, file_name: str) -> str:
        pass
    
    @abstractmethod
    async def process_file(self, file_path: str) -> dict:
        pass

class PdfFilesProcessor(FileProcessor):
    async def download_file(self, file_name: str, file_url: str) -> str:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as response:
                    if response.status == 200:
                        file_path = f"{DOCUMENTS_FOLDER}/{file_name}.pdf"
                        with open(file_path, "wb") as archivo:
                            async for chunk in response.content.iter_chunked(8192):
                                archivo.write(chunk)
                        logging.info(f"✅ Archivo descargado correctamente: {file_name}")
                        return file_path
                    else:
                        logging.error(f"❌ Error al descargar el archivo. Código de estado: {response.status}")
        except Exception as e:
            raise e

    async def process_file(self, file_path: str) -> dict:
        try:
            doc = fitz.open(file_path)
            enlaces = []
            email_pattern = re.compile(r"mailto:", re.IGNORECASE)  # Expresión regular para detectar emails
            
            for pagina in doc:
                for enlace in pagina.get_links():
                    if "uri" in enlace and not email_pattern.search(enlace["uri"]):  # Ignorar emails
                        rect = enlace["from"]
                        texto = pagina.get_textbox(rect).strip()
                        enlaces.append({texto: enlace["uri"]})
            
            return {Path(file_path).name: enlaces}
        except Exception as e:
            raise e

class SharePointFilesProcessor(FileProcessor):
    async def download_file(self, file_name:str, file_url:str) -> str:
        try:
            logging.info(file_name)
            logging.info(file_url)
            async with async_playwright() as playwright:
                scraper = Scraper(file_url, file_name)
                file_path= await scraper.run_download(playwright)
                return file_path
        except Exception as e:
            raise e

    async def process_file(self, file_path: str) -> dict:
        extracted_data = {}
        folder_name = Path(file_path).stem
        extract_folder = os.path.join(f"{SHARE_POINT_FOLDER}", folder_name)
        
        os.makedirs(extract_folder, exist_ok=True)
        try:
            if file_path.endswith(".zip"):
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_folder)
            elif file_path.endswith(".rar"):
                with rarfile.RarFile(file_path, 'r') as rar_ref:
                    rar_ref.extractall(extract_folder)
            else:
                raise ValueError("Formato de archivo no soportado")
            
            pdf_processor = PdfFilesProcessor()
            for pdf_file in Path(extract_folder).rglob("*.pdf"):
                pdf_data = await pdf_processor.process_file(str(pdf_file))
                extracted_data.update(pdf_data)
                
            os.remove(file_path)
            return extracted_data
        except Exception as e:
            raise e
