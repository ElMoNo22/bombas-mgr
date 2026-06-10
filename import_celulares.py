"""
import_celulares.py - Import masivo desde Excel a Turso
Versión optimizada: usa batch requests para velocidad
"""
import os, re, sys, json, datetime
import urllib.request

# Descargar turso.py si no existe localmente
if not os.path.exists('turso.py'):
    print("Descargando turso.py...")
    url = "https://raw.githubusercontent.com/ElMoNo22/bombas-mgr/main/turso.py"
    with urllib.request.urlopen(url) as r:
        open('turso.py','wb').write(r.read())

try:
    import openpyxl
except ImportError:
    os.system("pip install openpyxl -q")
    import openpyxl

import turso

EXCEL_PATH = "celus.xlsx"

# ── Helpers ──────────────────────────────────────────────────────────────────

def clean_str(v):
    if v is None: return None
    s = str(v).strip()
    return s if s and s.lower() not in ('none','nan') else None

def clean_imei(v):
    if v is None: return None
    s = str(v).strip()
    if 'e+' in s.lower() or 'e-' in s.lower():
        try: s = str(int(float(s)))
        except: pass
    if s.endswith('.0'): s = s[:-2]
    s = re.sub(r'[^0-9]', '', s)
    return s if len(s) >= 10 else None

def clean_numero(v):
    if v is None: return None
    s = str(v).strip()
    if s.endswith('.0'): s = s[:-2]
    s = re.sub(r'[^0-9]', '', s)
    return s if len(s) >= 6 else None

def clean_fecha(v):
    if v is None: return None
    if isinstance(v, (datetime.date, datetime.datetime)):
        return v.strftime('%Y-%m-%d')
    s = str(v).strip()
    m = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', s)
    if m: return f"{m.group(3)}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}"
    try:
        n = float(s)
        if 30000 < n < 60000:
            d = datetime.datetime(1899,12,30) + datetime.timedelta(days=n)
            return d.strftime('%Y-%m-%d')
    except: pass
    return None

def clean_legajo(v):
    if v is None: return None
    s = str(v).strip()
    if s.endswith('.0'): s = s[:-2]
    s = re.sub(r'[^0-9]', '', s)
    return s if s else None

def detect_marca(modelo):
    if not modelo: return 'Desconocida'
    m = modelo.lower()
    if 'samsung' in m: return 'Samsung'
    if 'motorola' in m or 'moto' in m: return 'Motorola'
    if 'huawei' in m: return 'Huawei'
    if 'lg ' in m or m.startswith('lg'): return 'LG'
    if 'iphone' in m or 'apple' in m: return 'Apple'
    if 'xiaomi' in m or 'redmi' in m: return 'Xiaomi'
    return modelo.split()[0].capitalize()

def build_stmt(sql, params):
    """Construye un stmt para _send_stmts de turso"""
    args = []
    for p in (params or []):
        if p is None:
            args.append({'type': 'null'})
        elif isinstance(p, int):
            args.append({'type': 'text', 'value': str(p)})
        elif isinstance(p, float):
            args.append({'type': 'float', 'value': p})
        else:
            args.append({'type': 'text', 'value': str(p)})
    return {'sql': sql, 'args': args}

def batch_execute(stmts, label=""):
    """Manda stmts en bloques de 80 para no exceder límites"""
    import turso as t
    total = len(stmts)
    errores = []
    CHUNK = 80
    for i in range(0, total, CHUNK):
        chunk = stmts[i:i+CHUNK]
        try:
            results = t._send_stmts(chunk)
            for j, res in enumerate(results):
                if res.get('type') == 'error':
                    msg = res.get('error', {})
                    if isinstance(msg, dict): msg = msg.get('message', str(msg))
                    errores.append(f"{label}[{i+j}]: {msg}")
        except Exception as e:
            errores.append(f"{label} chunk {i}: {e}")
        pct = min(i+CHUNK, total)
        print(f"  {label}: {pct}/{total}...", flush=True)
    return errores

# ── Leer Excel ────────────────────────────────────────────────────────────────

print(f"Leyendo {EXCEL_PATH}...")
wb = openpyxl.load_workbook(EXCEL_PATH, read_only=True)
ws = wb.active
headers = None
raw_rows = []
for i, row in enumerate(ws.iter_rows(values_only=True)):
    if i == 0:
        headers = [str(h).strip() if h else '' for h in row]
        continue
    raw_rows.append(dict(zip(headers, row)))
print(f"  {len(raw_rows)} filas leídas")

# ── Procesar ──────────────────────────────────────────────────────────────────

empleados_dict = {}
equipos_list   = []
lineas_list    = []
asignaciones_list = []
imei_seen = set()
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

