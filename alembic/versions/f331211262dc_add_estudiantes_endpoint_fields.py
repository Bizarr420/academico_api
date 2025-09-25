"""add estudiantes endpoint fields

Revision ID: f331211262dc
Revises: a68ab8d464ac
Create Date: 2025-09-23 14:45:55.576726

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f331211262dc'
down_revision: Union[str, Sequence[str], None] = 'a68ab8d464ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
