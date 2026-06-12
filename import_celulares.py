"""
import_celulares.py — v_final
Basado en estructura real de DB verificada en Turso.

Tablas y columnas reales:
  empleados:      legajo, nombre, apellido, sector, lugar_trabajo, activo, created_at
  equipos_cel:    marca, modelo, imei, estado, created_at
  asignaciones_cel: equipo_id, empleado_id(NOT NULL), fecha_desde(NOT NULL), activa, notas, usuario_reg, created_at
  lineas_cel:     numero, operadora, plan, equipo_id, estado, created_at
"""
import os, re, datetime

try:
    import openpyxl
except ImportError:
    os.system("pip install openpyxl -q")
    import openpyxl

import turso

EXCEL_PATH = os.path.join(os.path.dirname(__file__), "celus.xlsx")
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# ── Helpers ───────────────────────────────────────────────────────────────────

def s(v):
    if v is None: return None
    r = str(v).strip()
    return r if r and r.lower() not in ('none','nan','nat') else None

def clean_imei(v):
    if v is None: return None
    r = str(v).strip()
    if 'e+' in r.lower() or 'e-' in r.lower():
        try: r = str(int(float(r)))
        except: pass
    if r.endswith('.0'): r = r[:-2]
    r = re.sub(r'[^0-9]', '', r)
    return r if len(r) >= 10 else None

def clean_numero(v):
    if v is None: return None
    r = str(v).strip()
    if r.endswith('.0'): r = r[:-2]
    r = re.sub(r'[^0-9]', '', r)
    return r if len(r) >= 6 else None

def clean_legajo(v):
    if v is None: return None
    r = str(v).strip()
    if r.endswith('.0'): r = r[:-2]
    r = re.sub(r'[^0-9]', '', r)
    return r if r else None

def clean_fecha(v):
    if v is None: return None
    if isinstance(v, (datetime.date, datetime.datetime)):
        return v.strftime('%Y-%m-%d')
    r = str(v).strip()
    m = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', r)
    if m: return f"{m.group(3)}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}"
    try:
        n = float(r)
        if 30000 < n < 60000:
            d = datetime.datetime(1899, 12, 30) + datetime.timedelta(days=n)
            return d.strftime('%Y-%m-%d')
    except: pass
    return None

def detect_marca(modelo):
    if not modelo: return 'Desconocida'
    m = modelo.lower()
    for marca, kws in [
        ('Samsung',  ['samsung','galaxy']),
        ('Motorola', ['motorola','moto']),
        ('Huawei',   ['huawei']),
        ('LG',       ['lg c','lg k','lg g']),
        ('Apple',    ['iphone','apple']),
        ('Xiaomi',   ['xiaomi','redmi']),
        ('Nokia',    ['nokia']),
        ('Alcatel',  ['alcatel']),
    ]:
        if any(k in m for k in kws): return marca
    return modelo.split()[0].capitalize() if modelo else 'Desconocida'

# ── Leer Excel ────────────────────────────────────────────────────────────────

print(f"Leyendo {EXCEL_PATH}...")
wb = openpyxl.load_workbook(EXCEL_PATH, read_only=True)
ws = wb.active

headers = None
raw_rows = []
for i, row in enumerate(ws.iter_rows(values_only=True)):
    if i == 0:
        headers = [str(h).strip() if h else f'col{i}' for i, h in enumerate(row)]
        continue
    raw_rows.append(dict(zip(headers, row)))

print(f"  {len(raw_rows)} filas leidas\n")

# ── Procesar ──────────────────────────────────────────────────────────────────

empleados_dict = {}
equipos_list   = []
asig_list      = []
lineas_list    = []
imei_seen      = set()
linea_seen     = set()

for r in raw_rows:
    tipo    = s(r.get('TIPO', ''))
    if not tipo: continue
    tipo_up = tipo.upper()

    apellido = s(r.get('APELLIDO'))
    nombre   = s(r.get('NOMBRE'))
    legajo   = clean_legajo(r.get('LEGAJO'))
    numero   = clean_numero(r.get('Numero'))
    imei     = clean_imei(r.get('IMEI'))
    modelo   = s(r.get('Modelo Equipo Celular'))
    sector   = s(r.get('GERENCIA/UNIDAD'))
    lugar    = s(r.get('UBICACION LABORAL')) or s(r.get('UBICACIÓN LABORAL'))
    empresa  = s(r.get('EMPRESA'))
    plan     = s(r.get('Plan Contratado'))
    fecha    = clean_fecha(r.get('FECHA INICIO'))

    if legajo and apellido and legajo not in empleados_dict:
        empleados_dict[legajo] = (legajo, nombre or '', apellido, sector, lugar)

    if tipo_up == 'CELULAR' and imei and imei not in imei_seen:
        imei_seen.add(imei)
        equipos_list.append((detect_marca(modelo), modelo or 'Sin modelo', imei,
                             'asignado' if legajo else 'stock'))

    if tipo_up == 'CELULAR' and imei and legajo:
        asig_list.append((imei, legajo, fecha or '2020-01-01'))

    if numero and numero not in linea_seen:
        linea_seen.add(numero)
        operadora = empresa if empresa in ('MOVISTAR','CLARO','PERSONAL') else 'MOVISTAR'
        lineas_list.append((numero, operadora, plan, imei))