for r in raw_rows:
    tipo = clean_str(r.get('TIPO',''))
    if not tipo: continue
    tipo_up = tipo.upper()

    apellido = clean_str(r.get('APELLIDO'))
    nombre   = clean_str(r.get('NOMBRE'))
    legajo   = clean_legajo(r.get('LEGAJO'))
    numero   = clean_numero(r.get('Numero'))
    imei     = clean_imei(r.get('IMEI'))
    modelo   = clean_str(r.get('Modelo Equipo Celular'))
    sector   = clean_str(r.get('GERENCIA/UNIDAD'))
    lugar    = clean_str(r.get('UBICACIÓN LABORAL'))
    ceco     = clean_str(r.get('CECO'))
    empresa  = clean_str(r.get('EMPRESA'))
    plan     = clean_str(r.get('Plan Contratado'))
    fecha    = clean_fecha(r.get('FECHA INICIO'))
    obs      = clean_str(r.get('CAMBIOS'))

    if legajo and apellido:
        if legajo not in empleados_dict:
            empleados_dict[legajo] = (legajo, nombre or '', apellido, sector, lugar, now)

    if tipo_up == 'CELULAR' and imei and imei not in imei_seen:
        imei_seen.add(imei)
        equipos_list.append((imei, detect_marca(modelo), modelo or 'Sin modelo',
                             'asignado' if legajo else 'stock', obs, now))

    if numero and len(numero) >= 8:
        operadora = empresa if empresa in ('MOVISTAR','CLARO','PERSONAL') else 'MOVISTAR'
        lineas_list.append((numero, operadora, plan,
                            'kite' if tipo_up == 'TELEMETRIA' else 'standard',
                            'activa', imei, now, now))

    if tipo_up == 'CELULAR' and imei and legajo:
        asignaciones_list.append((imei, legajo, fecha, obs))

empleados_list = list(empleados_dict.values())
print(f"  Empleados: {len(empleados_list)}")
print(f"  Equipos:   {len(equipos_list)}")
print(f"  Líneas:    {len(lineas_list)}")
print(f"  Asignaciones: {len(asignaciones_list)}")

# ── Batch inserts ─────────────────────────────────────────────────────────────

all_errors = []

# Empleados
print("\nImportando empleados...")
emp_sql = '''INSERT INTO empleados (legajo,nombre,apellido,sector,lugar_trabajo,activo,created_at)
VALUES (?,?,?,?,?,1,?)
ON CONFLICT(legajo) DO UPDATE SET nombre=excluded.nombre,apellido=excluded.apellido,
sector=excluded.sector,lugar_trabajo=excluded.lugar_trabajo'''
stmts = [build_stmt(emp_sql, row) for row in empleados_list]
all_errors += batch_execute(stmts, "Empleados")

# Equipos
print("\nImportando equipos...")
eq_sql = '''INSERT INTO equipos_cel (imei,marca,modelo,estado,observaciones,created_at)
VALUES (?,?,?,?,?,?)
ON CONFLICT(imei) DO UPDATE SET marca=excluded.marca,modelo=excluded.modelo,
observaciones=excluded.observaciones'''
stmts = [build_stmt(eq_sql, row) for row in equipos_list]
all_errors += batch_execute(stmts, "Equipos")

# Para asignaciones necesitamos los IDs — hacemos lookup
print("\nImportando asignaciones...")
conn = turso.connect()

asig_ok = 0
asig_errors = []
for imei, legajo, fecha, obs in asignaciones_list:
    try:
        cur_eq  = conn.execute('SELECT id FROM equipos_cel WHERE imei=?', (imei,))
        eq_row  = cur_eq.fetchone()
        cur_emp = conn.execute('SELECT id FROM empleados WHERE legajo=?', (legajo,))
        emp_row = cur_emp.fetchone()
        if not eq_row:
            asig_errors.append(f"Sin equipo IMEI {imei}")
            continue
        eq_id  = eq_row['id'] if isinstance(eq_row, dict) else eq_row[0]
        emp_id = (emp_row['id'] if isinstance(emp_row, dict) else emp_row[0]) if emp_row else None
        conn.execute('UPDATE asignaciones_cel SET activa=0 WHERE equipo_id=? AND activa=1', (eq_id,))
        conn.execute('''INSERT INTO asignaciones_cel (equipo_id,empleado_id,fecha_desde,activa,notas,usuario_reg,created_at)
            VALUES (?,?,?,1,?,'import',?)''', (eq_id, emp_id, fecha, obs, now))
        conn.execute("UPDATE equipos_cel SET estado='asignado' WHERE id=?", (eq_id,))
        asig_ok += 1
    except Exception as e:
        asig_errors.append(f"IMEI {imei}: {e}")

conn.commit()
conn.close()
print(f"  Asignaciones: {asig_ok}/{len(asignaciones_list)}")
all_errors += asig_errors

# Líneas
print("\nImportando líneas SIM...")
conn2 = turso.connect()
lin_ok = 0
lin_errors = []
for numero, operadora, plan, tipo, estado, imei_ref, cat, uat in lineas_list:
    try:
        eq_id = None
        if imei_ref:
            cur = conn2.execute('SELECT id FROM equipos_cel WHERE imei=?', (imei_ref,))
            row = cur.fetchone()
            if row:
                eq_id = row['id'] if isinstance(row, dict) else row[0]
        conn2.execute('''INSERT OR IGNORE INTO lineas_cel (numero,operadora,plan,tipo,estado,equipo_id,created_at)
            VALUES (?,?,?,?,?,?,?)''', (numero, operadora, plan, tipo, estado, eq_id, cat, uat))
        lin_ok += 1
    except Exception as e:
        lin_errors.append(f"Línea {numero}: {e}")
conn2.commit()
conn2.close()
print(f"  Líneas: {lin_ok}/{len(lineas_list)}")
all_errors += lin_errors

# ── Resumen ───────────────────────────────────────────────────────────────────
print("\n" + "="*50)
print("IMPORT COMPLETADO")
print(f"  Empleados:    {len(empleados_list)}")
print(f"  Equipos:      {len(equipos_list)}")
print(f"  Asignaciones: {asig_ok}")
print(f"  Líneas:       {lin_ok}")
if all_errors:
    print(f"\n  ERRORES ({len(all_errors)}):")
    for e in all_errors[:15]:
        print(f"    - {e}")
    if len(all_errors) > 15:
        print(f"    ... y {len(all_errors)-15} más")
print("="*50)
