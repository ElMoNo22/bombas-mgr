"""
seed.py — carga inicial de datos al nuevo esquema
Tablas: bombas, perforaciones, asignaciones, catalogo
Solo inserta si las tablas están vacías.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from app import init_db, DB_PATH, get_db

print(f"DB: {DB_PATH}")
init_db()
db = get_db()

# ── CATALOGO ──
if db.execute('SELECT COUNT(*) FROM catalogo').fetchone()[0] == 0:
    with open('seed_catalogo.json', encoding='utf-8') as f:
        cat = json.load(f)
    for r in cat:
        db.execute('INSERT INTO catalogo (marca,modelo,para,hp,etapas,descarga,largo_mm,curva_json) VALUES (?,?,?,?,?,?,?,?)',
            (r.get('marca'),r.get('modelo'),r.get('para'),r.get('hp'),
             r.get('etapas'),r.get('descarga'),r.get('largo_mm'),json.dumps(r.get('curva',[]))))
    db.commit()
    print(f"✓ {len(cat)} modelos de catálogo")
else:
    print(f"✓ Catálogo ya existe")

# ── BOMBAS ──
if db.execute('SELECT COUNT(*) FROM bombas').fetchone()[0] == 0:
    with open('seed_bombas.json', encoding='utf-8') as f:
        bombas = json.load(f)
    fields = ['n_equipo','tag','tag_extraviado','marca','modelo','hp','kw','amperes',
              'serie','peso_kg','largo_mm','salida','tazones','sap_id','id_estadio','observaciones']
    for r in bombas:
        vals = [r.get(f) for f in fields]
        db.execute(f'INSERT INTO bombas ({",".join(fields)}) VALUES ({",".join(["?"]*len(fields))})', vals)
    db.commit()
    print(f"✓ {len(bombas)} bombas")
else:
    print(f"✓ Bombas ya existen")

# ── PERFORACIONES ──
if db.execute('SELECT COUNT(*) FROM perforaciones').fetchone()[0] == 0:
    with open('seed_perforaciones.json', encoding='utf-8') as f:
        perfs = json.load(f)
    fields = ['calle','entre','y_col','zona','bombeo','denominacion','prof_trabajo_mts',
              'tipo_cañeria','mts_cañeria','nivel_estatico','nivel_dinamico','Q_m3h','H_mca','candado']
    for r in perfs:
        vals = [r.get(f) for f in fields]
        db.execute(f'INSERT INTO perforaciones ({",".join(fields)}) VALUES ({",".join(["?"]*len(fields))})', vals)
    db.commit()
    print(f"✓ {len(perfs)} perforaciones")
else:
    print(f"✓ Perforaciones ya existen")

# ── ASIGNACIONES ──
if db.execute('SELECT COUNT(*) FROM asignaciones').fetchone()[0] == 0:
    with open('seed_asignaciones.json', encoding='utf-8') as f:
        asigs = json.load(f)

    # Build lookup maps
    bombas_map = {r['n_equipo']: r['id'] for r in
                  [dict(row) for row in db.execute('SELECT id, n_equipo FROM bombas').fetchall()]}
    perfs_raw = db.execute('SELECT id, calle, entre, y_col FROM perforaciones').fetchall()
    perfs_map = {}
    for p in perfs_raw:
        key = f"{p['calle']}|{p['entre'] or '0'}|{p['y_col'] or '0'}"
        perfs_map[key] = p['id']

    inserted = 0
    skipped = 0
    for a in asigs:
        bid = bombas_map.get(a.get('n_equipo'))
        pid = perfs_map.get(a.get('perf_key'))
        if not bid or not pid:
            skipped += 1
            continue
        db.execute('''INSERT INTO asignaciones
            (bomba_id, perforacion_id, estado, fecha_montaje, fecha_desmontaje, notificada_por, notas)
            VALUES (?,?,?,?,?,?,?)''',
            (bid, pid, a.get('estado','Desmontado'), a.get('fecha_montaje'),
             a.get('fecha_desmontaje'), a.get('notificada_por'), a.get('notas')))
        inserted += 1
    db.commit()
    print(f"✓ {inserted} asignaciones ({skipped} sin match)")
else:
    print(f"✓ Asignaciones ya existen")

db.close()
print("✅ DB lista")
