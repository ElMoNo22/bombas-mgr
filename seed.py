"""
seed.py — poblar la base de datos con los datos iniciales
Ejecutar una sola vez: python seed.py
"""
import json, sqlite3, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from app import init_db, DB_PATH, get_db

# Cargar inventario
with open('seed_inventario.json', encoding='utf-8') as f:
    inventario = json.load(f)

# Cargar catálogo
with open('seed_catalogo.json', encoding='utf-8') as f:
    catalogo = json.load(f)

print(f"Inicializando DB en: {DB_PATH}")
init_db()

db = get_db()

# Limpiar e insertar inventario
db.execute('DELETE FROM perforaciones')
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
print(f"✓ {len(inventario)} perforaciones insertadas")

# Limpiar e insertar catálogo
db.execute('DELETE FROM catalogo')
for r in catalogo:
    db.execute(
        'INSERT INTO catalogo (marca, modelo, para, hp, etapas, descarga, largo_mm, curva_json) VALUES (?,?,?,?,?,?,?,?)',
        (r.get('marca'), r.get('modelo'), r.get('para'), r.get('hp'),
         r.get('etapas'), r.get('descarga'), r.get('largo_mm'),
         json.dumps(r.get('curva', [])))
    )
print(f"✓ {len(catalogo)} modelos de catálogo insertados")

db.commit()
db.close()
print("✅ Base de datos inicializada correctamente")
print(f"   Usuario admin: admin / bombas2024")
print(f"   Cambiá la contraseña en el primer login")
