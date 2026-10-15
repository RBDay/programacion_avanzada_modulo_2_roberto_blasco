# API de notas

Proyecto de una API REST desarrollada con **FastAPI**, **SQLAlchemy** y **MySQL** (con soporte de migraciones mediante **Alembic** y orquestación con **Docker Compose**). FastAPI genera automáticamente la documentación interactiva de los endpoints.

> **Nota sobre la construcción:** Se ha intentado emular el sistema de funcionamiento del ORM de Laravel (eloquent). Por ello se trabaja con la BD metida en una "sesión" que permite ser llamada desde cualquier sitio. Esto implica ciertos cambios a nivel de Python y FastAPI como la gestión de tareas en segundo plano mediante hilos.

---

## Despliegue con Docker (Recomendado)

El proyecto incluye configuración completa de Docker y Docker Compose para gestionar los 4 servicios:
- **`mysql`**: Base de datos MySQL 8.0 persistente.
- **`phpmyadmin`**: Panel web para gestionar la base de datos MySQL.
- **`api`**: Contenedor FastAPI con ejecución automática de migraciones Alembic antes del arranque.
- **`requests_api`**: Contenedor de pruebas que valida todos los endpoints y casos de error/validación.

### 1. Levantar el stack completo

```bash
docker compose up -d
```

Al levantar los contenedores:
1. MySQL se inicializa y espera hasta estar listo (`healthcheck`).
2. La API se conecta a MySQL y aplica automáticamente las migraciones pendientes con `alembic upgrade head`.
3. El servidor FastAPI se inicia con recarga en caliente (`--reload`).
4. El contenedor de pruebas (`requests_api`) se ejecuta automáticamente, prueba todos los endpoints y sus validaciones, y finaliza con éxito.

### 2. Acceso a los servicios

| Servicio | URL Host | Credenciales / Info |
|---|---|---|
| **API REST** | <http://localhost:8001> | Endpoint raíz: `GET /` |
| **Swagger UI** | <http://localhost:8001/docs> | Documentación interactiva OpenAPI |
| **ReDoc** | <http://localhost:8001/redoc> | Documentación alternativa |
| **phpMyAdmin** | <http://localhost:8081> | **Servidor:** `mysql` \| **Usuario:** `notes_user` \| **Password:** `notes_password` |
| **MySQL (Host)** | `localhost:3308` | Base de datos: `notes_db` |

*(Nota: Los puertos 8001, 8081 y 3308 pueden cambiarse en el archivo `.env` según tus necesidades).*

### 3. Ejecutar la suite de pruebas en cualquier momento

Para lanzar nuevamente el contenedor con `requests_api.py` y probar todos los endpoints y sus validaciones:

```bash
docker compose run --rm requests_api
```

También puedes ejecutarlo localmente desde el host (con el entorno virtual activo):

```bash
python requests_api.py
```

### 4. Parar los contenedores

```bash
docker compose down
```

---

## Ejecución en Local (Sin Docker)

### Requisitos

- Python 3.10 o superior.
- `pip`.
- Base de datos MySQL o SQLite.

### Instalación

Desde la carpeta raíz del proyecto, instala las dependencias:

```bash
pip install -r requirements.txt
```

### Migraciones y Ejecución

```bash
# Aplicar migraciones
alembic upgrade head

# Levantar servidor
uvicorn backend_api.main:app --reload --port 8001
```


## Estructura del proyecto

La siguiente es la organización prevista y el propósito general de cada parte:

```text
.
├── .gitignore
├── README.md
├── requirements.txt
├── test_python.py
└── backend_api/
		├── __init__.py
		├── main.py
		├── database.py
		├── config.py
		├── models/
		│   ├── __init__.py
		│   └── note.py
		├── schemas/
		│   ├── __init__.py
		│   └── note_schema.py
		├── services/
		│   ├── __init__.py
		│   └── note_manager.py
		└── routers/
				├── __init__.py
				└── notes_router.py
```

- **`.gitignore`**: indica qué archivos locales o generados no se deben incluir en Git, como entornos virtuales, caché de Python y bases de datos locales.
- **`README.md`**: explica la instalación, ejecución y organización del proyecto.
- **`requirements.txt`**: enumera las bibliotecas necesarias, como FastAPI, Uvicorn, SQLAlchemy y Requests.
- **`test_python.py`**: script independiente para probar la API mediante peticiones HTTP con la biblioteca `requests`.
- **`backend_api/`**: contiene el código de la aplicación.
	- **`__init__.py`**: identifica el directorio como paquete de Python y puede centralizar inicializaciones del paquete.
	- **`main.py`**: punto de entrada de la aplicación; crea `app` y registra los routers.
	- **`database.py`**: configura la conexión a SQLite, el motor de SQLAlchemy y las sesiones de base de datos.
	- **`config.py`**: reúne la configuración de la aplicación, por ejemplo, valores leídos de variables de entorno.
	- **`models/`**: contiene los modelos ORM que representan las tablas y entidades de la base de datos.
	- **`schemas/`**: define los esquemas Pydantic que validan los datos recibidos y describen las respuestas de la API.
	- **`services/`**: contiene la lógica de negocio, separada de los detalles HTTP y de la persistencia.
	- **`routers/`**: agrupa los endpoints por recurso o funcionalidad y conecta las solicitudes HTTP con los servicios.

> **Nota sobre el estado actual:** Este es un proyecto para aprender y dominar fastapi. La estructura y los detalles pueden cambiar según el avance del proyecto. La estructura actual es una versión simplificada y puede ser mejorada según las necesidades del proyecto. Por ejemplo: añadir docker, pruebas unitarias, etc.

## Dependencias principales

- **FastAPI**: definición de la API y validación e integración con OpenAPI.
- **Uvicorn**: servidor ASGI que ejecuta la aplicación.
- **SQLAlchemy**: acceso ORM a la base de datos.
- **Pydantic**: validación y serialización de datos.
- **Requests**: envío de peticiones HTTP desde el script de prueba.
- **Alembic**: gestión de migraciones del esquema de la base de datos.


## Rutas del proyecto
# Rutas de notas
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST   | /api/notes/ | Crear una nueva nota |
| GET    | /api/notes/ | Obtener todas las notas |
| GET    | /api/notes/{note_id} | Obtener una nota por su ID |
| PUT    | /api/notes/{note_id} | Actualiza una nota por su ID |
| DELETE | /api/notes/{note_id} | Eliminar una nota por su ID |
| GET    | /api/notes/expired/list | Obtener notas caducadas |
| PATCH  | /api/notes/{note_id}/mark_completed | Marcar una nota como completada |


# Rutas por defecto
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET    | /    | Comprueba el estado de la api |
