from datetime import datetime

from backend_api.database import Base
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime


#creamos el modelo de la tabla Note
class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    deadline = Column(DateTime, nullable=False) #requerimiento del proyecto (no poner a TRUE)
    completed = Column(Boolean, default=False) 
    published = Column(Boolean, default=True)
    #control frields
    created_at = Column(
        DateTime, 
        nullable=False, 
        default=datetime.now()
    )
    updated_at = Column(
      DateTime,
      nullable=False,
      default=datetime.now(),
      onupdate=datetime.now(),
  )