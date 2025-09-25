"""lo que siga

Revision ID: 69e0d76d4c8b
Revises: 0e980b45a202
Create Date: 2025-09-24 13:12:05.043414

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '69e0d76d4c8b'
down_revision: Union[str, Sequence[str], None] = '0e980b45a202'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
