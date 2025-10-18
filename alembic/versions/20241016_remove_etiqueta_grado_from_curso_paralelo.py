"""
Remove 'etiqueta' and 'grado' columns from 'cursos' and 'paralelos'.
Revision ID: 20241016_remove_etiqueta_grado
Revises: 
Create Date: 2025-10-16
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Remove columns from cursos
    with op.batch_alter_table('cursos') as batch_op:
        batch_op.drop_column('etiqueta')
        batch_op.drop_column('grado')
    # Remove column from paralelos
    with op.batch_alter_table('paralelos') as batch_op:
        batch_op.drop_column('etiqueta')

def downgrade():
    # Add columns back if needed
    with op.batch_alter_table('cursos') as batch_op:
        batch_op.add_column(sa.Column('etiqueta', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('grado', sa.SmallInteger(), nullable=True))
    with op.batch_alter_table('paralelos') as batch_op:
        batch_op.add_column(sa.Column('etiqueta', sa.String(length=10), nullable=True))
