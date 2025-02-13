FROM python:3.12-slim

# Configurar directorio de trabajo
WORKDIR /tyba_bot

# Instalar dependencias del sistema necesarias para Chromium y ChromeDriver
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    xvfb \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Copiar la aplicación al contenedor
COPY bots/tyba_bot /tyba_bot

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Establecer la variable de entorno para Selenium
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_BIN=/usr/bin/chromium-driver

CMD ["sh", "-c", "sleep 5 && xvfb-run --auto-servernum --server-args='-screen 0 1920x1080x24' python3 main.py"]
