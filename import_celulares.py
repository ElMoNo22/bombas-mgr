"""
import_celulares.py
Importa empleados, equipos y asignaciones desde el Excel de telefonía.
Ejecutar UNA SOLA VEZ en el servidor o localmente con las vars de entorno de Turso.

Uso:
  python import_celulares.py

Requiere:
  - TURSO_URL y TURSO_AUTH_TOKEN en variables de entorno (igual que el resto del proyecto)
  - openpyxl instalado: pip install openpyxl
"""

import os, re, sys, json, datetime

try:
    import openpyxl
except ImportError:
    print("Instalando openpyxl...")
    os.system("pip install openpyxl --break-system-packages -q")
    import openpyxl

import turso

EXCEL_PATH = os.path.join(os.path.dirname(__file__), "celus.xlsx")

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
            d = datetime.datetime(1899, 12, 30) + datetime.timedelta(days=n)
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
    if 'nokia' in m: return 'Nokia'
    return modelo.split()[0].capitalize()

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

for r in raw_rows:
    tipo     = clean_str(r.get('TIPO', ''))
    if not tipo: continue
    tipo_up  = tipo.upper()

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

    # Empleados
    if legajo and apellido:
        if legajo not in empleados_dict:
            empleados_dict[legajo] = {
                'legajo': legajo,
                'apellido': apellido,
                'nombre': nombre or '',
                'sector': sector,
                'lugar_trabajo': lugar,
                'observaciones': ceco,
            }

    # Equipos celulares
    if tipo_up == 'CELULAR' and imei and imei not in imei_seen:
        imei_seen.add(imei)
        equipos_list.append({
            'imei': imei,
            'marca': detect_marca(modelo),
            'modelo': modelo or 'Sin modelo',
            'estado': 'asignado' if legajo else 'stock',
            'observaciones': obs,
        })

    # Líneas SIM
    if numero and len(numero) >= 8:
        operadora = empresa if empresa in ('MOVISTAR', 'CLARO', 'PERSONAL') else 'MOVISTAR'
        lineas_list.append({
            'numero': numero,
            'operadora': operadora,
            'plan': plan,
            'tipo': 'kite' if tipo_up == 'TELEMETRIA' else 'standard',
            'estado': 'activa',
            'imei_ref': imei,
            'legajo_ref': legajo,
        })

    # Asignaciones
    if tipo_up == 'CELULAR' and imei and legajo:
        asignaciones_list.append({
            'imei': imei,
            'legajo': legajo,
            'fecha_desde': fecha,
            'notas': obs,
        })

empleados_list = list(empleados_dict.values())
print(f"  Empleados únicos: {len(empleados_list)}")
print(f"  Equipos únicos:   {len(equipos_list)}")
print(f"  Líneas:           {len(lineas_list)}")
print(f"  Asignaciones:     {len(asignaciones_list)}")

# ── Cargar a DB ───────────────────────────────────────────────────────────────

conn = turso.connect()
stats = {'empleados': 0, 'equipos': 0, 'lineas': 0, 'asignaciones': 0, 'errores': []}

now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Empleados
print("\nImportando empleados...")
for emp in empleados_list:
    try:
        conn.execute('''
            INSERT INTO empleados (legajo, nombre, apellido, sector, lugar_trabajo, observaciones, activo, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
            ON CONFLICT(legajo) DO UPDATE SET
              nombre=excluded.nombre, apellido=excluded.apellido,
              sector=excluded.sector, lugar_trabajo=excluded.lugar_trabajo,
              updated_at=excluded.updated_at
        ''', (emp['legajo'], emp['nombre'], emp['apellido'],
              emp['sector'], emp['lugar_trabajo'], emp['observaciones'], now, now))
        stats['empleados'] += 1
    except Exception as e:
        stats['errores'].append(f"Empleado {emp['legajo']}: {e}")
conn.commit()
print(f"  ✓ {stats['empleados']} empleados")

