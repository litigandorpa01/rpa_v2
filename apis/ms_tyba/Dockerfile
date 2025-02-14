FROM python:3.12-slim

# Copiar la aplicación
COPY ./ms_tyba /home/app

WORKDIR /home/app

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Exponer el puerto
EXPOSE 5050

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5050"]