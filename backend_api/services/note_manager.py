#los services funcionan igual que en symfony, son clases que encapsulan la lógica de negocio y se encargan de interactuar con los modelos y la base de datos.

from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session

class NoteManager:
    """Clase que encapsula la lógica de negocio relacionada con las notas."""
    def __init__(self, title:str, content: str, deadline: datetime, completed: bool = False, published: bool = True, db_session=None):
        self.id = None;
        self.title = title
        self.content = content
        self.deadline = deadline
        self.completed = completed
        self.published = published
        #seteamos listad de palabras prohibidas por la tarea 
        self._prohibited_words = ["tonto", "gilipollas", "idiota", "imbécil", "estúpido"]
        #seteamos la BD 
        self.db_session = db_session
        

    def create_note(self, note_data):
        from backend_api.models.note import Note  # Importamos el modelo Note aquí para evitar problemas de importación circular
        from backend_api.schemas.note_schema import NoteCreate  # Importamos el esquema NoteCreate aquí para evitar problemas de importación circular
        checked_data = NoteCreate(**note_data.dict());
        new_note = Note(**note_data.dict())
        self.db_session.add(new_note)
        self.db_session.commit()
        self.db_session.refresh(new_note)
        return new_note

    def get_note_by_id(self, note_id, return_db_note=True):
        from backend_api.models.note import (
            Note,
        )  # Importación local para evitar bucles circulares

        # 1. SETEAR: Buscamos la nota en la BD y cargamos sus datos en la instancia actual (self)
        #TODO: se que es una guarrada y que tendría que estar en el init pero me da pereza y no quiero tocarlo ahora
        self.db_note = self.db_session.query(Note).filter(Note.id == note_id).first()

        if not self.db_note:
            raise HTTPException(404)

        # Actualizamos los atributos de 'self' con los valores recuperados de la base de datos
        self.id = self.db_note.id
        self.title = self.db_note.title
        self.content = self.db_note.content
        self.deadline = self.db_note.deadline
        self.completed = self.db_note.completed
        self.published = self.db_note.published

        # 2. CHEQUEAR: Comprobamos si está caducada utilizando el método de nuestra clase POO
        self.is_expired()  # Esto lanzará un ValueError si la nota ha expirado

        # 3. DEVOLVER SELF: Retornamos la propia instancia ya validada y poblada
        return self.db_note if return_db_note else self

    def get_all_notes(self, include_expired=False):
        from backend_api.models.note import Note  # Importamos el modelo Note aquí para evitar problemas de importación circular
        # 1. SETEAR: Obtenemos todas las notas de la base de datos, filtrando según el parámetro include_expired
        if include_expired:
            notes = self.db_session.query(Note).all()
        else:
            notes = self.db_session.query(Note).filter(Note.deadline >= datetime.now()).all()
        # 2. DEVOLVER: Retornamos la lista de notas, ya sea todas o solo las no caducadas
        return notes

    def update_note(self, note_id, note_data):
        from backend_api.models.note import Note  
        from backend_api.schemas.note_schema import NoteUpdate   

        checked_data = NoteUpdate(**note_data.dict(exclude_unset=True))
        
        # al trabajar ahora sobre un modelo no debería dar error
        note = self.get_note_by_id(note_id, return_db_note=True)
        
        if note:
            for key, value in note_data.dict(exclude_unset=True).items():
                setattr(note, key, value)
            note.updated_at = datetime.now() 
            self.db_session.commit()
            self.db_session.refresh(note) # Ahora 'note' sí es el modelo de SQLAlchemy y esto funcionará
            
        return note

    def delete_note(self, note_id):
        from backend_api.models.note import Note  # Importamos el modelo Note aquí para evitar problemas de importación circular
        note = self.get_note_by_id(note_id)

        if note:
            self.db_session.delete(note)
            self.db_session.commit()
        return self.db_note

    # Comprobación requerida: saber si la nota está caducada
    def is_expired(self) -> bool:
        """chequeamos que la nota no esté caducada, si no lanzamos un error"""
        if self.deadline < datetime.now():        
            raise ValueError(f"La nota '{self.title}' ha expirado.")

    def is_published(self) -> bool:
        """ Retorna True si la nota está publicada, False en caso contrario. """
        return self.published

    # funciones requeridas para completar la tarea
    def get_expired_notes(self):
        """Retorna una lista con todas las notas cuya fecha límite ya ha pasado."""
        from backend_api.models.note import Note
        now = datetime.now()
        expired_notes = self.db_session.query(Note).filter(Note.deadline < now).all()
        return expired_notes

    def mark_as_completed(self, note_id: int):
        """Marca una nota específica como completada."""
        db_note = self.get_note_by_id(note_id)
        if not db_note:
            raise HTTPException(status_code=404, detail="Nota no encontrada")
        
        db_note.completed = True
        db_note.updated_at = datetime.now()
        self.db_session.commit()
        self.db_session.refresh(db_note)
        return db_note