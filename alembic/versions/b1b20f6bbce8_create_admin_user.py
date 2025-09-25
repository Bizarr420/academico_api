"""create admin user

Revision ID: b1b20f6bbce8
Revises: 69e0d76d4c8b
Create Date: 2024-03-17 00:00:00.000000

"""

from datetime import date
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b1b20f6bbce8"
down_revision: Union[str, Sequence[str], None] = "69e0d76d4c8b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ADMIN_ROLE_NAME = "admin"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = "$2b$12$UqClPXCr0qq6/lN0c8pGuueS/aaUODsjMCRrvOKvWTYE9mZukYdxK"
ADMIN_NAMES = "Administrador"
ADMIN_LASTNAMES = "General"
ADMIN_SEXO = "M"
ADMIN_BIRTHDATE = date(1990, 1, 1)


def upgrade() -> None:
    """Insert the default admin user."""
    bind = op.get_bind()

    roles = sa.table(
        "roles",
        sa.column("id", sa.Integer),
        sa.column("nombre", sa.String(30)),
    )
    personas = sa.table(
        "personas",
        sa.column("id", sa.Integer),
        sa.column("nombres", sa.String(120)),
        sa.column("apellidos", sa.String(120)),
        sa.column("sexo", sa.String(1)),
        sa.column("fecha_nacimiento", sa.Date),
        sa.column("celular", sa.String(20)),
        sa.column("direccion", sa.String(255)),
    )
    usuarios = sa.table(
        "usuarios",
        sa.column("id", sa.Integer),
        sa.column("persona_id", sa.Integer),
        sa.column("username", sa.String(50)),
        sa.column("password_hash", sa.String(128)),
        sa.column("rol_id", sa.Integer),
        sa.column("estado", sa.String(20)),
    )

    role_id = bind.execute(
        sa.select(roles.c.id).where(roles.c.nombre == ADMIN_ROLE_NAME)
    ).scalar_one_or_none()
    if role_id is None:
        result = bind.execute(sa.insert(roles).values(nombre=ADMIN_ROLE_NAME))
        role_id = result.inserted_primary_key[0]

    existing_user_id = bind.execute(
        sa.select(usuarios.c.id).where(usuarios.c.username == ADMIN_USERNAME)
    ).scalar_one_or_none()
    if existing_user_id is not None:
        return

    persona_id = bind.execute(
        sa.select(personas.c.id).where(
            personas.c.nombres == ADMIN_NAMES,
            personas.c.apellidos == ADMIN_LASTNAMES,
        )
    ).scalar_one_or_none()
    if persona_id is None:
        result = bind.execute(
            sa.insert(personas).values(
                nombres=ADMIN_NAMES,
                apellidos=ADMIN_LASTNAMES,
                sexo=ADMIN_SEXO,
                fecha_nacimiento=ADMIN_BIRTHDATE,
            )
        )
        persona_id = result.inserted_primary_key[0]

    bind.execute(
        sa.insert(usuarios).values(
            persona_id=persona_id,
            username=ADMIN_USERNAME,
            password_hash=ADMIN_PASSWORD_HASH,
            rol_id=role_id,
            estado="ACTIVO",
        )
    )


def downgrade() -> None:
    """Remove the default admin user."""
    bind = op.get_bind()

    roles = sa.table(
        "roles",
        sa.column("id", sa.Integer),
        sa.column("nombre", sa.String(30)),
    )
    personas = sa.table(
        "personas",
        sa.column("id", sa.Integer),
        sa.column("nombres", sa.String(120)),
        sa.column("apellidos", sa.String(120)),
    )
    usuarios = sa.table(
        "usuarios",
        sa.column("id", sa.Integer),
        sa.column("persona_id", sa.Integer),
        sa.column("username", sa.String(50)),
        sa.column("rol_id", sa.Integer),
    )

    persona_id = bind.execute(
        sa.select(usuarios.c.persona_id).where(usuarios.c.username == ADMIN_USERNAME)
    ).scalar_one_or_none()

    bind.execute(sa.delete(usuarios).where(usuarios.c.username == ADMIN_USERNAME))

    if persona_id is not None:
        remaining = bind.execute(
            sa.select(sa.func.count()).select_from(usuarios).where(usuarios.c.persona_id == persona_id)
        ).scalar_one()
        if remaining == 0:
            bind.execute(sa.delete(personas).where(personas.c.id == persona_id))

    role_id = bind.execute(
        sa.select(roles.c.id).where(roles.c.nombre == ADMIN_ROLE_NAME)
    ).scalar_one_or_none()
    if role_id is not None:
        users_with_role = bind.execute(
            sa.select(sa.func.count()).select_from(usuarios).where(usuarios.c.rol_id == role_id)
        ).scalar_one()
        if users_with_role == 0:
            bind.execute(sa.delete(roles).where(roles.c.id == role_id))
