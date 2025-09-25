"""add etiqueta to niveles

Revision ID: e95e3c9706e2
Revises: dba2a6a3f82f
Create Date: 2025-09-23 13:07:52.905029

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e95e3c9706e2'
down_revision: Union[str, Sequence[str], None] = 'dba2a6a3f82f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
