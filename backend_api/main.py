from backend_api.database.database import Base, engine
from backend_api.routers import notes_router
from fastapi import FastAPI


# ¡Importante! Tenemos que ejecutar las migrations (alembic) para crear la tabla notes

# Esto crea las tablas en la base de datos SQLite si no existen todavía
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Mi primera API con FastAPI",
    description="Una API de ejemplo.",
    version="1.0.0"
)

@app.get("/")
def root_endpoint():
    return {"msg": "El servidor está levantado bien!"}


app.include_router(notes_router.router)  # Incluimos el router de notas para que los endpoints estén disponibles en la API