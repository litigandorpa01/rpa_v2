FROM python:3.12-slim

# Instalar dependencias del sistema para Chrome
RUN sudo apt install firefox - Mozilla Firefox 134.0

# Copiar la aplicación
COPY ./tyba_bot /tyba_bot/app

WORKDIR /tyba_bot/app

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

 
CMD ["python", "main.py"]

