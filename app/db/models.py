from datetime import datetime
from enum import Enum
from sqlalchemy.types import Numeric
from decimal import Decimal
from datetime import date
from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, Integer
# app/db/base.py
from sqlalchemy.orm import DeclarativeBase
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint  # y lo que uses
from sqlalchemy.orm import Mapped, relationship
from .base import Base  # 👈 ESTA es tu Base
from sqlalchemy import String, Text, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Base(DeclarativeBase):
    """Base declarativa común para todos los modelos."""
    pass

class Asignacion(Base):
    __tablename__ = "asignaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    docente_id:  Mapped[int] = mapped_column(ForeignKey("docentes.id"), nullable=False)
    materia_id:  Mapped[int] = mapped_column(ForeignKey("materias.id"), nullable=False)
    curso_id:    Mapped[int] = mapped_column(ForeignKey("cursos.id"), nullable=False)
    paralelo_id: Mapped[int] = mapped_column(ForeignKey("paralelos.id"), nullable=False)
    gestion:     Mapped[str] = mapped_column(String(10), nullable=False)

    __table_args__ = (
        UniqueConstraint("docente_id","materia_id","curso_id","paralelo_id","gestion",
                         name="uq_asignacion"),
    )

    # relaciones opcionales
    docente  = relationship("Docente")
    materia  = relationship("Materia")
    curso    = relationship("Curso")
    paralelo = relationship("Paralelo")