empleados_list = list(empleados_dict.values())
print(f"  Empleados: {len(empleados_list)}")
print(f"  Equipos:   {len(equipos_list)}")
print(f"  Asigs:     {len(asig_list)}")
print(f"  Lineas:    {len(lineas_list)}\n")

# ── DB ────────────────────────────────────────────────────────────────────────

conn = turso.connect()
stats  = {'empleados':0,'equipos':0,'asignaciones':0,'lineas':0}
errors = []

# 1. EMPLEADOS — cols: legajo,nombre,apellido,sector,lugar_trabajo,activo,created_at
print("Importando empleados...")
for legajo, nombre, apellido, sector, lugar in empleados_list:
    try:
        conn.execute(
            'INSERT INTO empleados (legajo,nombre,apellido,sector,lugar_trabajo,activo,created_at) '
            'VALUES (?,?,?,?,?,1,?) '
            'ON CONFLICT(legajo) DO UPDATE SET nombre=excluded.nombre,apellido=excluded.apellido,'
            'sector=excluded.sector,lugar_trabajo=excluded.lugar_trabajo',
            (legajo, nombre, apellido, sector, lugar, now))
        stats['empleados'] += 1
    except Exception as e:
        errors.append(f"Empleado {legajo}: {e}")
conn.commit()
print(f"  OK {stats['empleados']}")

# 2. EQUIPOS — cols: marca,modelo,imei,estado,created_at
print("Importando equipos...")
for marca, modelo, imei, estado in equipos_list:
    try:
        conn.execute(
            'INSERT INTO equipos_cel (marca,modelo,imei,estado,created_at) '
            'VALUES (?,?,?,?,?) '
            'ON CONFLICT(imei) DO UPDATE SET marca=excluded.marca,modelo=excluded.modelo',
            (marca, modelo, imei, estado, now))
        stats['equipos'] += 1
    except Exception as e:
        errors.append(f"Equipo {imei}: {e}")
conn.commit()
print(f"  OK {stats['equipos']}")

# 3. ASIGNACIONES — cols: equipo_id,empleado_id,fecha_desde,activa,notas,usuario_reg,created_at
print("Importando asignaciones...")
for imei, legajo, fecha_desde in asig_list:
    try:
        cur = conn.execute('SELECT id FROM equipos_cel WHERE imei=?', (imei,))
        eq_row = cur.fetchone()
        cur2 = conn.execute('SELECT id FROM empleados WHERE legajo=?', (legajo,))
        emp_row = cur2.fetchone()
        if not eq_row:
            errors.append(f"Asig: IMEI {imei} no encontrado"); continue
        if not emp_row:
            errors.append(f"Asig: legajo {legajo} no encontrado"); continue
        eq_id  = eq_row['id']  if isinstance(eq_row,  dict) else eq_row[0]
        emp_id = emp_row['id'] if isinstance(emp_row, dict) else emp_row[0]
        conn.execute('UPDATE asignaciones_cel SET activa=0 WHERE equipo_id=? AND activa=1', (eq_id,))
        conn.execute(
            'INSERT INTO asignaciones_cel (equipo_id,empleado_id,fecha_desde,activa,notas,usuario_reg,created_at) '
            "VALUES (?,?,?,1,NULL,'import',?)",
            (eq_id, emp_id, fecha_desde, now))
        conn.execute("UPDATE equipos_cel SET estado='asignado' WHERE id=?", (eq_id,))
        stats['asignaciones'] += 1
    except Exception as e:
        errors.append(f"Asig {imei}: {e}")
conn.commit()
print(f"  OK {stats['asignaciones']}")

# 4. LINEAS — cols: numero,operadora,plan,equipo_id,estado,created_at
print("Importando lineas SIM...")
for numero, operadora, plan, imei_ref in lineas_list:
    try:
        eq_id = None
        if imei_ref:
            cur = conn.execute('SELECT id FROM equipos_cel WHERE imei=?', (imei_ref,))
            row = cur.fetchone()
            if row: eq_id = row['id'] if isinstance(row,dict) else row[0]
        conn.execute(
            "INSERT OR IGNORE INTO lineas_cel (numero,operadora,plan,equipo_id,estado,created_at) "
            "VALUES (?,?,?,?,'activa',?)",
            (numero, operadora, plan, eq_id, now))
        stats['lineas'] += 1
    except Exception as e:
        errors.append(f"Linea {numero}: {e}")
conn.commit()
conn.close()
print(f"  OK {stats['lineas']}")

# ── Resumen ───────────────────────────────────────────────────────────────────
print("\n" + "="*50)
print("IMPORT COMPLETADO")
for k,v in stats.items():
    print(f"  {k.capitalize()}: {v}")
if errors:
    print(f"\n  ERRORES ({len(errors)}):")
    for e in errors[:20]: print(f"    - {e}")
    if len(errors) > 20: print(f"    ... y {len(errors)-20} mas")
else:
    print("\n  Sin errores")
print("="*50)
