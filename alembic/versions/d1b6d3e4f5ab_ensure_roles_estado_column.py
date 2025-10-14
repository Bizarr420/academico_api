"""Ensure roles table has estado column"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d1b6d3e4f5ab"
down_revision: Union[str, Sequence[str], None] = ("b1b20f6bbce8", "c2b3c3b1c1a9")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add the ``estado`` column to ``roles`` when missing."""

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("roles")}

    if "estado" not in columns:
        op.add_column(
            "roles",
            sa.Column("estado", sa.String(length=10), nullable=True),
        )
        op.execute("UPDATE roles SET estado = 'ACTIVO' WHERE estado IS NULL")
        op.alter_column(
            "roles",
            "estado",
            existing_type=sa.String(length=10),
            nullable=False,
            server_default="ACTIVO",
        )
    else:
        op.execute("UPDATE roles SET estado = 'ACTIVO' WHERE estado IS NULL")
        op.alter_column(
            "roles",
            "estado",
            existing_type=sa.String(length=10),
            nullable=False,
            server_default="ACTIVO",
        )


def downgrade() -> None:
    """Remove the ``estado`` column if present."""

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("roles")}

    if "estado" in columns:
        op.drop_column("roles", "estado")
