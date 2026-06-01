"""
sitecustomize.py — carga automática de POZO+

Python importa este archivo automáticamente al iniciar.
Sirve como puente para cargar pozo_plus.py aunque Render esté arrancando con app:app
en lugar de wsgi:app.
"""

try:
    import pozo_plus  # noqa: F401
    print("✓ POZO+ cargado desde sitecustomize.py")
except Exception as exc:
    # No rompemos el arranque de la app por una mejora opcional.
    print(f"⚠ POZO+ no pudo cargarse desde sitecustomize.py: {exc}")
