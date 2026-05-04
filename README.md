# POZO/MGR — Sistema de Gestión de Bombas de Pozo Profundo

## Stack
- Backend: Python + Flask
- Base de datos: SQLite
- Frontend: HTML/JS/CSS (embebido en templates)
- Deploy: Render.com

## Credenciales por defecto
- Usuario: `admin`
- Contraseña: `bombas2024`
- **Cambiar en el primer login desde Datos → Usuarios**

## Deploy en Render

1. Subir este repositorio a GitHub
2. En Render: New → Web Service → conectar el repo
3. Render detecta automáticamente el `render.yaml`
4. El build corre `pip install` + `seed.py` (carga datos iniciales)
5. Listo — la app queda en `https://bombas-mgr.onrender.com`

## Correr localmente

```bash
pip install -r requirements.txt
python seed.py        # primera vez solamente
python app.py
# Abrir http://localhost:5000
```

## Estructura
```
bombas_app/
├── app.py                  # Backend Flask + API REST
├── seed.py                 # Script de carga inicial de datos
├── seed_inventario.json    # Datos iniciales (539 perforaciones)
├── seed_catalogo.json      # Datos iniciales (103 modelos Motorarg)
├── requirements.txt
├── Procfile
├── render.yaml
└── templates/
    ├── login.html
    └── index.html          # App principal (CRUD completo)
```

## API Endpoints

| Método | URL | Descripción |
|--------|-----|-------------|
| GET | /api/perforaciones | Listar todo |
| GET | /api/perforaciones/:id | Detalle |
| POST | /api/perforaciones | Crear nuevo |
| PUT | /api/perforaciones/:id | Editar |
| PATCH | /api/perforaciones/:id/estado | Cambiar estado rápido |
| DELETE | /api/perforaciones/:id | Eliminar (solo admin) |
| GET | /api/catalogo | Listar catálogo |
| POST | /api/import/perforaciones | Importar desde Excel (admin) |
| POST | /api/import/catalogo | Importar catálogo (admin) |
| GET | /api/users | Listar usuarios (admin) |
| POST | /api/users | Crear usuario (admin) |
| DELETE | /api/users/:id | Eliminar usuario (admin) |
| PUT | /api/me/password | Cambiar mi contraseña |
