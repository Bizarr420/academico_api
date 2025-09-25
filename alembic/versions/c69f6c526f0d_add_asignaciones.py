"""add asignaciones

Revision ID: c69f6c526f0d
Revises: 9d1f2afd53be
Create Date: 2025-09-23 12:56:13.930253

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c69f6c526f0d'
down_revision: Union[str, Sequence[str], None] = '9d1f2afd53be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
