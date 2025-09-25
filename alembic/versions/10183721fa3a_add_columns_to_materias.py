"""add columns to materias

Revision ID: 10183721fa3a
Revises: a79045946885
Create Date: 2025-09-23 23:58:41.013747

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
revision = "10183721fa3a"
down_revision = "a79045946885"
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table("materias") as batch:
        # aÃ±ade columnas que faltan (idempotente si ya existen no lo repitas)
        batch.add_column(sa.Column("descripcion", sa.Text(), nullable=True))
        batch.add_column(sa.Column("estado", sa.String(length=10), nullable=False, server_default="ACTIVO"))
        batch.add_column(sa.Column("created_at", sa.DateTime(), nullable=False,
                                   server_default=sa.text("CURRENT_TIMESTAMP")))
        batch.add_column(sa.Column("updated_at", sa.DateTime(), nullable=False,
                                   server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")))

def downgrade():
    with op.batch_alter_table("materias") as batch:
        batch.drop_column("updated_at")
        batch.drop_column("created_at")
        batch.drop_column("estado")
        batch.drop_column("descripcion")
