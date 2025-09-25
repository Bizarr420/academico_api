"""add etiqueta to cursos

Revision ID: 32f4ac4e13e9
Revises: e95e3c9706e2
Create Date: 2025-09-23 13:09:54.647822

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '32f4ac4e13e9'
down_revision: Union[str, Sequence[str], None] = 'e95e3c9706e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
