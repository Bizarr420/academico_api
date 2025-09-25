"""add codigo to materias

Revision ID: 5513296ea9dd
Revises: 32f4ac4e13e9
Create Date: 2025-09-23 13:12:30.703205

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5513296ea9dd'
down_revision: Union[str, Sequence[str], None] = '32f4ac4e13e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
