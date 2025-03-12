import logging
from typing import List, Dict
import json  # Importamos json para asegurarnos de que todo esté bien formateado

from app.database.async_db_connection import AsyncDBConnection


class PublicacionesRepository:
    def __init__(self):
        pass
    
    async def fetch_publicaciones(self, interval_days: int) -> List[Dict[str, str]]:
        try:
            async with AsyncDBConnection() as connection:
                async with connection.cursor() as cursor:
                    # Ejecutar la consulta SQL sin generar JSON manualmente
                    await cursor.execute("""
                        SELECT 
                            A.DESPACHO_ID,
                            A.COD_DESPACHO,
                            TO_CHAR(B.ULTIMAFECHA, 'DD/MM/YYYY') AS ULTIMAFECHA
                        FROM (
                            SELECT 
                                DESPACHO_ID,
                                COD_DESPACHO
                            FROM DESPACHOS_ESTADOS_PUBLICACIONES
                            WHERE ESTADO_DESPACHO = 'SI'
                            ORDER BY FECHA_ULTIMA_VISITA DESC
                        ) A
                        JOIN (
                            SELECT 
                                MAX(FECHA_NOTIFICACION) AS ULTIMAFECHA, 
                                DESPACHO_ID
                            FROM TORRE_CONTROL
                            WHERE FECHA_NOTIFICACION <= TRUNC(SYSDATE)
                            GROUP BY DESPACHO_ID
                        ) B 
                        ON A.DESPACHO_ID = B.DESPACHO_ID
                    """)  

                    # Obtener los resultados
                    result = await cursor.fetchall()

                    # Obtener los nombres de las columnas
                    columns = [desc[0].lower() for desc in cursor.description]

                    # Convertir los resultados en una lista de diccionarios
                    publicaciones = [
                        dict(zip(columns, row)) for row in result
                    ]

                    # Agregar el valor de interval_days a cada diccionario
                    for pub in publicaciones:
                        pub["despa_liti"] = str(pub.pop("despacho_id", ""))
                        pub["cod_despacho"] = str(pub.pop("cod_despacho", ""))
                        pub["ultima_fecha"] = str(pub.pop("ultimafecha", ""))
                        pub["interval_days"] = str(interval_days)

                    return publicaciones

        except Exception as e:
            logging.error(f"Error al ejecutar la consulta: {e}")
            raise e
