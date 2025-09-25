"""add asignaciones

Revision ID: eca08940efbc
Revises: 5513296ea9dd
Create Date: 2025-09-23 13:34:51.971953

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eca08940efbc'
down_revision: Union[str, Sequence[str], None] = '5513296ea9dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
