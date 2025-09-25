"""add matriculas

Revision ID: 95fa3d7ba006
Revises: e969648eb5c5
Create Date: 2025-09-23 16:53:45.419706

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '95fa3d7ba006'
down_revision: Union[str, Sequence[str], None] = 'e969648eb5c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
