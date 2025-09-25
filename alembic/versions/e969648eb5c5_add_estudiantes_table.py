"""add estudiantes table

Revision ID: e969648eb5c5
Revises: f331211262dc
Create Date: 2025-09-23 14:50:25.881868

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e969648eb5c5'
down_revision: Union[str, Sequence[str], None] = 'f331211262dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
