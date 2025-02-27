import json
import logging
from typing import Dict, Any
from datetime import datetime, timedelta

from app.database.database import OracleDB
from app.services.rabbitmq.producer import RabbitMQProducer
from app.services.scraper.publicaciones_scraper import PublicacionesScraper

class PublicacionesService:
    def __init__(self, body:str):
        self.body = self.parse_body(body)
        self.db = OracleDB()
        self.scraper = self.initialize_scraper()
    
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
    
    async def db_service(self, data:dict):
        await self.db.connect()
        
        #Comprueba si ya hay registro de las urls en la bd y que tengan estado en
        fecha_pub="2025-02-05"
        despa_liti=29530
        url="https://publicacionesprocesales.ramajudicial.gov.co/documents/6098902/81135016/004+2025+00002+ConcedeImpugnacionFijaAviso.pdf/81ddfab7-7fb5-ffc0-b50c-750e947f8489?t=1738791385027"
        result = await self.db.check_url(fecha_pub,despa_liti,url)
        result=bool(result)
        
        # if result:
        #     print("\n📌 Resultados de la consulta:")
        #     for row in result:
        #         print(row)
        # else:
        #     print("⚠️ No se encontraron datos.")
        
        await self.db.close_connection()

    async def execute(self):                
        data=await self.scraper.run()
        print("hola bbs")
        await self.db_service(data)
        
          #Publicar data en bot de descargas
            # producer=RabbitMQProducer()
            # await producer.connect()
            # await producer.publish_message(cleaned_data)
            # await producer.close()
    
