"""Local authentication with hashed passwords and revocable sessions."""

import hashlib
import hmac
import os
import secrets
import smtplib
import time
from email.message import EmailMessage

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from .storage import database

router = APIRouter(prefix="/api", tags=["Accounts"])


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    value = hashlib.scrypt(
        password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1
    )
    return f"{salt}:{value.hex()}"


def check_password(password: str, stored: str) -> bool:
    return hmac.compare_digest(hash_password(password, stored.split(":")[0]), stored)


def normalize_email(email: str) -> str:
    email = email.strip().lower()
    if (
        "@" not in email
        or "." not in email.rsplit("@", 1)[-1]
        or len(email) > 254
        or any(character.isspace() for character in email)
    ):
        raise HTTPException(422, "Correo inválido.")
    return email


def public_user(row) -> dict:
    return {
        "correo": row["email"],
        "nombre": row["first_name"],
        "appat": row["paternal_name"],
        "apmat": row["maternal_name"],
        "telefono": row["phone"],
        "departamento": row["department"],
        "notif": bool(row["notifications"]),
        "rol": row["role"],
    }


def bootstrap_admin():
    with database() as connection:
        if connection.execute("SELECT 1 FROM users LIMIT 1").fetchone():
            return
        email = normalize_email(os.environ["ADMIN_EMAIL"])
        password = os.environ["ADMIN_PASSWORD"]
        if len(password) < 12:
            raise RuntimeError("ADMIN_PASSWORD must contain at least 12 characters.")
        connection.execute(
            "INSERT INTO users(email, password_hash, first_name, role) "
            "VALUES (?, ?, ?, 'admin')",
            (email, hash_password(password), "Administrador"),
        )


def session_user(token: str):
    with database() as connection:
        return connection.execute(
            "SELECT users.* FROM sessions JOIN users USING(email) "
            "WHERE token_hash=? AND expires_at>?",
            (digest(token), time.time()),
        ).fetchone()


def current_user(request: Request):
    header = request.headers.get("Authorization", "")
    token = (
        header[7:]
        if header.startswith("Bearer ")
        else request.cookies.get("dof_session", "")
    )
    row = session_user(token)
    if row is None:
        raise HTTPException(401, "Inicia sesión para continuar.")
    return row


def admin_user(user=Depends(current_user)):
    if user["role"] != "admin":
        raise HTTPException(403, "Se requieren permisos de administrador.")
    return user


def rate_limit(bucket: str, limit: int, window: int):
    now = time.time()
    with database() as connection:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("DELETE FROM attempts WHERE occurred_at<?", (now - 3600,))
        count = connection.execute(
            "SELECT COUNT(*) FROM attempts WHERE bucket=? AND occurred_at>?",
            (bucket, now - window),
        ).fetchone()[0]
        if count >= limit:
            raise HTTPException(429, "Demasiados intentos. Espera unos minutos.")
        connection.execute("INSERT INTO attempts VALUES (?, ?)", (bucket, now))


class EmailInput(BaseModel):
    email: str = Field(alias="correo", max_length=254)


class LoginInput(EmailInput):
    password: str = Field(alias="contraseña", max_length=128)
    keep_session: bool = Field(default=False, alias="keepsesion")


class TokenInput(BaseModel):
    token: str = Field(max_length=256)


class UserInput(EmailInput):
    first_name: str = Field(alias="nombre", min_length=1, max_length=100)
    paternal_name: str = Field(default="", alias="appat", max_length=100)
    maternal_name: str = Field(default="", alias="apmat", max_length=100)
    phone: str = Field(default="", alias="telefono", max_length=30)
    department: str = Field(default="", alias="departamento", max_length=100)
    notifications: bool = Field(default=True, alias="notif")


class RegistrationInput(UserInput):
    password: str = Field(alias="contraseña", min_length=8, max_length=128)


class CodeInput(EmailInput):
    code: str = Field(alias="codigo", pattern=r"^\d{6}$")


class PasswordInput(EmailInput):
    password: str = Field(alias="contraseña", min_length=8, max_length=128)
    reset_token: str = Field(min_length=20, max_length=256)


@router.post("/login")
def login(payload: LoginInput, request: Request):
    from fastapi.responses import JSONResponse

    email = normalize_email(payload.email)
    rate_limit(f"login:{email}", 10, 300)
    rate_limit(f"login-ip:{request.client.host}", 60, 300)
    with database() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE email=?", (email,)
        ).fetchone()
        stored = row["password_hash"] if row else hash_password("unused-password")
        if not check_password(payload.password, stored) or row is None:
            raise HTTPException(401, "Correo o contraseña incorrectos.")
        token = secrets.token_urlsafe(32)
        lifetime = 604800 if payload.keep_session else 43200
        connection.execute("DELETE FROM sessions WHERE expires_at<?", (time.time(),))
        connection.execute(
            "INSERT INTO sessions VALUES (?, ?, ?)",
            (digest(token), email, time.time() + lifetime),
        )
    response = JSONResponse({"token": token, "user": public_user(row)})
    response.set_cookie(
        "dof_session", token, httponly=True, samesite="strict", max_age=lifetime
    )
    return response


@router.post("/logout")
def logout(request: Request, user=Depends(current_user)):
    from fastapi.responses import JSONResponse

    token = request.headers.get("Authorization", "").removeprefix(
        "Bearer "
    ) or request.cookies.get("dof_session", "")
    with database() as connection:
        connection.execute("DELETE FROM sessions WHERE token_hash=?", (digest(token),))
    response = JSONResponse({"message": "Sesión cerrada."})
    response.delete_cookie("dof_session")
    return response


