"""Add estado column to asignacion_docente"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ff3c5c9c4f4e"
down_revision: Union[str, Sequence[str], None] = "a79045946885"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "asignacion_docente",
        sa.Column(
            "estado",
            sa.String(length=10),
            nullable=False,
            server_default="ACTIVO",
        ),
    )
    op.execute(
        "UPDATE asignacion_docente SET estado = 'ACTIVO' WHERE estado IS NULL"
    )

    op.add_column(
        "alertas",
        sa.Column("observacion", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("alertas", "observacion")
    op.drop_column("asignacion_docente", "estado")
