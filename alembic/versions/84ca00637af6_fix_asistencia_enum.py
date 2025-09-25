"""fix asistencia enum

Revision ID: 84ca00637af6
Revises: c5d187ae33aa
Create Date: 2025-09-23 18:10:53.153167

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '84ca00637af6'
down_revision: Union[str, Sequence[str], None] = 'c5d187ae33aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
