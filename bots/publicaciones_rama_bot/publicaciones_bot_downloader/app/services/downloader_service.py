import os
import json
import shutil
import logging
from typing import Dict, Any

from app.database.database import OracleDB
from app.services.file_manager import FileManager
from app.services.downloader.download_factory import FileDownloadFactory

class DownloaderService:
    def __init__(self, body:str):
        self.body = self.parse_body(body)
        self.factory=FileDownloadFactory()
        self.file_manager=FileManager(
            self.factory
        )
        self.db=OracleDB()
        
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
    
    async def process_external_data(self, download_data:list):
        internal_data=[]
        
        for fecha, lista_dicts in download_data.items():
            for diccionario in lista_dicts:
                url_text, url = next(iter(diccionario.items()))
                url_text = url_text.replace('.pdf', '') if '.pdf' in url_text else url_text

                file_path, file_extension=await self.file_manager.download_file(fecha, url_text, url)
                processed_data = await self.file_manager.process_file(file_path, file_extension, url)

                if isinstance(processed_data, list):
                    for item in processed_data:
                        item["publication_date"] = fecha
                    internal_data.extend(processed_data)
                else:
                    processed_data.update({"publication_date": fecha})
                    internal_data.append(processed_data)

        return internal_data
    
    async def update_download_status(self, despa_liti, data: list) -> list:
        try:
            for item in data[:]:  # recorrer copia segura
                url = item.get('url')
                file_type = item.get('file_type')
                file_name = os.path.basename(item.get("file_path", ""))
                publication_date = item.get('publication_date')
                file_path = item.get('file_path')

                if file_type != 3:
                    status_id = await self.db.update_file_download(despa_liti, url, file_type)
                else:
                    subfile_record_exists = await self.db.subfile_record_exists(despa_liti, url, file_name)
                    if subfile_record_exists:
                        data.remove(item)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        continue  #No actualizar status_id para un item eliminado
                    else:
                        status_id = await self.db.add_subfile_record(despa_liti, url, file_type, file_name, publication_date)

                item.update({"status_id": status_id})
            return data

        except Exception as e:
            logging.error(e)
            raise e
    
    async def send_data_s3(self, filter_data: list):
        for item in filter_data:
            original_path = item.get("file_path")
            status_id = item.get("status_id")
                
            # Obtener directorio y extensión
            directory = os.path.dirname(original_path)
            file_extension = os.path.splitext(original_path)[1]
            
            # Crear nuevo nombre de archivo y nueva ruta
            new_file_name = f"{status_id}{file_extension}"
            new_path = os.path.join(directory, new_file_name)
            
            try:
                # Renombrar el archivo físicamente
                shutil.move(original_path, new_path)
                
                # Actualizar el diccionario con la nueva ruta
                item["file_path"] = new_path
                item["original_file_name"] = os.path.basename(original_path)  # Guardar el nombre original por si acaso

                # logging.info(f"Archivo renombrado: {original_path} -> {new_path}")
            except Exception as e:
                logging.info(f"Error al renombrar {original_path}: {str(e)}")
                continue
        return filter_data
            
    async def process_links_data(self,internal_data:list):
        filtered_data = [d for d in internal_data if any(d.values())]
        print(filtered_data)
        #Se filtran datos con valores en la lista
        for diccionario in filtered_data:
            for nombre_pdf, lista_urls in diccionario.items():  # Extrae nombre y lista de URLs
                print(f"\nNombre del PDF: {nombre_pdf}")
                for url_dict in lista_urls:  # Itera sobre la lista de diccionarios con URLs
                    for url_text, url in url_dict.items():  # Extrae texto y URL
                        file_path, file_extension=await self.file_manager.download_file(url_text,url)
                        
        return filtered_data
    
    async def execute(self):
        try:
            logging.info("Inicia proceso")
            await self.db.connect()
            
            despa_liti=self.body['despa_liti']
            
            download_data = self.body['download_data']
            
            data=await self.process_external_data(download_data)
            
            # filter_data= await self.update_download_status(despa_liti, data)

            # await self.send_data_s3(filter_data)
            
            # await self.process_links_data(filter_data)
                            
            logging.info("Finaliza proceso")
        except Exception as e:
            logging.error(e)

                
        
        
        
        
        

        

    
