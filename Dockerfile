FROM python:3.11-slim

# Evitar buffering en stdout/stderr y generación de .pyc
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Instalar dependencias mínimas del sistema (curl para comprobación de salud y debugging)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero para aprovechar la caché de capas de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

# Asegurar permisos de ejecución en entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Exponer el puerto de FastAPI
EXPOSE 8000

# Usar el script de entrada para migraciones y ejecución
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "backend_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
