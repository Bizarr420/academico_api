"""add vistas and audit logs

Revision ID: ce370f07d10f
Revises: b1b20f6bbce8
Create Date: 2025-09-29 23:36:00.739920

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ce370f07d10f'
down_revision: Union[str, Sequence[str], None] = 'b1b20f6bbce8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'vistas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=60), nullable=False),
        sa.Column('codigo', sa.String(length=60), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('codigo'),
    )

    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('actor_id', sa.Integer(), nullable=True),
        sa.Column('accion', sa.String(length=60), nullable=False),
        sa.Column('entidad', sa.String(length=60), nullable=False),
        sa.Column('entidad_id', sa.String(length=60), nullable=True),
        sa.Column('ip_origen', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('creado_en', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['actor_id'], ['usuarios.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'rol_vistas',
        sa.Column('rol_id', sa.Integer(), nullable=False),
        sa.Column('vista_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['rol_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['vista_id'], ['vistas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('rol_id', 'vista_id'),
        sa.UniqueConstraint('rol_id', 'vista_id', name='uq_rol_vista'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('rol_vistas')
    op.drop_table('audit_logs')
    op.drop_table('vistas')
