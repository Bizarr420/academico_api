"""merge estudiantes schema.

Revision ID: 3d9c7423011c
Revises: a79045946885, 69e0d76d4c8b, ce370f07d10f
Create Date: 2025-10-05 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "3d9c7423011c"
down_revision: Union[str, Sequence[str], None] = (
    "a79045946885",
    "69e0d76d4c8b",
    "ce370f07d10f",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(bind, table_name: str) -> bool:
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _get_metadata(bind, table_name: str) -> tuple[set[str], set[str], set[str]]:
    inspector = sa.inspect(bind)
    columns = {col["name"] for col in inspector.get_columns(table_name)}
    uniques = {uc["name"] for uc in inspector.get_unique_constraints(table_name) if uc.get("name")}
    fks = {fk["name"] for fk in inspector.get_foreign_keys(table_name) if fk.get("name")}
    return columns, uniques, fks


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    if not _table_exists(bind, "estudiantes"):
        return

    columns, uniques, fks = _get_metadata(bind, "estudiantes")

    fk_names_to_drop = [
        name
        for name in ("fk_estudiantes_persona", "estudiantes_ibfk_1")
        if name in fks
    ]

    with op.batch_alter_table("estudiantes") as batch_op:
        for fk_name in fk_names_to_drop:
            batch_op.drop_constraint(fk_name, type_="foreignkey")
        if "codigo_est" not in columns:
            batch_op.add_column(sa.Column("codigo_est", sa.String(length=30), nullable=True))
        if "codigo_rude" in columns and "uq_estudiantes_rude" in uniques:
            batch_op.drop_constraint("uq_estudiantes_rude", type_="unique")

    if "codigo_rude" in columns:
        op.execute(
            sa.text(
                "UPDATE estudiantes SET codigo_est = codigo_rude "
                "WHERE codigo_est IS NULL OR codigo_est = ''"
            )
        )

    columns, uniques, fks = _get_metadata(bind, "estudiantes")

    with op.batch_alter_table("estudiantes") as batch_op:
        if "codigo_rude" in columns:
            batch_op.drop_column("codigo_rude")
        batch_op.alter_column(
            "codigo_est",
            existing_type=sa.String(length=30),
            nullable=False,
        )
        if "uq_est_codigo" not in uniques:
            batch_op.create_unique_constraint("uq_est_codigo", ["codigo_est"])
        if "fk_estudiantes_persona" not in fks:
            batch_op.create_foreign_key(
                "fk_estudiantes_persona",
                "personas",
                ["persona_id"],
                ["id"],
                ondelete="CASCADE",
            )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    if not _table_exists(bind, "estudiantes"):
        return

    columns, uniques, fks = _get_metadata(bind, "estudiantes")

    with op.batch_alter_table("estudiantes") as batch_op:
        if "fk_estudiantes_persona" in fks:
            batch_op.drop_constraint("fk_estudiantes_persona", type_="foreignkey")
        if "uq_est_codigo" in uniques:
            batch_op.drop_constraint("uq_est_codigo", type_="unique")
        if "codigo_rude" not in columns:
            batch_op.add_column(sa.Column("codigo_rude", sa.String(length=30), nullable=True))

    op.execute(
        sa.text("UPDATE estudiantes SET codigo_rude = codigo_est WHERE codigo_est IS NOT NULL")
    )

    columns, uniques, fks = _get_metadata(bind, "estudiantes")

    with op.batch_alter_table("estudiantes") as batch_op:
        batch_op.alter_column(
            "codigo_est",
            existing_type=sa.String(length=30),
            nullable=True,
        )
        if "codigo_est" in columns:
            batch_op.drop_column("codigo_est")
        if "uq_estudiantes_rude" not in uniques:
            batch_op.create_unique_constraint("uq_estudiantes_rude", ["codigo_rude"])
        if "fk_estudiantes_persona" not in fks:
            batch_op.create_foreign_key(
                "fk_estudiantes_persona",
                "personas",
                ["persona_id"],
                ["id"],
            )
