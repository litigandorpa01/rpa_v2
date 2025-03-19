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

    async def update_file_download(self, despa_liti: int, url: str):
        try:
            cursor = await asyncio.to_thread(self.connection.cursor)

            current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            query = """
                UPDATE liti.CONTROL_ESTADOS_RAMA_TEST
                SET ESTADO_DESCARGA = 'SI',
                    FECHA_CREACION_ARCHIVO = TO_TIMESTAMP(:current_timestamp, 'YYYY-MM-DD HH24:MI:SS'),
                    DOC_TYPE = 1
                WHERE URL_ESTADO = :url 
                AND DESPACHO_ID = :despa_liti
                RETURNING ESTADO_ID INTO :estado_id
            """

            estado_id = cursor.var(oracledb.NUMBER)

            params = {
                "current_timestamp": current_timestamp,
                "url": url,
                "despa_liti": despa_liti,
                "estado_id": estado_id
            }

            await asyncio.to_thread(cursor.execute, query, params)
            self.connection.commit()

            estado_id_value = estado_id.getvalue()
            cursor.close()

            return estado_id_value[0] if estado_id_value else None

        except oracledb.DatabaseError as e:
            logging.error(f"❌ Error al ejecutar la consulta: {e}")
            raise e

    async def close_connection(self):
        if self.connection:
            self.connection.close()
            logging.info("🔌 Conexión cerrada.")
