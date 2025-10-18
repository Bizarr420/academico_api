# Script para resetear la contraseña de un usuario a un valor nuevo y seguro
# Uso: Ejecuta este script dentro del entorno virtual activado

import sys
from getpass import getpass
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import Usuario
from app.core.security import hash_password


def reset_password(username: str, new_password: str):
    db: Session = SessionLocal()
    user = db.query(Usuario).filter(Usuario.username == username).first()
    if not user:
        print(f"Usuario '{username}' no encontrado.")
        return
    user.password_hash = hash_password(new_password)
    db.commit()
    print(f"Contraseña de '{username}' actualizada correctamente.")
    db.close()


def main():
    if len(sys.argv) < 2:
        print("Uso: python reset_user_password.py <username>")
        return
    username = sys.argv[1]
    new_password = getpass(f"Nueva contraseña para {username}: ")
    if len(new_password) > 72:
        print("Advertencia: solo los primeros 72 caracteres serán usados.")
    reset_password(username, new_password)


if __name__ == "__main__":
    main()
