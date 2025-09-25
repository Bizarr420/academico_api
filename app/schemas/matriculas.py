from pydantic import BaseModel, ConfigDict
from pydantic import BaseModel, ConfigDict  # 👈 añade esto

class MatriculaBase(BaseModel):
    asignacion_id: int
    estudiante_id: int

class MatriculaCreate(MatriculaBase):
    pass

class MatriculaRead(MatriculaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
