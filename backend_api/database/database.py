from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

SQLARCHEMY_DATABASE_URL = "sqlite:///./notes.db"

#si no existe lo creamos ---> perfecto para pruebas y desarrollo en local (no para producción)
engine = create_engine(
    SQLARCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

#configuro el autocomit a false porque así lo hicimos en clase --- por mi sería true
#otro aspecto del "False" es que facilita fakear un transaction ya que python no los tiene
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#esto es para el ORM ----> los modelos tienen que poder leer "BASE" como herencia
Base = declarative_base();

#vamos a trabajar la sesión con un campo llamado "db" para acceder a ella en los endpoints
def get_bd():
    db = SessionLocal() 
    try:
       yield db # esto setea la sesión de "DB" para que lo usen los endpoints
    finally:
        db.close() # cuando el script cierre se cierra la sesión de la base de datos automaticamente --- evitando que se queden conexiones abiertas
        #esto puede funcioanr en un API (un entorno de ejecución que se cierra cuando termina la petición). Pero para un MVC o un entorno con front no serviría
        

#Preguntado a la IA: 
#si quisiera hacer una acción en segundo plano y querrar la sesión debería ejecutarse así: 
# Para lanzarlo:
# hilo = threading.Thread(target=tarea_en_segundo_plano)
# hilo.start()

#Así se cerraría la sesión si o si aunque el endpoint termine con un 200