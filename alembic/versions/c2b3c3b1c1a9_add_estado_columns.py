"""add estado columns to master tables"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c2b3c3b1c1a9"
down_revision: Union[str, Sequence[str], None] = ("3d9c7423011c", "b78bd934f74c")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _add_estado_column(table_name: str) -> None:
    op.add_column(
        table_name,
        sa.Column(
            "estado",
            sa.String(length=10),
            nullable=False,
            server_default="ACTIVO",
        ),
    )


def upgrade() -> None:
    master_tables = [
        "roles",
        "vistas",
        "gestion",
        "niveles",
        "cursos",
        "paralelos",
        "plan_curso_materia",
        "docentes",
    ]

    for table in master_tables:
        _add_estado_column(table)

    # migrate legacy gestion.activo values into the new estado column
    op.execute("UPDATE gestion SET estado = 'INACTIVO' WHERE activo = 0")
    op.execute("UPDATE gestion SET estado = 'ACTIVO' WHERE estado IS NULL")

    # ensure all other tables default to ACTIVO for existing rows
    for table in (t for t in master_tables if t != "gestion"):
        op.execute(f"UPDATE {table} SET estado = 'ACTIVO' WHERE estado IS NULL")

    op.drop_column("gestion", "activo")


def downgrade() -> None:
    op.add_column(
        "gestion",
        sa.Column(
            "activo",
            sa.SmallInteger(),
            nullable=False,
            server_default="1",
        ),
    )
    op.execute(
        "UPDATE gestion SET activo = CASE WHEN estado = 'INACTIVO' THEN 0 ELSE 1 END"
    )

    master_tables = [
        "roles",
        "vistas",
        "gestion",
        "niveles",
        "cursos",
        "paralelos",
        "plan_curso_materia",
        "docentes",
    ]

    for table in master_tables:
        op.drop_column(table, "estado")

    op.alter_column("gestion", "activo", server_default=None)
