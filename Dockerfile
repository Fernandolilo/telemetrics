FROM python:3.12-slim

# Instala dependências de sistema necessárias para Bluetooth
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libdbus-1-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

# Força a instalação com suporte async
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "flask[async]" bleak

COPY . .

CMD ["python", "app.py"]