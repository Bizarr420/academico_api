"""merge heads

Revision ID: 0e980b45a202
Revises: ac78685aeeeb, f12a9fba7dfd
Create Date: 2025-09-24 13:05:10.680140

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e980b45a202'
down_revision: Union[str, Sequence[str], None] = ('ac78685aeeeb', 'f12a9fba7dfd')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
