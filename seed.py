"""
seed.py — carga inicial a Turso o SQLite
Solo inserta si las tablas están vacías.
Usa executemany para bulk inserts eficientes.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from app import init_db, get_db, db_commit, fetchone_dict, fetchall_dicts

print("Inicializando DB...")
init_db()
db = get_db()

def count(table):
    cur = db.execute(f'SELECT COUNT(*) as n FROM {table}')
    r = fetchone_dict(cur)
    return r['n'] if r else 0

# ── CATALOGO ──
if count('catalogo') == 0:
    with open('seed_catalogo.json', encoding='utf-8') as f:
        cat = json.load(f)
    sql = 'INSERT INTO catalogo (marca,modelo,para,hp,etapas,descarga,largo_mm,curva_json) VALUES (?,?,?,?,?,?,?,?)'
    params = [(r.get('marca'),r.get('modelo'),r.get('para'),r.get('hp'),
               r.get('etapas'),r.get('descarga'),r.get('largo_mm'),json.dumps(r.get('curva',[])))
              for r in cat]
    db.executemany(sql, params)
    db_commit(db)
    print(f"✓ {len(cat)} modelos de catálogo")
else:
    print(f"✓ Catálogo ya existe ({count('catalogo')} modelos)")

# ── BOMBAS ──
if count('bombas') == 0:
    with open('seed_bombas.json', encoding='utf-8') as f:
        bombas = json.load(f)
    fields = ['n_equipo','tag','tag_extraviado','marca','modelo','hp','kw','amperes',
              'serie','peso_kg','largo_mm','salida','tazones','sap_id','id_estadio','observaciones']
    sql = f'INSERT INTO bombas ({",".join(fields)}) VALUES ({",".join(["?"]*len(fields))})'
    params = [[r.get(f) for f in fields] for r in bombas]
    db.executemany(sql, params)
    db_commit(db)
    print(f"✓ {len(bombas)} bombas")
else:
    print(f"✓ Bombas ya existen ({count('bombas')})")

# ── PERFORACIONES ──
if count('perforaciones') == 0:
    with open('seed_perforaciones.json', encoding='utf-8') as f:
        perfs = json.load(f)
    fields = ['calle','entre','y_col','zona','bombeo','denominacion','prof_trabajo_mts',
              'tipo_cañeria','mts_cañeria','nivel_estatico','nivel_dinamico','Q_m3h','H_mca','candado']
    sql = f'INSERT INTO perforaciones ({",".join(fields)}) VALUES ({",".join(["?"]*len(fields))})'
    params = [[r.get(f) for f in fields] for r in perfs]
    db.executemany(sql, params)
    db_commit(db)
    print(f"✓ {len(perfs)} perforaciones")
else:
    print(f"✓ Perforaciones ya existen ({count('perforaciones')})")

# ── ASIGNACIONES ──
if count('asignaciones') == 0:
    with open('seed_asignaciones.json', encoding='utf-8') as f:
        asigs = json.load(f)

    cur = db.execute('SELECT id, n_equipo FROM bombas')
    bombas_map = {r['n_equipo']: r['id'] for r in fetchall_dicts(cur)}
    cur2 = db.execute('SELECT id, calle, entre, y_col FROM perforaciones')
    perfs_map = {}
    for p in fetchall_dicts(cur2):
        key = f"{p['calle']}|{p['entre'] or '0'}|{p['y_col'] or '0'}"
        perfs_map[key] = p['id']

    sql = '''INSERT INTO asignaciones
        (bomba_id,perforacion_id,estado,fecha_montaje,fecha_desmontaje,notificada_por,notas)
        VALUES (?,?,?,?,?,?,?)'''
    params = []
    skipped = 0
    for a in asigs:
        bid = bombas_map.get(a.get('n_equipo'))
        pid = perfs_map.get(a.get('perf_key'))
        if not bid or not pid:
            skipped += 1
            continue
        params.append((bid, pid, a.get('estado','Desmontado'), a.get('fecha_montaje'),
                       a.get('fecha_desmontaje'), a.get('notificada_por'), a.get('notas')))

    db.executemany(sql, params)
    db_commit(db)
    print(f"✓ {len(params)} asignaciones ({skipped} sin match)")
else:
    print(f"✓ Asignaciones ya existen ({count('asignaciones')})")

# ── FIX: doble Montado ──
cur = db.execute('''
    SELECT perforacion_id FROM asignaciones
    WHERE estado='Montado' GROUP BY perforacion_id HAVING COUNT(*)>1
''')
probs = fetchall_dicts(cur)
fixed = 0
for p in probs:
    pid = p['perforacion_id']
    cur2 = db.execute('''
        SELECT id FROM asignaciones WHERE perforacion_id=? AND estado='Montado'
        ORDER BY CASE WHEN COALESCE(fecha_desmontaje,fecha_montaje) IS NULL THEN 1 ELSE 0 END,
        COALESCE(fecha_desmontaje,fecha_montaje) DESC, id DESC
    ''', (pid,))
    montados = fetchall_dicts(cur2)
    for row in montados[1:]:
        db.execute("UPDATE asignaciones SET estado='Desmontado' WHERE id=?", (row['id'],))
        fixed += 1

if fixed:
    db_commit(db)
    print(f"✓ {fixed} asignaciones duplicadas corregidas")

db.close()
print("✅ DB lista")
