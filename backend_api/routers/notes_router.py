from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend_api.database.database import get_bd
from backend_api.schemas.note_schema import NoteCreate, NoteResponse, NoteUpdate
from backend_api.services.note_manager import NoteManager



#definimos el router para que este fichero tenga los endpoints de la API de notas 
# y se pueda importar en main.py
router = APIRouter(prefix="/api/notes", tags=["Notes Management"])

@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_new_note(note_data: NoteCreate, db: Session = Depends(get_bd)):
    """Permite añadir una nueva nota aplicando las validaciones del negocio."""
    manager = NoteManager(
                  title=note_data.title,
                  content=note_data.content,
                  deadline=note_data.deadline,
                  completed=note_data.completed,
                  published=note_data.published,
                  db_session=db,
    )
    return manager.create_note(note_data)

@router.get("/{note_id}", response_model=NoteResponse, summary="Obtener una nota por su ID")
def get_single_note(note_id: int, db: Session = Depends(get_bd)):
  """Obtiene el contenido de una nota dado su id (y valida si ha expirado)."""
  # putada: me he dado cuenta que al no definirlos con un default tengo que pasar los 3 primeros parametros
  # no lo corrijo porque ya llevo horas con la actividad pero debería
  manager = NoteManager(title="", content="", deadline=datetime.now(), db_session=db)
  try:
      note = manager.get_note_by_id(note_id)
      return note
  except HTTPException as e:
      raise e
  except ValueError as ve:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

@router.put("/{note_id}", response_model=NoteResponse, summary="Actualizar una nota por su ID")
def update_existing_note(note_id: int, note_data: NoteUpdate, db: Session = Depends(get_bd)):
    """Actualiza una nota específica dado su ID."""
    manager = NoteManager(title="", content="", deadline=datetime.now(), db_session=db)
    try:
        updated_note = manager.update_note(note_id, note_data)
        if not updated_note:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nota no encontrada")
        return updated_note
    except HTTPException as e:
        raise e
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

@router.get("/", response_model=List[NoteResponse], summary="Obtener todas las notas")
def get_all_notes(include_expired: bool = False, db: Session = Depends(get_bd)):
    """Obtiene la lista de todas las notas, permitiendo filtrar opcionalmente las caducadas."""
    manager = NoteManager(title="", content="", deadline=datetime.now(), db_session=db)
    return manager.get_all_notes(include_expired=include_expired)

@router.get("/expired/list", response_model=List[NoteResponse], summary="Obtener notas caducadas")
def get_expired_notes(db: Session = Depends(get_bd)):
    """Obtiene la lista de todas las notas caducadas."""
    manager = NoteManager(title="", content="", deadline=datetime.now(), db_session=db)
    return manager.get_expired_notes()

@router.patch("/{note_id}/mark_completed", response_model=NoteResponse, summary="Marcar una nota como completada")
def mark_note_as_completed(note_id: int, db: Session = Depends(get_bd)):
    """Marca una nota específica como completada."""
    manager = NoteManager(title="", content="", deadline=datetime.now(), db_session=db)
    try:
        updated_note = manager.mark_as_completed(note_id)
        return updated_note
    except HTTPException as e:
        raise e
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

@router.delete("/{note_id}", response_model=NoteResponse, summary="Eliminar una nota por su ID")
def delete_note(note_id: int, db: Session = Depends(get_bd)):
    """Elimina una nota específica dado su ID."""
    manager = NoteManager(title="", content="", deadline=datetime.now(), db_session=db)
    try:
        deleted_note = manager.delete_note(note_id)
        if not deleted_note:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nota no encontrada")
        return deleted_note
    except HTTPException as e:
        raise e
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

