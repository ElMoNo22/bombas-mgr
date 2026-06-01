"""
wsgi.py — arranque seguro + carga modular POZO+

Usar en producción con:
    gunicorn wsgi:app

Este archivo:
- Carga la app original desde app.py
- Aplica seguridad básica de sesión/cookies
- Carga las mejoras POZO+ desde pozo_plus.py
"""

import os
import secrets
import warnings

from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash, generate_password_hash

import app as original_app


DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "bombas2024"

app = original_app.app


def _is_truthy(value):
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _running_on_render():
    return bool(os.environ.get("RENDER")) or bool(os.environ.get("RENDER_SERVICE_ID"))


def configure_secret_key():
    secret_key = os.environ.get("SECRET_KEY", "").strip()

    if not secret_key:
        if _running_on_render():
            raise RuntimeError(
                "Falta SECRET_KEY en variables de entorno. "
                "En Render agregá SECRET_KEY con Generate Value."
            )
        secret_key = secrets.token_urlsafe(48)
        warnings.warn(
            "SECRET_KEY no configurada. Usando una clave temporal solo para desarrollo local.",
            RuntimeWarning,
        )

    if secret_key == "bombas-mgr-secret-2024":
        raise RuntimeError(
            "SECRET_KEY insegura detectada. Cambiala en Render por un valor secreto."
        )

    app.secret_key = secret_key


def configure_session_security():
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=_running_on_render() or _is_truthy(os.environ.get("FORCE_HTTPS_COOKIES")),
        PERMANENT_SESSION_LIFETIME=60 * 60 * 12,
        MAX_CONTENT_LENGTH=25 * 1024 * 1024,
    )
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)


def secure_admin_user():
    admin_username = os.environ.get("ADMIN_USERNAME", DEFAULT_ADMIN_USERNAME).strip() or DEFAULT_ADMIN_USERNAME
    admin_password = os.environ.get("ADMIN_PASSWORD", "").strip()

    conn = original_app.get_db()
    try:
        cur = conn.execute("SELECT * FROM users WHERE username = ?", (admin_username,))
        user = original_app.fetchone_dict(cur)

        if user:
            uses_default_password = check_password_hash(user["password_hash"], DEFAULT_ADMIN_PASSWORD)

            if uses_default_password:
                if not admin_password or admin_password == DEFAULT_ADMIN_PASSWORD:
                    if _running_on_render():
                        raise RuntimeError(
                            f"El usuario {admin_username!r} sigue usando la contraseña inicial. "
                            "Agregá ADMIN_PASSWORD en Render con una contraseña segura."
                        )
                    warnings.warn(
                        f"El usuario {admin_username!r} sigue usando la contraseña inicial.",
                        RuntimeWarning,
                    )
                    return

                conn.execute(
                    "UPDATE users SET password_hash=? WHERE id=?",
                    (generate_password_hash(admin_password), user["id"]),
                )
                original_app.db_commit(conn)
                print(f"✓ Contraseña inicial de {admin_username!r} rotada automáticamente.")

        else:
            if admin_password:
                conn.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    (admin_username, generate_password_hash(admin_password), "admin"),
                )
                original_app.db_commit(conn)
                print(f"✓ Usuario admin {admin_username!r} creado desde variables de entorno.")
    finally:
        conn.close()


configure_secret_key()
configure_session_security()
secure_admin_user()

# Carga las mejoras modulares: APIs + inyección visual.
import pozo_plus  # noqa: E402,F401
