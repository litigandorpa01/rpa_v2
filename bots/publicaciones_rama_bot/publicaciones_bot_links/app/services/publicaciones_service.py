import json
import logging
from typing import Dict, Any
from datetime import datetime

from app.database.database import OracleDB
from app.services.rabbitmq.producer import RabbitMQProducer
from app.services.scraper.publicaciones_scraper import PublicacionesScraper

class PublicacionesService:
    def __init__(self, body:str):
        self.body = self.parse_body(body)
        self.db = OracleDB()
        self.scraper = self.initialize_scraper()
        self.publisher=RabbitMQProducer()
    
    def parse_body(self, body: str) -> Dict[str, Any]:
        """Parsea el body y maneja errores."""
        try:
            data = json.loads(body)
            data["despa_liti"] = int(data.get("despa_liti"))
            data["interval_days"] = int(data.get("interval_days"))

            # Manejar la conversión de fecha con validación
            try:
                data["ultima_fecha"] = datetime.strptime(
                    data.get("ultima_fecha", "01/01/2000"), "%d/%m/%Y"
                ).date()
            except ValueError:
                logging.error("❌ Formato de fecha inválido en 'ultima_fecha'.")
                
            return data
        except Exception as e:
            logging.error(f"❌ Error procesando el body: {body}. Detalles: {e}")
    
    def initialize_scraper(self) -> PublicacionesScraper:
        """Inicializa el scraper con los datos del body."""
        return PublicacionesScraper(
            self.body["despa_liti"],
            self.body.get("cod_despacho"),
            self.body["ultima_fecha"],
            self.body["interval_days"],
        )
    
    async def db_service(self, data: dict):
        try:
            await self.db.connect()

            filter_data = {} 

            for key, value_list in data.items():
                filter_list = []
                for item in value_list:
                    url_text = list(item.keys())[0]
                    publication_date = key
                    despa_liti = self.body["despa_liti"]
                    url = list(item.values())[0]
                    creation_date = datetime.today().strftime('%Y-%m-%d')

                    # Validamos si está en la base de datos
                    result = await self.db.check_url(publication_date, despa_liti, url)
                    
                    if not result:
                        result = await self.db.add_url_record(despa_liti, url, creation_date, url_text, publication_date)
                        print("Se agregó dato")
                        filter_list.append(item)

                if filter_list:
                    filter_data[key] = filter_list

            await self.db.close_connection()

            return filter_data
        except Exception as e:
            print(f"Error en db_service: {e}")

    async def publisher_service(self, pub_data: dict):
        await self.publisher.connect()
       # Convertir datetime.date a string
        body_copy = self.body.copy()
        body_copy.pop('ultima_fecha', None) 
        body_copy.pop('interval_days', None)  
        data = {
            **body_copy,
            "download_data": pub_data
        }

        await self.publisher.publish_message(data)
        await self.publisher.close()

    async def execute(self):     
        try: 
            logging.info(f"Proceso Scrapper")           
            data=await self.scraper.run()

            logging.info(f"Proceso BD")           
            pub_data=await self.db_service(data)
            
            logging.info(f"Publicacion rabbit")
            await self.publisher_service(pub_data)

            logging.info(f"Finaliza bot")
        except Exception as e:
            logging.error(f"Error en el bot: {e}")

        
        
      
    
