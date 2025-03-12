import logging
import oracledb

from app.constants import DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_SERVICE_NAME

class OracleDB:
    connection_pool = None

    @staticmethod
    async def create_pool():
        """Crea un pool de conexiones a la base de datos de manera asíncrona."""
        try:
            OracleDB.connection_pool = oracledb.create_pool_async(
                user=DB_USERNAME,
                password=DB_PASSWORD,
                dsn=f"{DB_HOST}:{DB_PORT}/{DB_SERVICE_NAME}",
                min=5,  # Mínimo de conexiones en el pool
                max=20,  # Máximo de conexiones en el pool
                increment=2  # Número de conexiones a agregar cuando se necesiten más
            )
            logging.info("✅ Pool de conexiones creado exitosamente.")
        except oracledb.DatabaseError as e:
            logging.error(f"❌ Error al crear el pool de conexiones: {e}")
            raise

    @staticmethod
    async def get_connection():
        """Obtiene una conexión del pool de manera asíncrona."""
        if OracleDB.connection_pool is None:
            error_msg = "El pool de conexiones no ha sido inicializado."
            logging.error(error_msg)
            raise RuntimeError(error_msg)
        
        try:
            connection = await OracleDB.connection_pool.acquire()
            logging.info("🔗 Conexión adquirida exitosamente.")
            return connection
        except oracledb.DatabaseError as e:
            logging.error(f"❌ Error al adquirir una conexión: {e}")
            raise

    @staticmethod
    async def release_connection(connection):
        """Libera una conexión y la devuelve al pool de manera asíncrona."""
        if OracleDB.connection_pool is None:
            error_msg = "El pool de conexiones no ha sido inicializado."
            logging.error(error_msg)
            raise RuntimeError(error_msg)
        
        try:
            await OracleDB.connection_pool.release(connection)
            logging.info("🔄 Conexión liberada exitosamente.")
        except oracledb.DatabaseError as e:
            logging.error(f"❌ Error al liberar la conexión: {e}")
            raise

    @staticmethod
    async def close_pool():
        """Cierra el pool de conexiones de manera asíncrona."""
        if OracleDB.connection_pool is not None:
            try:
                await OracleDB.connection_pool.close()
                logging.info("🔌 Pool de conexiones cerrado exitosamente.")
            except oracledb.DatabaseError as e:
                logging.error(f"❌ Error al cerrar el pool de conexiones: {e}")
                raise
            finally:
                OracleDB.connection_pool = None
