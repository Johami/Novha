
import getpass

from werkzeug.security import generate_password_hash
from email_validator import validate_email, EmailNotValidError

from db import get_sql


def crear_administrador():
    print("\n========== CREAR ADMINISTRADOR NOVHA ==========\n")

    nombre = input("Nombre del administrador: ").strip()
    email = input("Correo electrónico: ").strip().lower()

    if not nombre or not email:
        print("\nError: nombre y correo son obligatorios.")
        return

    try:
        validate_email(email, check_deliverability=False)
    except EmailNotValidError:
        print("\nError: el correo electrónico no es válido.")
        return

    password = getpass.getpass("Contraseña: ")
    confirmacion = getpass.getpass("Confirmar contraseña: ")

    if len(password) < 8:
        print("\nError: la contraseña debe tener al menos 8 caracteres.")
        return

    if password != confirmacion:
        print("\nError: las contraseñas no coinciden.")
        return

    conn = get_sql()

    try:
        existente = conn.execute(
            "SELECT id FROM usuarios WHERE email = ?",
            (email,)
        ).fetchone()

        if existente:
            print("\nError: ya existe una cuenta con ese correo.")
            return

        password_hash = generate_password_hash(password)

        conn.execute(
            """
            INSERT INTO usuarios
                (email, password_hash, nombre, rol, activo)
            VALUES (?, ?, ?, 'admin', 1)
            """,
            (email, password_hash, nombre)
        )

        conn.commit()

        print("\nAdministrador creado correctamente.")
        print(f"Nombre: {nombre}")
        print(f"Correo: {email}")
        print("Rol: admin")
        print("Estado: activo")

    except Exception as error:
        conn.rollback()
        print(f"\nError al crear el administrador: {error}")

    finally:
        conn.close()


if __name__ == "__main__":
    crear_administrador()
