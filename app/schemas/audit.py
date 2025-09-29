from datetime import datetime
from pydantic import BaseModel, Field


class AuditLogOut(BaseModel):
    id: int
    actor_id: int | None = None
    accion: str
    entidad: str
    entidad_id: str | None = None
    ip_origen: str | None = None
    user_agent: str | None = None
    creado_en: datetime

    class Config:
        from_attributes = True


class AuditLogPage(BaseModel):
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    size: int = Field(ge=1)
    items: list[AuditLogOut]
