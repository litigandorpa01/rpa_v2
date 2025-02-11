FROM python:3.12-slim

# Instalar dependencias del sistema y Firefox
RUN apt-get update && apt-get install -y \
    firefox-esr \
    wget \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libgbm1 \
    libxkbcommon-x11-0 \
    && rm -rf /var/lib/apt/lists/*  # Limpia el caché para reducir la imagen

# Configurar directorio de trabajo
WORKDIR /tyba_bot/app

# Copiar la aplicación al contenedor
COPY ./tyba_bot /tyba_bot/app

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Comando por defecto para ejecutar el bot
CMD ["python", "main.py"]
