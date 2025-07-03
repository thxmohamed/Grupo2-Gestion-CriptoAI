# Usar Python 3.11 como imagen base
FROM python:3.11-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update --allow-releaseinfo-change && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt primero para aprovechar el cache de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Crear directorio para la base de datos si no existe
RUN mkdir -p /app/data

# Crear usuario no root para seguridad
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Exponer el puerto 8000
EXPOSE 8000

# Variables de entorno
ENV PYTHONPATH=/app
ENV DATABASE_URL=sqlite:///./data/criptoai.db
ENV ENVIRONMENT=production

# Comando para ejecutar la aplicación
CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
