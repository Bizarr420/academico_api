"""seed vistas y rol_vistas

Revision ID: 7034219973dc
Revises: ce370f07d10f
Create Date: 2025-09-29 20:19:07.817715

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7034219973dc'
down_revision: Union[str, Sequence[str], None] = 'ce370f07d10f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
