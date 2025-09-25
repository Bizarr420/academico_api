"""add gestion to asignacion_docente

Revision ID: a68ab8d464ac
Revises: eca08940efbc
Create Date: 2025-09-23 13:47:03.296088

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a68ab8d464ac'
down_revision: Union[str, Sequence[str], None] = 'eca08940efbc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
