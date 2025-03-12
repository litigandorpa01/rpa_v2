from . import OracleDB 
 
class AsyncDBConnection:
    def __init__(self):
        self.connection = None

    async def __aenter__(self):
        """Método que se ejecuta al entrar en el bloque 'async with'."""
        self.connection = await OracleDB.get_connection()
        return self.connection

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Método que se ejecuta al salir del bloque 'async with'."""
        if self.connection:
            await OracleDB.release_connection(self.connection)
