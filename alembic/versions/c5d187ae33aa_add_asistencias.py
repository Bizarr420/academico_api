"""add asistencias

Revision ID: c5d187ae33aa
Revises: 95fa3d7ba006
Create Date: 2025-09-23 18:02:58.699588

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5d187ae33aa'
down_revision: Union[str, Sequence[str], None] = '95fa3d7ba006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
