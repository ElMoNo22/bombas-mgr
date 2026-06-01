"""
wsgi.py — arranque seguro para POZO/MGR

Este archivo envuelve la app Flask original (`app.py`) sin tocar su lógica principal.
Usar en producción con: gunicorn wsgi:app

Variables recomendadas en Render:
- SECRET_KEY: generado automáticamente o valor largo aleatorio
- ADMIN_PASSWORD: contraseña segura para reemplazar el admin inicial si sigue usando bombas2024
- ADMIN_USERNAME: opcional, por defecto "admin"
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


def _is_truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _running_on_render() -> bool:
    return bool(os.environ.get("RENDER")) or bool(os.environ.get("RENDER_SERVICE_ID"))


def configure_secret_key() -> None:
    """
    En producción no permite usar la SECRET_KEY vieja/hardcodeada.
    En local permite arrancar con una clave temporal para no trabarte.
    """
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


def configure_session_security() -> None:
    """
    Endurece cookies de sesión.
    SESSION_COOKIE_SECURE se activa en Render porque ahí debería correr por HTTPS.
    """
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=_running_on_render() or _is_truthy(os.environ.get("FORCE_HTTPS_COOKIES")),
        PERMANENT_SESSION_LIFETIME=60 * 60 * 12,  # 12 horas
        MAX_CONTENT_LENGTH=25 * 1024 * 1024,      # 25 MB para evitar cargas gigantes accidentales
    )

    # Render/proxies: ayuda a Flask a entender https real detrás del proxy.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)


def secure_admin_user() -> None:
    """
    Si el usuario admin todavía tiene la contraseña vieja, obliga a rotarla.
    Si existe ADMIN_PASSWORD, la cambia automáticamente.
    Si no existe ADMIN_PASSWORD y detecta la clave vieja en Render, corta el deploy.
    """
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


@app.before_request
def make_session_permanent():
    """
    Hace que la sesión use PERMANENT_SESSION_LIFETIME.
    """
    from flask import session
    session.permanent = True


@app.after_request
def add_security_headers(response):
    """
    Headers defensivos básicos.
    No reemplazan autenticación ni permisos, pero reducen superficie de ataque.
    """
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")

    if response.content_type and "text/html" in response.content_type:
        response.headers.setdefault("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        response.headers.setdefault("Pragma", "no-cache")

    return response


configure_secret_key()
configure_session_security()
secure_admin_user()