@router.post("/validar_token")
def validate_token(payload: TokenInput):
    return {"valid": session_user(payload.token) is not None}


@router.post("/datos_user")
def user_details(correo: str, user=Depends(current_user)):
    email = normalize_email(correo)
    if user["email"] != email and user["role"] != "admin":
        raise HTTPException(403, "No puedes consultar ese usuario.")
    with database() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE email=?", (email,)
        ).fetchone()
    if row is None:
        raise HTTPException(404, "Usuario no encontrado.")
    return [public_user(row)]


@router.post("/usuarios")
def list_users(user=Depends(admin_user)):
    with database() as connection:
        return [
            public_user(row)
            for row in connection.execute("SELECT * FROM users ORDER BY first_name")
        ]


@router.post("/registro", status_code=201)
def register(payload: RegistrationInput, user=Depends(admin_user)):
    email = normalize_email(payload.email)
    with database() as connection:
        if connection.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
            raise HTTPException(400, "El correo ya está registrado.")
        connection.execute(
            "INSERT INTO users(email, password_hash, first_name, paternal_name, "
            "maternal_name, phone, department, notifications) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                email,
                hash_password(payload.password),
                payload.first_name,
                payload.paternal_name,
                payload.maternal_name,
                payload.phone,
                payload.department,
                payload.notifications,
            ),
        )
    return {"message": "Usuario registrado."}


@router.post("/actualizar_user")
def update_user(payload: UserInput, user=Depends(current_user)):
    email = normalize_email(payload.email)
    if user["email"] != email and user["role"] != "admin":
        raise HTTPException(403, "No puedes modificar ese usuario.")
    with database() as connection:
        cursor = connection.execute(
            "UPDATE users SET first_name=?, paternal_name=?, maternal_name=?, "
            "phone=?, department=?, notifications=? WHERE email=?",
            (
                payload.first_name,
                payload.paternal_name,
                payload.maternal_name,
                payload.phone,
                payload.department,
                payload.notifications,
                email,
            ),
        )
        if not cursor.rowcount:
            raise HTTPException(404, "Usuario no encontrado.")
    return {"message": "Datos actualizados."}


@router.delete("/delete_user")
def delete_user(correo: str, user=Depends(admin_user)):
    email = normalize_email(correo)
    if email == user["email"]:
        raise HTTPException(400, "No puedes eliminar tu propia cuenta.")
    with database() as connection:
        connection.execute("DELETE FROM users WHERE email=?", (email,))
    return {"message": "Usuario eliminado."}


@router.post("/solicitar_codigo")
def request_code(payload: EmailInput):
    email = normalize_email(payload.email)
    rate_limit(f"reset:{email}", 3, 600)
    with database() as connection:
        row = connection.execute(
            "SELECT 1 FROM users WHERE email=?", (email,)
        ).fetchone()
        if row:
            code = f"{secrets.randbelow(1000000):06d}"
            connection.execute(
                "INSERT OR REPLACE INTO resets VALUES (?, ?, ?, 0, NULL)",
                (email, hash_password(code), time.time() + 600),
            )
            message = EmailMessage()
            message["From"] = "noreply@dof.local"
            message["To"] = email
            message["Subject"] = "Código de recuperación de CapiDOFChat"
            message.set_content(
                f"Tu código de recuperación es {code}. Caduca en 10 minutos."
            )
            try:
                with smtplib.SMTP(
                    os.getenv("SMTP_HOST", "mailpit"),
                    int(os.getenv("SMTP_PORT", "1025")),
                    timeout=10,
                ) as client:
                    client.send_message(message)
            except OSError as error:
                raise HTTPException(
                    503, "El buzón local no está disponible."
                ) from error
    return {"message": "Si la cuenta existe, recibirás el código en el buzón local."}


@router.post("/validar_codigo")
def validate_code(payload: CodeInput):
    email = normalize_email(payload.email)
    valid = False
    token = secrets.token_urlsafe(32)
    with database() as connection:
        connection.execute("BEGIN IMMEDIATE")
        row = connection.execute(
            "SELECT * FROM resets WHERE email=?", (email,)
        ).fetchone()
        if (
            row
            and row["expires_at"] > time.time()
            and row["attempts"] < 5
            and not row["token_hash"]
        ):
            valid = check_password(payload.code, row["code_hash"])
            connection.execute(
                "UPDATE resets SET attempts=attempts+1, token_hash=? WHERE email=?",
                (digest(token) if valid else None, email),
            )
    if not valid:
        raise HTTPException(400, "Código inválido o vencido.")
    return {"reset_token": token}


@router.post("/actualizar_password")
def change_password(payload: PasswordInput):
    email = normalize_email(payload.email)
    with database() as connection:
        connection.execute("BEGIN IMMEDIATE")
        row = connection.execute(
            "SELECT * FROM resets WHERE email=? AND token_hash=? AND expires_at>?",
            (email, digest(payload.reset_token), time.time()),
        ).fetchone()
        if row is None:
            raise HTTPException(400, "La autorización de recuperación no es válida.")
        connection.execute(
            "UPDATE users SET password_hash=? WHERE email=?",
            (hash_password(payload.password), email),
        )
        connection.execute("DELETE FROM resets WHERE email=?", (email,))
        connection.execute("DELETE FROM sessions WHERE email=?", (email,))
    return {"message": "Contraseña actualizada."}
