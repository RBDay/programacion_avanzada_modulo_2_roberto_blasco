from backend_api.routers import notes_router
from fastapi import FastAPI



app = FastAPI(
    title="Mi primera API con FastAPI",
    description="Una API de ejemplo.",
    version="1.0.0"
)

@app.get("/")
def root_endpoint():
    return {"msg": "El servidor está levantado bien!"}


app.include_router(notes_router.router)  # Incluimos el router de notas para que los endpoints estén disponibles en la API