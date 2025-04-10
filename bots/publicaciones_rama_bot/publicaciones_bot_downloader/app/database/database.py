import asyncio
import logging
from datetime import datetime

import oracledb

from app.constants import DB_USERNAME,DB_PASSWORD,DB_HOST,DB_PORT,DB_SERVICE_NAME

class OracleDB:
    def __init__(self):
        self.dsn = f"{DB_HOST}:{DB_PORT}/{DB_SERVICE_NAME}"
        self.username = DB_USERNAME
        self.password = DB_PASSWORD
        self.connection = None

    async def connect(self):
        try:
            self.connection = await asyncio.to_thread(
                oracledb.connect,
                user=self.username,
                password=self.password,
                dsn=self.dsn
            )
            logging.info("✅ Conexión exitosa a la base de datos LITI.")
        except oracledb.DatabaseError as e:
            logging.error(f"❌ Error al conectar a la base de datos: {e}")
            raise e

    async def update_file_download(self, despa_liti: int, url: str, file_type:int):
        try:
            cursor = await asyncio.to_thread(self.connection.cursor)

            current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            query = """
                UPDATE liti.CONTROL_ESTADOS_RAMA_TEST
                SET ESTADO_DESCARGA = 'SI',
                    FECHA_CREACION_ARCHIVO = TO_TIMESTAMP(:current_timestamp, 'YYYY-MM-DD HH24:MI:SS'),
                    DOC_TYPE = :file_type
                WHERE URL_ESTADO = :url 
                AND DESPACHO_ID = :despa_liti
                RETURNING ESTADO_ID INTO :estado_id
            """

            estado_id = cursor.var(oracledb.NUMBER)

            params = {
                "current_timestamp": current_timestamp,
                "url": url,
                "despa_liti": despa_liti,
                "estado_id": estado_id,
                "file_type":file_type
            }

            await asyncio.to_thread(cursor.execute, query, params)
            self.connection.commit()

            # Obtener el valor y asegurarse de que sea un entero
            estado_id_value = estado_id.getvalue()
            result_id = int(estado_id_value[0]) if estado_id_value else None
            
            cursor.close()

            if result_id is None:
                raise ValueError("No se encontró el registro para actualizar")
            
            return result_id

        except oracledb.DatabaseError as e:
            logging.error(f"❌ Error al ejecutar la consulta: {e}")
            raise e
    
    async def subfile_record_exists(self, despa_liti: int, url: str, file_name: str) -> bool:
        try:
            cursor = await asyncio.to_thread(self.connection.cursor)

            query = """
                SELECT 1 FROM liti.CONTROL_ESTADOS_RAMA_TEST
                WHERE DESPACHO_ID = :despa_liti
                AND URL_ESTADO = :url
                AND TEXTO_URL = :file_name
                FETCH FIRST 1 ROWS ONLY
            """

            params = {
                "despa_liti": despa_liti,
                "url": url,
                "file_name": file_name
            }

            await asyncio.to_thread(cursor.execute, query, params)
            result = await asyncio.to_thread(cursor.fetchone)
            cursor.close()

            return result is not None  # True si encontró algo, False si no

        except oracledb.DatabaseError as e:
            logging.error(f"❌ Error al consultar existencia del registro: {e}")
            raise e

    async def add_subfile_record(self, despa_liti: int, url: str, file_type: int, file_name: str, publication_date: str) -> int:
        creation_date = datetime.today().strftime('%Y-%m-%d')
        try:
            cursor = await asyncio.to_thread(self.connection.cursor)
            estado_id = cursor.var(int)
            query = """
                INSERT INTO liti.CONTROL_ESTADOS_RAMA_TEST (
                    DESPACHO_ID, 
                    URL_ESTADO, 
                    ESTADO_DESCARGA, 
                    FECHA_CREACION_URL,
                    FECHA_CREACION_ARCHIVO,
                    TEXTO_URL, 
                    FECHA_PUBLICACION,
                    DOC_TYPE
                ) VALUES (
                    :despa_liti, 
                    :url, 
                    'SI', 
                    TO_DATE(:creation_date, 'YYYY-MM-DD'),
                    TO_DATE(:creation_date, 'YYYY-MM-DD'), 
                    :file_name, 
                    TO_DATE(:publication_date, 'YYYY-MM-DD'),
                    :file_type
                ) RETURNING ESTADO_ID INTO :estado_id
            """

            params = {
                "despa_liti": despa_liti,
                "url": url,
                "creation_date": creation_date,
                "file_name": file_name,
                "publication_date": publication_date,
                "file_type": file_type,
                "estado_id": estado_id
            }

            await asyncio.to_thread(cursor.execute, query, params)

            self.connection.commit()
            result_value = estado_id.getvalue()
            result_id = int(result_value[0] if isinstance(result_value, list) else result_value)
            cursor.close()

            return result_id

        except oracledb.DatabaseError as e:
            logging.error(f"❌ Error al ejecutar la consulta: {e}")
            raise e

    async def close_connection(self):
        if self.connection:
            self.connection.close()
            logging.info("🔌 Conexión cerrada.")
