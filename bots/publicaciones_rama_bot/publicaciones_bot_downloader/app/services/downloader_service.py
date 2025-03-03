import json
import logging
from typing import Dict, Any

from app.services.file_manager import FileManager
from app.services.downloader.download_factory import FileProcessorFactory

logging.basicConfig(
    level=logging.INFO,  # Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Formato del log
    datefmt="%Y-%m-%d %H:%M:%S",  # Formato de fecha y hora
)


class DownloaderService:
    def __init__(self, body:str):
        self.body = self.parse_body(body)
        self.factory=FileProcessorFactory()
        self.file_manager=FileManager(
            self.factory
        )
    
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
    
    async def execute(self):
        logging.info("Inicia proceso")
        
        download_data = self.body['download_data']

        for fecha, lista_dicts in download_data.items():
            for diccionario in lista_dicts:
                logging.info(f"Cantidad: {len(lista_dicts)}")
                url_text = f"{fecha} - {list(diccionario.keys())[0]}"
                url=list(diccionario.values())[0]
                #Se descarga el archivo
                await self.file_manager.download_file(url_text,url)
        logging.info("Finaliza proceso")

                
        
        
        
        
        

        

    
