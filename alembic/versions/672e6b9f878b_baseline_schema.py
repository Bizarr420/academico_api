"""baseline schema

Revision ID: 672e6b9f878b
Revises: 9e16972cb51a
Create Date: 2025-09-13 02:20:33.203805

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '672e6b9f878b'
down_revision: Union[str, Sequence[str], None] = '9e16972cb51a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
