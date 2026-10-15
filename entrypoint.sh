#!/bin/sh
set -e

# Ejecutar espera a base de datos y migraciones si es el contenedor de la API
# me daba problemas la ejecución de las migraciones --- así que lo he extraido en este fichero 
# se que podría ser más elegante (o podría haberlo hecho a mano, esto lo ha hecho una IA) pero estaba ya hasta los mismismisimos de probar y fallar
if [ "$1" = "uvicorn" ] || [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "=================================================="
    echo " Esperando a que MySQL esté listo y disponible..."
    echo "=================================================="
    python - << 'EOF'
import os
import time
import pymysql

db_host = os.getenv("DB_HOST", "mysql")
db_port = int(os.getenv("DB_PORT", "3306"))
db_user = os.getenv("DB_USER", "notes_user")
db_password = os.getenv("DB_PASSWORD", "notes_password")
db_name = os.getenv("DB_NAME", "notes_db")

retries = 30
while retries > 0:
    try:
        conn = pymysql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name,
            connect_timeout=3
        )
        conn.close()
        print("¡Conexión a MySQL establecida con éxito!")
        break
    except Exception as e:
        print(f"Esperando a MySQL en {db_host}:{db_port}... ({e})")
        time.sleep(2)
        retries -= 1
else:
    print("ERROR: No se pudo conectar a MySQL tras múltiples intentos.")
    exit(1)
EOF

    echo "=================================================="
    echo " Ejecutando migraciones de base de datos (Alembic)..."
    echo "=================================================="
    alembic upgrade head
    echo "¡Migraciones aplicadas correctamente!"
    echo "=================================================="
fi

exec "$@"