# Equipos
print("Importando equipos...")
for eq in equipos_list:
    try:
        conn.execute('''
            INSERT INTO equipos_cel (imei, marca, modelo, estado, observaciones, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(imei) DO UPDATE SET
              marca=excluded.marca, modelo=excluded.modelo,
              observaciones=excluded.observaciones, updated_at=excluded.updated_at
        ''', (eq['imei'], eq['marca'], eq['modelo'],
              eq['estado'], eq['observaciones'], now, now))
        stats['equipos'] += 1
    except Exception as e:
        stats['errores'].append(f"Equipo {eq['imei']}: {e}")
conn.commit()
print(f"  ✓ {stats['equipos']} equipos")

# Asignaciones
print("Importando asignaciones...")
for asig in asignaciones_list:
    try:
        # Buscar IDs
        cur_eq = conn.execute('SELECT id FROM equipos_cel WHERE imei=?', (asig['imei'],))
        eq_row = cur_eq.fetchone()
        cur_emp = conn.execute('SELECT id FROM empleados WHERE legajo=?', (asig['legajo'],))
        emp_row = cur_emp.fetchone()

        if not eq_row:
            stats['errores'].append(f"Asig sin equipo IMEI {asig['imei']}")
            continue

        eq_id  = eq_row[0] if not isinstance(eq_row, dict) else eq_row['id']
        emp_id = (emp_row[0] if not isinstance(emp_row, dict) else emp_row['id']) if emp_row else None

        # Cerrar asignación activa previa si existe
        conn.execute('''UPDATE asignaciones_cel SET activa=0, updated_at=?
                        WHERE equipo_id=? AND activa=1''', (now, eq_id))

        conn.execute('''
            INSERT INTO asignaciones_cel (equipo_id, empleado_id, fecha_desde, activa, notas, usuario_reg, created_at, updated_at)
            VALUES (?, ?, ?, 1, ?, 'import', ?, ?)
        ''', (eq_id, emp_id, asig['fecha_desde'], asig['notas'], now, now))

        # Marcar equipo como asignado
        conn.execute("UPDATE equipos_cel SET estado='asignado', updated_at=? WHERE id=?", (now, eq_id))
        stats['asignaciones'] += 1
    except Exception as e:
        stats['errores'].append(f"Asig IMEI {asig['imei']}: {e}")

conn.commit()
print(f"  ✓ {stats['asignaciones']} asignaciones")

# Líneas
print("Importando líneas SIM...")
for lin in lineas_list:
    try:
        # Buscar equipo asociado si tiene IMEI
        eq_id = None
        if lin['imei_ref']:
            cur = conn.execute('SELECT id FROM equipos_cel WHERE imei=?', (lin['imei_ref'],))
            row = cur.fetchone()
            if row:
                eq_id = row[0] if not isinstance(row, dict) else row['id']

        conn.execute('''
            INSERT OR IGNORE INTO lineas_cel (numero, operadora, plan, tipo, estado, equipo_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (lin['numero'], lin['operadora'], lin['plan'],
              lin['tipo'], lin['estado'], eq_id, now, now))
        stats['lineas'] += 1
    except Exception as e:
        stats['errores'].append(f"Línea {lin['numero']}: {e}")

conn.commit()
print(f"  ✓ {stats['lineas']} líneas")

# ── Resumen ───────────────────────────────────────────────────────────────────

print("\n" + "="*50)
print("IMPORT COMPLETADO")
print(f"  Empleados: {stats['empleados']}")
print(f"  Equipos:   {stats['equipos']}")
print(f"  Asignaciones: {stats['asignaciones']}")
print(f"  Líneas:    {stats['lineas']}")
if stats['errores']:
    print(f"\n  ERRORES ({len(stats['errores'])}):")
    for e in stats['errores'][:20]:
        print(f"    - {e}")
    if len(stats['errores']) > 20:
        print(f"    ... y {len(stats['errores'])-20} más")
print("="*50)
conn.close()
