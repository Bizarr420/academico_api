"""Enforce ``estudiantes.codigo_est`` not null."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b78bd934f74c"
down_revision: Union[str, Sequence[str], None] = "f331211262dc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    estudiantes = sa.table(
        "estudiantes",
        sa.column("id", sa.Integer()),
        sa.column("codigo_est", sa.String(length=30)),
    )

    result = conn.execute(
        sa.select(estudiantes.c.id).where(estudiantes.c.codigo_est.is_(None))
    ).all()

    for (estudiante_id,) in result:
        conn.execute(
            sa.update(estudiantes)
            .where(estudiantes.c.id == estudiante_id)
            .values(codigo_est=f"AUTO_NULL_FIX_{estudiante_id}")
        )

    op.alter_column(
        "estudiantes",
        "codigo_est",
        existing_type=sa.String(length=30),
        nullable=False,
    )


def downgrade() -> None:
    conn = op.get_bind()
    estudiantes = sa.table(
        "estudiantes",
        sa.column("id", sa.Integer()),
        sa.column("codigo_est", sa.String(length=30)),
    )

    conn.execute(
        sa.update(estudiantes)
        .where(estudiantes.c.codigo_est.like("AUTO_NULL_FIX_%"))
        .values(codigo_est=None)
    )

    op.alter_column(
        "estudiantes",
        "codigo_est",
        existing_type=sa.String(length=30),
        nullable=True,
    )
