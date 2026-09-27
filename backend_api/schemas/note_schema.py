from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class NoteBase(BaseModel):
    title: str = Field(
        ..., 
        max_length=100,
        description="El título de la nota")
    content: str = Field(..., description="El contenido de la nota")
    deadline: datetime = Field(..., description="La fecha límite de la nota")
    completed: Optional[bool] = False
    published: Optional[bool] = True

#creamos los metodos CRUD dado que necesitaremos validar distintos tipos de requests recibidos
class NoteCreate(NoteBase):
    """ Este modelo se usará para crear una nueva nota. """
    pass

class NoteUpdate(NoteBase):
    """ Este modelo se usará para actualizar una nota existente. """
    #ponemos title sobreescrita con un max_length porque es la única que puede dar problemas a nivel de la BD
    title: Optional[str] = Field(None, max_length=100, description="El título de la nota")
    content: Optional[str] = None
    deadline: Optional[datetime] = None
    completed: Optional[bool] = None
    published: Optional[bool] = None
    pass



#clases para transformar la respuesta y poder ocultar campos (copiando de lo que hace laravel en sus models)
class NoteResponse(NoteBase):
    id: int

    #datos de la BD ---> si algun campo queremos que no salga lo eludimos aquí
    title: str
    content: str
    deadline: datetime
    completed: bool
    #published: bool  #----> ejemplo: si no queremos que salga lo comentamos o no lo ponemos
    
    #control fields
    created_at: datetime
    updated_at: datetime

    # Configuración necesaria en Pydantic v2 para que entienda modelos de SQLAlchemy
    model_config = {"from_attributes": True}