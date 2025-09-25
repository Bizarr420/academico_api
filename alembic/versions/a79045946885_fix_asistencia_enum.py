"""fix asistencia enum

Revision ID: a79045946885
Revises: 84ca00637af6
Create Date: 2025-09-23 18:20:25.054901

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a79045946885'
down_revision: Union[str, Sequence[str], None] = '84ca00637af6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
