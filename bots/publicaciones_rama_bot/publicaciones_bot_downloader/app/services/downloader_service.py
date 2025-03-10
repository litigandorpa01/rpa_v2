import json
import logging
from pathlib import Path
from typing import Dict, Any

from app.services.file_manager import FileManager
from app.constants import DOCUMENTS_FOLDER, SHARE_POINT_FOLDER
from app.services.downloader.download_factory import FileDownloadFactory

class DownloaderService:
    def __init__(self, body:str):
        self.body = self.parse_body(body)
        self.factory=FileDownloadFactory()
        self.file_manager=FileManager(
            self.factory
        )
        
    # Función para garantizar la existencia de carpetas
    def create_folders(self,*folders):
        for folder in folders:
            Path(folder).mkdir(parents=True, exist_ok=True)
    
    #Convertir data
    def parse_body(self, body: str) -> Dict[str, Any]:
        """Parsea el body y maneja errores."""
        try:
            data = json.loads(body)
            # data["despa_liti"] = int(data.get("despa_liti"))
            # data["interval_days"] = int(data.get("interval_days"))

            # # Manejar la conversión de fecha con validación
            # try:
            #     data["ultima_fecha"] = datetime.strptime(
            #         data.get("ultima_fecha"), "%d/%m/%Y"
            #     ).date()
            # except ValueError:
            #     logging.error("❌ Formato de fecha inválido en 'ultima_fecha'.")
                
            return data
        except Exception as e:
            logging.error(f"❌ Error procesando el body: {body}. Detalles: {e}")
    
    async def process_external_data(self,data:list):
        internal_data=[]
        
        for fecha, lista_dicts in data.items():
            for diccionario in lista_dicts:
                url_text, url = next(iter(diccionario.items()))
                url_text = url_text.replace('.pdf', '') if '.pdf' in url_text else url_text
                file_path, file_extension=await self.file_manager.download_file(url_text,url)
                processed_data = await self.file_manager.process_file(file_path,file_extension)
                internal_data.append(processed_data)  
        return internal_data
    
    async def process_internal_data(self,internal_data:list):
        filtered_data = [d for d in internal_data if any(d.values())]
        #Se filtran datos con valores en la lista
        for diccionario in filtered_data:
            for nombre_pdf, lista_urls in diccionario.items():  # Extrae nombre y lista de URLs
                print(f"\nNombre del PDF: {nombre_pdf}")
                for url_dict in lista_urls:  # Itera sobre la lista de diccionarios con URLs
                    for url_text, url in url_dict.items():  # Extrae texto y URL
                        file_path, file_extension=await self.file_manager.download_file(url_text,url)
                        
        return filtered_data
    
    async def execute(self):
        logging.info("Inicia proceso")
        logging.info("Se crean folders")
        self.create_folders(DOCUMENTS_FOLDER, SHARE_POINT_FOLDER)
        download_data = self.body['download_data']
        
        internal_data=await self.process_external_data(download_data)
        await self.process_internal_data(internal_data)
                          
        logging.info("Finaliza proceso")

                
        
        
        
        
        

        

    
