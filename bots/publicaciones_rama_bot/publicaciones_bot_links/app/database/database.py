import asyncio
import logging

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

    async def check_url(self,fecha_pub,despa_liti,url):
        try:
            cursor = await asyncio.to_thread(self.connection.cursor)

            query = """
                SELECT CASE 
                    WHEN COUNT(*) > 0 THEN 1 
                    ELSE 0 
                END AS ES_DESCARGADO
                FROM liti.CONTROL_ESTADOS_RAMA_TEST 
                WHERE FECHA_PUBLICACION = TO_DATE(:fecha_pub, 'YYYY-MM-DD') 
                AND DESPACHO_ID = :despa_liti 
                AND URL_ESTADO = :url
                AND ESTADO_DESCARGA = 'SI'
            """

            # Parámetros correctamente formateados
            params = {
                "fecha_pub": fecha_pub,
                "despa_liti": despa_liti,
                "url": url
            }

            await asyncio.to_thread(cursor.execute, query, params)

            result = await asyncio.to_thread(cursor.fetchone)  # Obtener un solo resultado
            cursor.close()

            return bool(result[0]) if result else False  # Convertir a bool directamente

        except oracledb.DatabaseError as e:
            logging.error(f"❌ Error al ejecutar la consulta: {e}")

    async def close_connection(self):
        if self.connection:
            self.connection.close()
            logging.info("🔌 Conexión cerrada.")
