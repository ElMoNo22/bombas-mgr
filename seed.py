"""
seed.py — poblar la base de datos con los datos iniciales
Solo inserta datos si las tablas están vacías — no borra datos existentes.
Se ejecuta en cada deploy de Render pero es seguro.
"""
import json, sqlite3, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from app import init_db, DB_PATH, get_db

print(f"Inicializando DB en: {DB_PATH}")
init_db()  # Crea tablas si no existen, crea usuario admin si no existe

db = get_db()

# ── Solo insertar inventario si la tabla está vacía ──
count_inv = db.execute('SELECT COUNT(*) FROM perforaciones').fetchone()[0]
if count_inv == 0:
    with open('seed_inventario.json', encoding='utf-8') as f:
        inventario = json.load(f)
    fields = ['n_equipo','tag','tag_extraviado','zona','estado','denominacion','calle','entre','y_col',
              'bombeo','marca','modelo','hp','kw','amperes','serie','salida','tazones','largo_mm',
              'ubicacion_actual','notificada_por','relevado_el','candado','tipo_cañeria','mts_cañeria',
              'prof_trabajo_mts','Q_m3h','H_mca','nivel_estatico','nivel_dinamico','fecha_lectura',
              'fecha_notif','observaciones','id_estadio','sap_id']
    placeholders = ','.join(['?']*len(fields))
    cols = ','.join(fields)
    for r in inventario:
        vals = [r.get(f) for f in fields]
        db.execute(f'INSERT INTO perforaciones ({cols}) VALUES ({placeholders})', vals)
    db.commit()
    print(f"✓ {len(inventario)} perforaciones insertadas (primera vez)")
else:
    print(f"✓ Inventario ya existe ({count_inv} registros) — no se sobreescribe")

# ── Solo insertar catálogo si la tabla está vacía ──
count_cat = db.execute('SELECT COUNT(*) FROM catalogo').fetchone()[0]
if count_cat == 0:
    with open('seed_catalogo.json', encoding='utf-8') as f:
        catalogo = json.load(f)
    for r in catalogo:
        db.execute(
            'INSERT INTO catalogo (marca, modelo, para, hp, etapas, descarga, largo_mm, curva_json) VALUES (?,?,?,?,?,?,?,?)',
            (r.get('marca'), r.get('modelo'), r.get('para'), r.get('hp'),
             r.get('etapas'), r.get('descarga'), r.get('largo_mm'),
             json.dumps(r.get('curva', [])))
        )
    db.commit()
    print(f"✓ {len(catalogo)} modelos de catálogo insertados (primera vez)")
else:
    print(f"✓ Catálogo ya existe ({count_cat} modelos) — no se sobreescribe")

db.close()
print("✅ Base de datos lista")
