import re
import json
import aiofiles
from datetime import datetime

class TybaFileProcessor:
    def __init__(self, file):
        self.file = file
        self.file_name = None

    async def read_file_by_chunks(self, chunk_size: int = 1024):
        """Lee el archivo en fragmentos pequeños"""
        while chunk := await self.file.read(chunk_size):
            yield chunk.decode("utf-8")


    async def process_file(self):
        """Procesa el archivo, extrae los IDs y guarda el resultado en JSON"""
        unique_radicados = set()
        invalid_ids = set()
        buffer = ""

        async for chunk in self.read_file_by_chunks():
            buffer += chunk
            buffer = buffer.replace("\n", "").replace("\r", "").replace(" ", "")
            buffer = re.sub(r",+", ",", buffer)

            ids = buffer.split(",")
            buffer = ids.pop()  # Mantener la última parte en buffer

            for rid in ids:
                if re.fullmatch(r"\d{23}", rid):
                    unique_radicados.add(rid)
                elif rid:
                    invalid_ids.add(rid)

        # Procesar el último fragmento del buffer
        if buffer and re.fullmatch(r"\d{23}", buffer):
            unique_radicados.add(buffer)
        elif buffer:
            invalid_ids.add(buffer)

        processed_data = [{"process_id": rid} for rid in unique_radicados]
        self.file_name = f"process_ids_tyba_{datetime.today().strftime('%Y-%m-%d')}.json"

        async with aiofiles.open(self.file_name, "w") as f:
            await f.write(json.dumps(processed_data, indent=4))

        return self.file_name, len(unique_radicados), len(invalid_ids), list(invalid_ids)