from sqlalchemy import (
    Integer, String, Date, DateTime, Enum as SAEnum, ForeignKey, TIMESTAMP, func
)
from sqlalchemy import (
    DECIMAL, CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.orm import Mapped, relationship
from app.db.base import Base

from sqlalchemy import (
    SmallInteger
)

class SexoEnum(str, Enum): M="M"; F="F"; X="X"
class EstadoUsuarioEnum(str, Enum): ACTIVO="ACTIVO"; INACTIVO="INACTIVO"

class Rol(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    usuarios = relationship("Usuario", back_populates="rol")

class Persona(Base):
    __tablename__ = "personas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombres: Mapped[str] = mapped_column(String(120), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(120), nullable=False)
    # antes:
    # sexo: Mapped[SexoEnum] = mapped_column(SAEnum(SexoEnum), nullable=False)

    # después (igual a tu DDL CHAR(1)):
    from sqlalchemy import String
    sexo: Mapped[str] = mapped_column(String(1), nullable=False)

    fecha_nacimiento: Mapped[date] = mapped_column(Date, nullable=False)
    celular: Mapped[str | None] = mapped_column(String(20))
    direccion: Mapped[str | None] = mapped_column(String(255))
    creado_en: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    actualizado_en: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)
    ci = relationship("CIPersona", back_populates="persona", uselist=False)
    usuario = relationship("Usuario", back_populates="persona", uselist=False)

class CIPersona(Base):
    __tablename__ = "ci_persona"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    persona_id: Mapped[int] = mapped_column(ForeignKey("personas.id", ondelete="CASCADE"), nullable=False)
    ci_numero: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    ci_complemento: Mapped[str | None] = mapped_column(String(5))
    ci_expedicion: Mapped[str | None] = mapped_column(String(5))
    persona = relationship("Persona", back_populates="ci")

class Usuario(Base):
    __tablename__ = "usuarios"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    persona_id: Mapped[int] = mapped_column(ForeignKey("personas.id", ondelete="CASCADE"), nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    rol_id: Mapped[int | None] = mapped_column(ForeignKey("roles.id"))
    estado: Mapped[EstadoUsuarioEnum] = mapped_column(SAEnum(EstadoUsuarioEnum), nullable=False, default=EstadoUsuarioEnum.ACTIVO)
    ultimo_acceso_en: Mapped[datetime | None] = mapped_column(DateTime)
    creado_en: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    persona = relationship("Persona", back_populates="usuario")
    rol = relationship("Rol", back_populates="usuarios")

class Estudiante(Base):
    __tablename__ = "estudiantes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    persona_id: Mapped[int] = mapped_column(ForeignKey("personas.id"), nullable=False)
    codigo_est: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    __table_args__ = (UniqueConstraint("codigo_est", name="uq_est_codigo"),)

class TipoEvalEnum(str, Enum):
    EXAMEN = "EXAMEN"
    TAREA = "TAREA"
    PROYECTO = "PROYECTO"
    PRACTICA = "PRACTICA"
    OTRO = "OTRO"

# Stub opcional: no necesitas mapear toda la tabla, solo el PK para la FK
#class AsignacionDocente(Base):
    #__tablename__ = "asignacion_docente"
    #id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

from sqlalchemy import Enum as SAEnum

TIPOS = ("EXAMEN","TAREA","PROYECTO","PRACTICA","OTRO")

class Evaluacion(Base):
    __tablename__ = "evaluaciones"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asignacion_id: Mapped[int] = mapped_column(ForeignKey("asignacion_docente.id", ondelete="CASCADE"), nullable=False)
    titulo: Mapped[str] = mapped_column(String(120), nullable=False)
    tipo: Mapped[str] = mapped_column(
        SAEnum(*TIPOS, name="tipo_eval", native_enum=False, validate_strings=True),
        nullable=False, default="OTRO"
    )
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    ponderacion: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    __table_args__ = (UniqueConstraint("asignacion_id", "titulo", name="uq_eval_asig_titulo"),)



class Nota(Base):
    __tablename__ = "notas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    evaluacion_id: Mapped[int] = mapped_column(ForeignKey("evaluaciones.id"), nullable=False)
    estudiante_id: Mapped[int] = mapped_column(ForeignKey("estudiantes.id"), nullable=False)
    calificacion: Mapped[float] = mapped_column(DECIMAL(5, 2), nullable=False)
    observacion: Mapped[str | None] = mapped_column(String(255))

    __table_args__ = (
        CheckConstraint("calificacion >= 0 AND calificacion <= 100", name="ck_nota_calificacion"),
        UniqueConstraint("evaluacion_id", "estudiante_id", name="uq_nota_eval_est"),
        Index("idx_nota_est", "estudiante_id"),
    )

# --- ORGANIZACIÓN ACADÉMICA ---
class Gestion(Base):
    __tablename__ = "gestion"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[date] = mapped_column(Date, nullable=False)
    activo: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)

# app/db/models.py (ejemplo)
class Nivel(Base):
    __tablename__ = "niveles"
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    etiqueta: Mapped[str] = mapped_column(String(20), nullable=False)  # 👈


# app/db/models.py (ejemplo)
class Curso(Base):
    __tablename__ = "cursos"
    id: Mapped[int] = mapped_column(primary_key=True)
    nivel_id: Mapped[int] = mapped_column(ForeignKey("niveles.id"), nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    etiqueta: Mapped[str] = mapped_column(String(20), nullable=False)

    __table_args__ = (
        UniqueConstraint("nivel_id", "nombre", name="uq_cursos_nivel_nombre"),
        # UniqueConstraint("etiqueta", name="uq_cursos_etiqueta"),  # opcional
    )


class Paralelo(Base):
    __tablename__ = "paralelos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    curso_id: Mapped[int] = mapped_column(ForeignKey("cursos.id", ondelete="CASCADE"), nullable=False)
    etiqueta: Mapped[str] = mapped_column(String(10), nullable=False)
    __table_args__ = (UniqueConstraint("curso_id", "etiqueta", name="uq_paralelo"),)

# app/db/models.py (ejemplo)
# app/db/models.py (fragmento)
class Materia(Base):
    __tablename__ = "materias"
    __table_args__ = (
        UniqueConstraint("codigo", name="uq_materias_codigo"),
        UniqueConstraint("nombre", name="uq_materias_nombre"),  # tu DB tiene UNIQUE en nombre
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    codigo: Mapped[str] = mapped_column(String(20), nullable=False, index=True, unique=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    area: Mapped[str | None] = mapped_column(String(100), nullable=True)  # 👈 NUEVO

    estado: Mapped[str] = mapped_column(String(10), nullable=False, server_default="ACTIVO")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

class PlanCursoMateria(Base):
    __tablename__ = "plan_curso_materia"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    curso_id: Mapped[int] = mapped_column(ForeignKey("cursos.id", ondelete="CASCADE"), nullable=False)
    materia_id: Mapped[int] = mapped_column(ForeignKey("materias.id", ondelete="CASCADE"), nullable=False)
    horas_sem: Mapped[int | None] = mapped_column(SmallInteger)
    __table_args__ = (UniqueConstraint("curso_id", "materia_id", name="uq_plan"),)

class Docente(Base):
    __tablename__ = "docentes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    persona_id: Mapped[int] = mapped_column(ForeignKey("personas.id", ondelete="CASCADE"), unique=True,
                                            nullable=False)
    titulo: Mapped[str | None] = mapped_column(String(120))

class AsignacionDocente(Base):
    __tablename__ = "asignacion_docente"

    id = mapped_column(Integer, primary_key=True)

    # usar FK a la tabla gestion
    gestion_id = mapped_column(ForeignKey("gestion.id"), nullable=False, index=True)
    gestion    = relationship("Gestion")  # relación opcional

    docente_id  = mapped_column(ForeignKey("docentes.id"), nullable=False)
    materia_id  = mapped_column(ForeignKey("materias.id"), nullable=False)
    curso_id    = mapped_column(ForeignKey("cursos.id"), nullable=False)
    paralelo_id = mapped_column(ForeignKey("paralelos.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("gestion_id","docente_id","materia_id","curso_id","paralelo_id", name="uq_asig"),
    )
# app/db/models.py
# imports típicos arriba del archivo:
# from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint, Index, select, func
# from sqlalchemy.orm import Mapped, mapped_column

class Matricula(Base):
    __tablename__ = "matriculas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asignacion_id: Mapped[int] = mapped_column(
        ForeignKey("asignacion_docente.id", ondelete="CASCADE"),
        nullable=False,
    )
    estudiante_id: Mapped[int] = mapped_column(
        ForeignKey("estudiantes.id", ondelete="CASCADE"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("asignacion_id", "estudiante_id", name="uq_matricula"),
        Index("ix_matriculas_asig", "asignacion_id"),
        Index("ix_matriculas_est", "estudiante_id"),
    )

# 👇 IMPORTANTE: usa alias para no chocar con el Enum de la stdlib
from sqlalchemy import Enum as SAEnum, UniqueConstraint, ForeignKey, Integer, String, Date
from sqlalchemy.orm import Mapped, mapped_column
# NO importes "from enum import Enum" aquí

class Asistencia(Base):
    __tablename__ = "asistencias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fecha: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    asignacion_id: Mapped[int] = mapped_column(ForeignKey("asignacion_docente.id"), nullable=False, index=True)
    estudiante_id: Mapped[int] = mapped_column(ForeignKey("estudiantes.id"), nullable=False, index=True)

    # ✅ Para MySQL, evita el kwarg "name" y asegúrate de usar el Enum de SQLAlchemy (SAEnum)
    estado: Mapped[str] = mapped_column(
        SAEnum("PRESENTE", "AUSENTE", "TARDE", "JUSTIFICADO", native_enum=True),
        nullable=False,
        default="PRESENTE",
    )

    observacion: Mapped[str | None] = mapped_column(String(255), nullable=True)

    __table_args__ = (
        UniqueConstraint("fecha", "asignacion_id", "estudiante_id", name="uq_asistencia_unica"),
    )

from sqlalchemy import String, Integer, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

class Alerta(Base):
    __tablename__ = "alertas"

    id: Mapped[int] = mapped_column(primary_key=True)
    gestion: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    asignacion_id: Mapped[int] = mapped_column(
        ForeignKey("asignacion_docente.id", ondelete="CASCADE"),  # 👈 aquí el cambio
        nullable=False, index=True
    )
    estudiante_id: Mapped[int] = mapped_column(
        ForeignKey("estudiantes.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)       # p.ej. "RIESGO_PROMEDIO", "RIESGO_ASISTENCIA"
    motivo: Mapped[str] = mapped_column(String(255), nullable=False)    # texto corto: "promedio 48 < umbral 51"
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)   # 0-100 simple

    estado: Mapped[str] = mapped_column(String(10), nullable=False, server_default="NUEVO")  # NUEVO/LEIDO/CERRADO

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
