"""
patch_app.py — Agregar blueprints CelMGR y TeleMGR al app.py existente
Correr UNA VEZ desde la raíz del repo:
    python patch_app.py
"""
import re, shutil, os

APP_FILE = 'app.py'
BACKUP   = 'app.py.bak'

# Líneas a insertar DESPUÉS de los imports existentes y ANTES de app = Flask(...)
IMPORT_LINES = [
    'from blueprints.celulares import cel_bp',
    'from blueprints.telemetria import tele_bp',
]

# Líneas a insertar DESPUÉS de app.secret_key = ...
REGISTER_LINES = [
    'app.register_blueprint(cel_bp)',
    'app.register_blueprint(tele_bp)',
]

def main():
    if not os.path.exists(APP_FILE):
        print(f"ERROR: No se encontró {APP_FILE}")
        return

    # Backup
    shutil.copy(APP_FILE, BACKUP)
    print(f"✓ Backup creado: {BACKUP}")

    with open(APP_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Verificar que no esté ya parcheado
    if 'from blueprints.celulares import cel_bp' in content:
        print("⚠ Ya está parcheado — no se hicieron cambios")
        return

    # 1. Insertar imports antes de "app = Flask(__name__)"
    app_flask_pattern = r'(app = Flask\(__name__\))'
    imports_str = '\n'.join(IMPORT_LINES) + '\n\n'
    content = re.sub(app_flask_pattern, imports_str + r'\1', content, count=1)

    # 2. Insertar register_blueprint después de app.secret_key = ...
    secret_key_pattern = r"(app\.secret_key\s*=\s*os\.environ\.get\([^\n]+\))"
    registers_str = r'\1\n' + '\n'.join(REGISTER_LINES)
    content = re.sub(secret_key_pattern, registers_str, content, count=1)

    with open(APP_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

    # Verificar
    if 'from blueprints.celulares import cel_bp' in content and \
       'app.register_blueprint(cel_bp)' in content:
        print("✓ app.py parcheado correctamente")
        print("  → Imports agregados antes de app = Flask(__name__)")
        print("  → register_blueprint agregado después de app.secret_key")
    else:
        print("ERROR: El patch no funcionó — restaurando backup")
        shutil.copy(BACKUP, APP_FILE)

if __name__ == '__main__':
    main()
