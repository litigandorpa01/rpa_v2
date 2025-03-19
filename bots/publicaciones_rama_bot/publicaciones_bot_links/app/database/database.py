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
            raise e

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

    async def add_url_record(self,despa_liti:int,url:str, creation_date:str,url_text:str,publication_date):
        try:
            cursor = await asyncio.to_thread(self.connection.cursor)

            query = """
                MERGE INTO liti.CONTROL_ESTADOS_RAMA_TEST t
                USING (SELECT :despa_liti AS DESPACHO_ID, :url AS URL_ESTADO FROM dual) src
                ON (t.DESPACHO_ID = src.DESPACHO_ID AND t.URL_ESTADO = src.URL_ESTADO)
                WHEN NOT MATCHED THEN
                INSERT (
                    DESPACHO_ID, 
                    URL_ESTADO, 
                    ESTADO_DESCARGA, 
                    FECHA_CREACION_URL, 
                    TEXTO_URL, 
                    FECHA_PUBLICACION,
                    DOC_TYPE
                ) VALUES (
                    :despa_liti, 
                    :url, 
                    'NO', 
                    TO_DATE(:creation_date, 'YYYY-MM-DD'), 
                    :url_text, 
                    TO_DATE(:publication_date, 'YYYY-MM-DD'),
                    0
                )
            """

            params = {
                "despa_liti": despa_liti,
                "url": url,
                "creation_date": creation_date,
                "url_text": url_text,
                "publication_date": publication_date
            }

            await asyncio.to_thread(cursor.execute, query, params)  # Ejecutar en hilo separado

            self.connection.commit()  # Asegurar que la transacción se guarda

            cursor.close()
            return True  # Si todo salió bien, devolver True

        except oracledb.DatabaseError as e:
            logging.error(f"❌ Error al ejecutar la consulta: {e}")

    async def close_connection(self):
        if self.connection:
            self.connection.close()
            logging.info("🔌 Conexión cerrada.")
