# POZO/MGR — Sistema de Gestión de Bombas de Pozo Profundo

## Stack

- Backend: Python + Flask
- Base de datos: SQLite / Turso
- Frontend: HTML/JS/CSS embebido en templates
- Deploy: Render.com

## Seguridad inicial

Esta versión no recomienda publicar credenciales por defecto.

En Render configurá estas variables de entorno:

| Variable | Uso |
|---|---|
| `SECRET_KEY` | Clave secreta de Flask. En Render puede generarse con `generateValue`. |
| `ADMIN_USERNAME` | Usuario admin inicial. Por defecto: `admin`. |
| `ADMIN_PASSWORD` | Contraseña segura para el admin inicial. No debe subirse al repo. |
| `DB_PATH` | Ruta de base de datos si se usa SQLite local/persistente. |

Si el usuario `admin` todavía usa la contraseña vieja inicial, el arranque seguro (`wsgi.py`) intenta reemplazarla con `ADMIN_PASSWORD`.
En producción, si no configuraste `ADMIN_PASSWORD`, el deploy se corta para evitar dejar una clave conocida.

## Deploy en Render

1. Subir este repositorio a GitHub.
2. En Render: New → Web Service → conectar el repo.
3. Render detecta el `render.yaml`.
4. Configurar `ADMIN_PASSWORD` como variable secreta.
5. El build corre `pip install` + `seed.py`.
6. La app arranca con `gunicorn wsgi:app`.

## Correr localmente

```bash
pip install -r requirements.txt
python seed.py        # primera vez solamente
python app.py
# Abrir http://localhost:5000
```

Para probar el arranque seguro local:

```bash
set SECRET_KEY=dev-secret-largo
set ADMIN_PASSWORD=una-clave-segura
gunicorn wsgi:app
```

En Windows PowerShell:

```powershell
$env:SECRET_KEY="dev-secret-largo"
$env:ADMIN_PASSWORD="una-clave-segura"
python app.py
```

## Estructura

```text
bombas_app/
├── app.py                  # Backend Flask + API REST
├── wsgi.py                 # Arranque seguro para producción
├── seed.py                 # Script de carga inicial de datos
├── seed_inventario.json    # Datos iniciales
├── seed_catalogo.json      # Datos iniciales
├── requirements.txt
├── Procfile
├── render.yaml
└── templates/
    ├── login.html
    └── index.html          # App principal
```

## API Endpoints

| Método | URL | Descripción |
|--------|-----|-------------|
| GET | /api/perforaciones | Listar todo |
| GET | /api/perforaciones/:id | Detalle |
| POST | /api/perforaciones | Crear nuevo |
| PUT | /api/perforaciones/:id | Editar |
| PATCH | /api/perforaciones/:id/estado | Cambiar estado rápido |
| DELETE | /api/perforaciones/:id | Eliminar solo admin |
| GET | /api/catalogo | Listar catálogo |
| POST | /api/import/perforaciones | Importar desde Excel solo admin |
| POST | /api/import/catalogo | Importar catálogo solo admin |
| GET | /api/users | Listar usuarios solo admin |
| POST | /api/users | Crear usuario solo admin |
| DELETE | /api/users/:id | Eliminar usuario solo admin |
| PUT | /api/me/password | Cambiar mi contraseña |
