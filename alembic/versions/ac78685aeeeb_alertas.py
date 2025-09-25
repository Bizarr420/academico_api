from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "ac78685aeeeb"
down_revision: Union[str, Sequence[str], None] = "10183721fa3a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # Evita fallo si alguien ya la creó por create_all o manualmente
    if "alertas" in insp.get_table_names():
        return

    op.create_table(
        "alertas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("gestion", sa.Integer(), nullable=False),
        sa.Column("asignacion_id", sa.Integer(), nullable=False, index=True),
        sa.Column("estudiante_id", sa.Integer(), nullable=False, index=True),
        sa.Column("tipo", sa.String(length=30), nullable=False),
        sa.Column("motivo", sa.String(length=255), nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("estado", sa.String(length=10), nullable=False, server_default="NUEVO"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )

    # Índices útiles
    op.create_index("ix_alertas_gestion", "alertas", ["gestion"])
    op.create_index("ix_alertas_asignacion", "alertas", ["asignacion_id"])
    op.create_index("ix_alertas_estudiante", "alertas", ["estudiante_id"])

    # 🔗 FKs a tablas que sí existen en tu BD actual
    op.create_foreign_key(
        "fk_alertas_asignacion_docente",
        source_table="alertas",
        referent_table="asignacion_docente",  # <= tu tabla existente
        local_cols=["asignacion_id"],
        remote_cols=["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_alertas_estudiante",
        source_table="alertas",
        referent_table="estudiantes",
        local_cols=["estudiante_id"],
        remote_cols=["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    # Borrar en orden inverso
    try:
        op.drop_constraint("fk_alertas_estudiante", "alertas", type_="foreignkey")
    except Exception:
        pass
    try:
        op.drop_constraint("fk_alertas_asignacion_docente", "alertas", type_="foreignkey")
    except Exception:
        pass

    for ix in ("ix_alertas_estudiante", "ix_alertas_asignacion", "ix_alertas_gestion"):
        try:
            op.drop_index(ix, table_name="alertas")
        except Exception:
            pass

    op.drop_table("alertas")
