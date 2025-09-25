"""create alertas table

Revision ID: f12a9fba7dfd
Revises: 10183721fa3a
Create Date: 2025-09-24 12:36:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "f12a9fba7dfd"
down_revision = "10183721fa3a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "alertas",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("gestion", sa.Integer(), nullable=False),
        sa.Column("asignacion_id", sa.Integer(), nullable=False),
        sa.Column("estudiante_id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=30), nullable=False),
        sa.Column("motivo", sa.String(length=255), nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("estado", sa.String(length=10), nullable=False, server_default="NUEVO"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["asignacion_id"], ["asignacion_docente.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["estudiante_id"], ["estudiantes.id"], ondelete="CASCADE"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_alertas_gestion", "alertas", ["gestion"])
    op.create_index("ix_alertas_asignacion", "alertas", ["asignacion_id"])
    op.create_index("ix_alertas_estudiante", "alertas", ["estudiante_id"])


def downgrade() -> None:
    op.drop_index("ix_alertas_estudiante", table_name="alertas")
    op.drop_index("ix_alertas_asignacion", table_name="alertas")
    op.drop_index("ix_alertas_gestion", table_name="alertas")
    op.drop_table("alertas")
