"""add profesion to docentes

Revision ID: dba2a6a3f82f
Revises: c69f6c526f0d
Create Date: 2025-09-23 13:04:20.925179

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dba2a6a3f82f'
down_revision: Union[str, Sequence[str], None] = 'c69f6c526f0d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
