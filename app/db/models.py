"""SQLAlchemy ORM models for the Académico API."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator

from .base import Base


class EstadoUsuarioEnum(str, Enum):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"


class SexoEnum(str, Enum):
    """Sex designation used by :class:`Persona` records.

    The database stores the verbose values (``MASCULINO``, ``FEMENINO`` and
    ``OTRO``) because previous migrations were generated with those literals.
    Our API, however, historically used the short codes ``M``, ``F`` and ``X``.
    To keep backwards compatibility with existing data and payloads we accept
    both formats by normalising the incoming value inside ``_missing_``.
    """

    MASCULINO = "MASCULINO"
    FEMENINO = "FEMENINO"
    OTRO = "OTRO"

    @property
    def short_code(self) -> str:
        """Return the short (``M``/``F``/``X``) representation."""

        return {
            SexoEnum.MASCULINO: "M",
            SexoEnum.FEMENINO: "F",
            SexoEnum.OTRO: "X",
        }[self]

    @classmethod
    def _missing_(cls, value):
        """Allow the enum to be constructed from short codes as well."""

        if isinstance(value, str):
            normalised = value.strip().upper()
            if not normalised:
                return None
            if normalised in cls.__members__:
                return cls.__members__[normalised]
            alias_map = {
                "M": cls.MASCULINO,
                "F": cls.FEMENINO,
                "X": cls.OTRO,
            }
            return alias_map.get(normalised)
        return None


class SexoEnumType(TypeDecorator):
    """Custom SQLAlchemy type that normalises ``SexoEnum`` values."""

    impl = String(1)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, SexoEnum):
            enum_value = value
        elif isinstance(value, str):
            enum_value = SexoEnum._missing_(value)
            if enum_value is None:
                enum_value = SexoEnum(value)
        else:
            raise TypeError(f"Unsupported value for SexoEnum: {value!r}")

        return enum_value.short_code

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        try:
            return SexoEnum(value)
        except ValueError:
            enum_value = SexoEnum._missing_(value)
            if enum_value is None:
                raise
            return enum_value


class Rol(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    usuarios: Mapped[list["Usuario"]] = relationship("Usuario", back_populates="rol")


class Persona(Base):
    __tablename__ = "personas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombres: Mapped[str] = mapped_column(String(120), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(120), nullable=False)
    sexo: Mapped[SexoEnum] = mapped_column(SexoEnumType(), nullable=False)
    fecha_nacimiento: Mapped[date] = mapped_column(Date, nullable=False)
    celular: Mapped[str | None] = mapped_column(String(20))
    direccion: Mapped[str | None] = mapped_column(String(255))
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    ci: Mapped["CIPersona | None"] = relationship(
        "CIPersona", back_populates="persona", uselist=False
    )
    usuario: Mapped["Usuario | None"] = relationship(
        "Usuario", back_populates="persona", uselist=False
    )


class CIPersona(Base):
    __tablename__ = "ci_persona"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    persona_id: Mapped[int] = mapped_column(
        ForeignKey("personas.id", ondelete="CASCADE"), nullable=False
    )
    ci_numero: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    ci_complemento: Mapped[str | None] = mapped_column(String(5))
    ci_expedicion: Mapped[str | None] = mapped_column(String(5))

    persona: Mapped[Persona] = relationship("Persona", back_populates="ci")


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    persona_id: Mapped[int] = mapped_column(
        ForeignKey("personas.id", ondelete="CASCADE"), nullable=False
    )
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    rol_id: Mapped[int | None] = mapped_column(ForeignKey("roles.id"))
    estado: Mapped[EstadoUsuarioEnum] = mapped_column(
        SAEnum(EstadoUsuarioEnum), nullable=False, default=EstadoUsuarioEnum.ACTIVO
    )
    ultimo_acceso_en: Mapped[datetime | None] = mapped_column(DateTime)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    persona: Mapped[Persona] = relationship("Persona", back_populates="usuario")
    rol: Mapped[Rol | None] = relationship("Rol", back_populates="usuarios")


class Estudiante(Base):
    __tablename__ = "estudiantes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    persona_id: Mapped[int] = mapped_column(
        ForeignKey("personas.id", ondelete="CASCADE"), nullable=False
    )
    codigo_est: Mapped[str | None] = mapped_column(String(30), unique=True)

    __table_args__ = (UniqueConstraint("codigo_est", name="uq_est_codigo"),)


class TipoEvalEnum(str, Enum):
    EXAMEN = "EXAMEN"
    TAREA = "TAREA"
    PROYECTO = "PROYECTO"
    PRACTICA = "PRACTICA"
    OTRO = "OTRO"


class Evaluacion(Base):
    __tablename__ = "evaluaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asignacion_id: Mapped[int] = mapped_column(
        ForeignKey("asignacion_docente.id", ondelete="CASCADE"), nullable=False
    )
    titulo: Mapped[str] = mapped_column(String(120), nullable=False)
    tipo: Mapped[str] = mapped_column(
        SAEnum(*(item.value for item in TipoEvalEnum), name="tipo_eval", native_enum=False),
        nullable=False,
        default=TipoEvalEnum.OTRO.value,
    )
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    ponderacion: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("0.00"))

    __table_args__ = (
        UniqueConstraint("asignacion_id", "titulo", name="uq_eval_asig_titulo"),
    )


class Nota(Base):
    __tablename__ = "notas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    evaluacion_id: Mapped[int] = mapped_column(
        ForeignKey("evaluaciones.id", ondelete="CASCADE"), nullable=False
    )
    estudiante_id: Mapped[int] = mapped_column(
        ForeignKey("estudiantes.id", ondelete="CASCADE"), nullable=False
    )
    calificacion: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    observacion: Mapped[str | None] = mapped_column(String(255))

    __table_args__ = (
        CheckConstraint("calificacion >= 0 AND calificacion <= 100", name="ck_nota_calificacion"),
        UniqueConstraint("evaluacion_id", "estudiante_id", name="uq_nota_eval_est"),
        Index("idx_nota_est", "estudiante_id"),
    )


class Gestion(Base):
    __tablename__ = "gestion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[date] = mapped_column(Date, nullable=False)
    activo: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)


class Nivel(Base):
    __tablename__ = "niveles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    etiqueta: Mapped[str] = mapped_column(String(20), nullable=False)


class Curso(Base):
    __tablename__ = "cursos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nivel_id: Mapped[int] = mapped_column(
        ForeignKey("niveles.id", ondelete="CASCADE"), nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(60), nullable=False)
    etiqueta: Mapped[str] = mapped_column(String(20), nullable=False)
    grado: Mapped[int | None] = mapped_column(SmallInteger)

    __table_args__ = (
        UniqueConstraint("nivel_id", "nombre", name="uq_cursos_nivel_nombre"),
    )


class Paralelo(Base):
    __tablename__ = "paralelos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    curso_id: Mapped[int] = mapped_column(
        ForeignKey("cursos.id", ondelete="CASCADE"), nullable=False
    )
    etiqueta: Mapped[str] = mapped_column(String(10), nullable=False)
    nombre: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)

    __table_args__ = (
        UniqueConstraint("curso_id", "etiqueta", name="uq_paralelo"),
        UniqueConstraint("nombre", name="uq_paralelo_nombre"),
    )


class Materia(Base):
    __tablename__ = "materias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    codigo: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    descripcion: Mapped[str | None] = mapped_column(Text)
    area: Mapped[str | None] = mapped_column(String(100))
    estado: Mapped[str] = mapped_column(String(10), nullable=False, server_default="ACTIVO")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint("codigo", name="uq_materias_codigo"),
        UniqueConstraint("nombre", name="uq_materias_nombre"),
    )


class PlanCursoMateria(Base):
    __tablename__ = "plan_curso_materia"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    curso_id: Mapped[int] = mapped_column(
        ForeignKey("cursos.id", ondelete="CASCADE"), nullable=False
    )
    materia_id: Mapped[int] = mapped_column(
        ForeignKey("materias.id", ondelete="CASCADE"), nullable=False
    )
    horas_sem: Mapped[int | None] = mapped_column(SmallInteger)

    __table_args__ = (UniqueConstraint("curso_id", "materia_id", name="uq_plan"),)


class Docente(Base):
    __tablename__ = "docentes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    persona_id: Mapped[int] = mapped_column(
        ForeignKey("personas.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    titulo: Mapped[str | None] = mapped_column(String(120))
    profesion: Mapped[str | None] = mapped_column(String(120))


class AsignacionDocente(Base):
    __tablename__ = "asignacion_docente"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    gestion_id: Mapped[int] = mapped_column(
        ForeignKey("gestion.id", ondelete="CASCADE"), nullable=False, index=True
    )
    docente_id: Mapped[int] = mapped_column(
        ForeignKey("docentes.id", ondelete="CASCADE"), nullable=False
    )
    materia_id: Mapped[int] = mapped_column(
        ForeignKey("materias.id", ondelete="CASCADE"), nullable=False
    )
    curso_id: Mapped[int] = mapped_column(
        ForeignKey("cursos.id", ondelete="CASCADE"), nullable=False
    )
    paralelo_id: Mapped[int] = mapped_column(
        ForeignKey("paralelos.id", ondelete="CASCADE"), nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "gestion_id",
            "docente_id",
            "materia_id",
            "curso_id",
            "paralelo_id",
            name="uq_asig",
        ),
    )


class Matricula(Base):
    __tablename__ = "matriculas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asignacion_id: Mapped[int] = mapped_column(
        ForeignKey("asignacion_docente.id", ondelete="CASCADE"), nullable=False
    )
    estudiante_id: Mapped[int] = mapped_column(
        ForeignKey("estudiantes.id", ondelete="CASCADE"), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("asignacion_id", "estudiante_id", name="uq_matricula"),
        Index("ix_matriculas_asig", "asignacion_id"),
        Index("ix_matriculas_est", "estudiante_id"),
    )


ASISTENCIA_ESTADOS = ("PRESENTE", "AUSENTE", "TARDE", "JUSTIFICADO")


class Asistencia(Base):
    __tablename__ = "asistencias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    asignacion_id: Mapped[int] = mapped_column(
        ForeignKey("asignacion_docente.id", ondelete="CASCADE"), nullable=False, index=True
    )
    estudiante_id: Mapped[int] = mapped_column(
        ForeignKey("estudiantes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    estado: Mapped[str] = mapped_column(
        SAEnum(*ASISTENCIA_ESTADOS, name="asistencia_estado", native_enum=True),
        nullable=False,
        default="PRESENTE",
    )
    observacion: Mapped[str | None] = mapped_column(String(255))

    __table_args__ = (
        UniqueConstraint("fecha", "asignacion_id", "estudiante_id", name="uq_asistencia_unica"),
    )


class Alerta(Base):
    __tablename__ = "alertas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    gestion: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    asignacion_id: Mapped[int] = mapped_column(
        ForeignKey("asignacion_docente.id", ondelete="CASCADE"), nullable=False, index=True
    )
    estudiante_id: Mapped[int] = mapped_column(
        ForeignKey("estudiantes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    motivo: Mapped[str] = mapped_column(String(255), nullable=False)
    score: Mapped[int | None] = mapped_column(Integer)
    estado: Mapped[str] = mapped_column(String(10), nullable=False, server_default="NUEVO")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
