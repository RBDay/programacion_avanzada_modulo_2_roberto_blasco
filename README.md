# API de notas

Proyecto de una API REST desarrollada con **FastAPI**, **SQLAlchemy** y **SQLite**. FastAPI genera automáticamente la documentación interactiva de los endpoints.

> **Nota sobre la construcción:** Se ha intentado emular el sistema de funcionamiento del ORM de Laravel (eloquet). Por ello se trabaja con la BD metida en una "sesión" que permite ser llamada desde cualquier sitio. Esto implica ciertos cambios a nivel de Python y Fastapi como la gestión de tareas en segundo plano mediante hilos. 

## Requisitos

- Python 3.10 o superior.
- `pip`.

## Instalación

Desde la carpeta raíz del proyecto, instala las dependencias:

```bash
pip install -r requirements.txt
```

Opcionalmente, crea y activa antes un entorno virtual para aislar las dependencias del proyecto.

## Levantar la API

Desde la carpeta raíz del proyecto, ejecuta:

```bash
uvicorn backend_api.main:app --reload
```

El comando indica a Uvicorn que cargue el objeto `app` definido en `backend_api/main.py`. La opción `--reload` reinicia el servidor cuando detecta cambios en el código; se recomienda para desarrollo.

Cuando el servidor esté en marcha, abre:

- API: <http://127.0.0.1:8000>
- Documentación interactiva Swagger: <http://127.0.0.1:8000/docs>
- Documentación alternativa ReDoc: <http://127.0.0.1:8000/redoc>

Para que el comando funcione, `backend_api/main.py` debe crear la aplicación FastAPI y asignarla a una variable llamada `app`. Los routers deben incluirse en esa aplicación para que sus endpoints aparezcan en `/docs`.

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
