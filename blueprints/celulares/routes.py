import json
from flask import Blueprint, request, jsonify, render_template, session
from functools import wraps

cel_bp = Blueprint('celulares', __name__, url_prefix='/celulares')

# ── helpers ──────────────────────────────────────────────────────────────────

def get_db():
    import turso as db_driver
    return db_driver.connect()

def db_commit(conn):
    conn.commit()

def fetchall_dicts(cursor):
    rows = cursor.fetchall()
    result = []
    for r in rows:
        try:
            result.append(dict(r))
        except Exception:
            result.append({k: r[k] for k in r.keys()})
    return result

def fetchone_dict(cursor):
    row = cursor.fetchone()
    if row is None:
        return None
    try:
        return dict(row)
    except Exception:
        return {k: row[k] for k in row.keys()}

def _rol_celulares():
    """Retorna el rol del usuario en el módulo celulares, o None si no tiene acceso."""
    role = session.get('role')
    if role == 'admin':
        return 'admin'
    permisos = session.get('permisos', session.get('modulos', {}))
    if isinstance(permisos, list):
        return 'viewer' if 'celulares' in permisos else None
    if isinstance(permisos, dict):
        return permisos.get('celulares')
    return None

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'No autorizado'}), 401
        return f(*args, **kwargs)
    return decorated

def editor_required(f):
    """Requiere rol editor o admin EN el módulo celulares."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'No autorizado'}), 401
        rol = _rol_celulares()
        if rol not in ('editor', 'admin'):
            return jsonify({'error': 'Se requiere rol editor o admin en celulares'}), 403
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """Requiere rol admin EN el módulo celulares (o admin global)."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'No autorizado'}), 401
        rol = _rol_celulares()
        if rol != 'admin':
            return jsonify({'error': 'Se requiere rol admin en celulares'}), 403
        return f(*args, **kwargs)
    return decorated

def modulo_celulares_required(f):
    """Verifica que el usuario tenga cualquier acceso al módulo celulares."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            from flask import redirect, url_for
            return redirect(url_for('login_page'))
        if not _rol_celulares():
            from flask import abort
            abort(403)
        return f(*args, **kwargs)
    return decorated

def init_cel_tables():
    """Crea las tablas del módulo celulares si no existen."""
    conn = get_db()
    tables = [
        '''CREATE TABLE IF NOT EXISTS empleados (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            legajo        TEXT UNIQUE,
            nombre        TEXT NOT NULL,
            apellido      TEXT NOT NULL,
            puesto        TEXT,
            sector        TEXT,
            lugar_trabajo TEXT,
            email         TEXT,
            activo        INTEGER DEFAULT 1,
            fecha_ingreso TEXT,
            created_at    TEXT DEFAULT (datetime('now')),
            updated_at    TEXT DEFAULT (datetime('now'))
        )''',
        '''CREATE TABLE IF NOT EXISTS equipos_cel (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            marca           TEXT NOT NULL,
            modelo          TEXT NOT NULL,
            imei            TEXT UNIQUE NOT NULL,
            imei2           TEXT,
            numero_serie    TEXT,
            color           TEXT,
            almacenamiento  TEXT,
            estado          TEXT DEFAULT 'stock',
            motivo_baja     TEXT,
            fecha_baja      TEXT,
            garantia_hasta  TEXT,
            accesorios      TEXT,
            observaciones   TEXT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        )''',
        '''CREATE TABLE IF NOT EXISTS lineas_cel (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            numero      TEXT UNIQUE NOT NULL,
            operadora   TEXT,
            plan        TEXT,
            datos_gb    REAL,
            vencimiento TEXT,
            iccid       TEXT,
            equipo_id   INTEGER REFERENCES equipos_cel(id) ON DELETE SET NULL,
            estado      TEXT DEFAULT 'activa',
            tipo        TEXT DEFAULT 'standard',
            observaciones TEXT,
            created_at  TEXT DEFAULT (datetime('now')),
            updated_at  TEXT DEFAULT (datetime('now'))
        )''',
        '''CREATE TABLE IF NOT EXISTS asignaciones_cel (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            equipo_id    INTEGER NOT NULL REFERENCES equipos_cel(id),
            empleado_id  INTEGER REFERENCES empleados(id) ON DELETE SET NULL,
            linea_id     INTEGER REFERENCES lineas_cel(id) ON DELETE SET NULL,
            fecha_desde  TEXT,
            fecha_hasta  TEXT,
            activa       INTEGER DEFAULT 1,
            notas        TEXT,
            usuario_reg  TEXT,
            created_at   TEXT DEFAULT (datetime('now')),
            updated_at   TEXT DEFAULT (datetime('now'))
        )'''
    ]
    for t in tables:
        try:
            conn.execute(t)
            db_commit(conn)
        except Exception as e:
            if 'already exists' not in str(e).lower():
                raise
    conn.close()

# Ejecutar al importar el módulo
init_cel_tables()

# ── PÁGINA PRINCIPAL ─────────────────────────────────────────────────────────

@cel_bp.route('/', strict_slashes=False)
@cel_bp.route('/home', strict_slashes=False)
@modulo_celulares_required
def index():
    return render_template('celulares/index.html',
                           username=session.get('username'),
                           role=session.get('role'),
                           user_id=session.get('user_id', 0))

# ── API EQUIPOS ───────────────────────────────────────────────────────────────

@cel_bp.route('/api/equipos', methods=['GET'])
@login_required
def get_equipos():
    conn = get_db()
    q = request.args.get('q', '').strip()
    estado = request.args.get('estado', '').strip()

    sql = '''
        SELECT e.*,
               a.id        AS asig_id,
               a.fecha_desde,
               emp.id      AS empleado_id,
               emp.nombre  || ' ' || emp.apellido AS empleado_nombre,
               emp.legajo,
               emp.sector,
               l.numero    AS linea_numero,
               l.operadora AS linea_operadora
        FROM equipos_cel e
        LEFT JOIN asignaciones_cel a ON a.equipo_id = e.id AND a.activa = 1
        LEFT JOIN empleados emp ON a.empleado_id = emp.id
        LEFT JOIN lineas_cel l ON a.linea_id = l.id
        WHERE 1=1
    '''
    params = []

    if q:
        sql += ''' AND (
            e.marca LIKE ? OR e.modelo LIKE ? OR e.imei LIKE ?
            OR e.imei2 LIKE ? OR e.numero_serie LIKE ?
            OR emp.nombre LIKE ? OR emp.apellido LIKE ? OR emp.legajo LIKE ?
        )'''
        like = f'%{q}%'
        params.extend([like]*8)

    if estado:
        sql += ' AND e.estado = ?'
        params.append(estado)

    sql += ' ORDER BY e.marca, e.modelo, e.id'

    cur = conn.execute(sql, params)
    rows = fetchall_dicts(cur)
    conn.close()
    return jsonify(rows)


@cel_bp.route('/api/equipos/disponibles', methods=['GET'])
@login_required
def get_equipos_disponibles():
    """Equipos en stock (no asignados actualmente). Acepta ?q= para filtrar."""
    conn = get_db()
    q = request.args.get('q', '').strip()
    sql = '''
        SELECT id, marca, modelo, imei, imei2, numero_serie, color, almacenamiento
        FROM equipos_cel
        WHERE estado = 'stock'
          AND id NOT IN (SELECT equipo_id FROM asignaciones_cel WHERE activa = 1)
    '''
    params = []
    if q:
        sql += ''' AND (
            marca LIKE ? OR modelo LIKE ? OR imei LIKE ?
            OR imei2 LIKE ? OR numero_serie LIKE ?
        )'''
        like = f'%{q}%'
        params.extend([like]*5)
    sql += ' ORDER BY marca, modelo'
    cur = conn.execute(sql, params)
    rows = fetchall_dicts(cur)
    conn.close()
    return jsonify(rows)


@cel_bp.route('/api/equipos/<int:eid>', methods=['GET'])
@login_required
def get_equipo(eid):
    conn = get_db()
    cur = conn.execute('SELECT * FROM equipos_cel WHERE id = ?', (eid,))
    equipo = fetchone_dict(cur)
    if not equipo:
        conn.close()
        return jsonify({'error': 'No encontrado'}), 404

    # historial de asignaciones
    cur2 = conn.execute('''
        SELECT a.*,
               emp.nombre || ' ' || emp.apellido AS empleado_nombre,
               emp.legajo, emp.sector,
               l.numero AS linea_numero, l.operadora AS linea_operadora
        FROM asignaciones_cel a
        LEFT JOIN empleados emp ON a.empleado_id = emp.id
        LEFT JOIN lineas_cel l  ON a.linea_id   = l.id
        WHERE a.equipo_id = ?
        ORDER BY a.activa DESC, a.fecha_desde DESC, a.id DESC
    ''', (eid,))
    equipo['historial'] = fetchall_dicts(cur2)
    conn.close()
    return jsonify(equipo)


@cel_bp.route('/api/equipos', methods=['POST'])
@editor_required
def create_equipo():
    data = request.get_json()
    fields = ['marca','modelo','imei','imei2','numero_serie','color',
              'almacenamiento','estado','garantia_hasta','accesorios','observaciones']
    vals = [data.get(f) for f in fields]
    # estado default
    if not vals[fields.index('estado')]:
        vals[fields.index('estado')] = 'stock'
    conn = get_db()
    try:
        conn.execute(
            f'INSERT INTO equipos_cel ({",".join(fields)}) VALUES ({",".join(["?"]*len(fields))})',
            vals
        )
        db_commit(conn)
        cur = conn.execute('SELECT * FROM equipos_cel ORDER BY id DESC LIMIT 1')
        row = fetchone_dict(cur)
        conn.close()
        return jsonify(row), 201
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 409


@cel_bp.route('/api/equipos/<int:eid>', methods=['PUT'])
@editor_required
def update_equipo(eid):
    data = request.get_json()
    fields = ['marca','modelo','imei','imei2','numero_serie','color',
              'almacenamiento','estado','motivo_baja','fecha_baja',
              'garantia_hasta','accesorios','observaciones']
    sets = ', '.join([f'{f} = ?' for f in fields]) + ', updated_at = datetime(\'now\')'
    vals = [data.get(f) for f in fields] + [eid]
    conn = get_db()
    conn.execute(f'UPDATE equipos_cel SET {sets} WHERE id = ?', vals)
    db_commit(conn)
    cur = conn.execute('SELECT * FROM equipos_cel WHERE id = ?', (eid,))
    row = fetchone_dict(cur)
    conn.close()
    return jsonify(row)


@cel_bp.route('/api/equipos/<int:eid>', methods=['DELETE'])
@admin_required
def delete_equipo(eid):
    conn = get_db()
    conn.execute('UPDATE asignaciones_cel SET activa=0 WHERE equipo_id=?', (eid,))
    conn.execute('DELETE FROM equipos_cel WHERE id=?', (eid,))
    db_commit(conn)
    conn.close()
    return jsonify({'ok': True})


# ── API EMPLEADOS ─────────────────────────────────────────────────────────────

@cel_bp.route('/api/empleados', methods=['GET'])
@login_required
def get_empleados():
    conn = get_db()
    q = request.args.get('q', '').strip()
    sql = 'SELECT * FROM empleados WHERE activo = 1'
    params = []
    if q:
        sql += ' AND (nombre LIKE ? OR apellido LIKE ? OR legajo LIKE ? OR sector LIKE ?)'
        like = f'%{q}%'
        params.extend([like]*4)
    sql += ' ORDER BY apellido, nombre'
    cur = conn.execute(sql, params)
    rows = fetchall_dicts(cur)
    conn.close()
    return jsonify(rows)


@cel_bp.route('/api/empleados/<int:empid>', methods=['GET'])
@login_required
def get_empleado(empid):
    conn = get_db()
    cur = conn.execute('SELECT * FROM empleados WHERE id = ?', (empid,))
    emp = fetchone_dict(cur)
    if not emp:
        conn.close()
        return jsonify({'error': 'No encontrado'}), 404
    cur2 = conn.execute('''
        SELECT a.*, e.marca, e.modelo, e.imei, l.numero AS linea_numero
        FROM asignaciones_cel a
        JOIN equipos_cel e ON a.equipo_id = e.id
        LEFT JOIN lineas_cel l ON a.linea_id = l.id
        WHERE a.empleado_id = ?
        ORDER BY a.activa DESC, a.fecha_desde DESC
    ''', (empid,))
    emp['asignaciones'] = fetchall_dicts(cur2)
    conn.close()
    return jsonify(emp)


@cel_bp.route('/api/empleados', methods=['POST'])
@editor_required
def create_empleado():
    data = request.get_json()
    fields = ['legajo','nombre','apellido','puesto','sector','lugar_trabajo','email','fecha_ingreso']
    vals = [data.get(f) for f in fields]
    conn = get_db()
    try:
        conn.execute(
            f'INSERT INTO empleados ({",".join(fields)}) VALUES ({",".join(["?"]*len(fields))})',
            vals
        )
        db_commit(conn)
        cur = conn.execute('SELECT * FROM empleados ORDER BY id DESC LIMIT 1')
        row = fetchone_dict(cur)
        conn.close()
        return jsonify(row), 201
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 409


@cel_bp.route('/api/empleados/<int:empid>', methods=['PUT'])
@editor_required
def update_empleado(empid):
    data = request.get_json()
    fields = ['legajo','nombre','apellido','puesto','sector','lugar_trabajo','email','fecha_ingreso','activo']
    sets = ', '.join([f'{f} = ?' for f in fields]) + ', updated_at = datetime(\'now\')'
    vals = [data.get(f) for f in fields] + [empid]
    conn = get_db()
    conn.execute(f'UPDATE empleados SET {sets} WHERE id = ?', vals)
    db_commit(conn)
    cur = conn.execute('SELECT * FROM empleados WHERE id = ?', (empid,))
    row = fetchone_dict(cur)
    conn.close()
    return jsonify(row)


# ── API ASIGNACIONES CEL ──────────────────────────────────────────────────────

@cel_bp.route('/api/asignaciones', methods=['POST'])
@editor_required
def create_asignacion():
    data = request.get_json()
    equipo_id = data.get('equipo_id')
    if not equipo_id:
        return jsonify({'error': 'equipo_id requerido'}), 400

    conn = get_db()

    # Verificar que el equipo existe y está disponible
    cur = conn.execute('SELECT * FROM equipos_cel WHERE id = ?', (equipo_id,))
    equipo = fetchone_dict(cur)
    if not equipo:
        conn.close()
        return jsonify({'error': 'Equipo no encontrado'}), 404

    # Cerrar asignación activa anterior si existe
    cur2 = conn.execute('SELECT id FROM asignaciones_cel WHERE equipo_id=? AND activa=1', (equipo_id,))
    prev = fetchone_dict(cur2)
    if prev:
        conn.execute('''UPDATE asignaciones_cel SET activa=0, fecha_hasta=datetime('now'),
                        updated_at=datetime('now') WHERE id=?''', (prev['id'],))

    # Crear nueva asignación
    conn.execute('''
        INSERT INTO asignaciones_cel (equipo_id, empleado_id, linea_id, fecha_desde, activa, notas, usuario_reg)
        VALUES (?, ?, ?, ?, 1, ?, ?)
    ''', (
        equipo_id,
        data.get('empleado_id'),
        data.get('linea_id'),
        data.get('fecha_desde') or 'date(\'now\')',
        data.get('notas'),
        session.get('username')
    ))

    # Actualizar estado del equipo
    conn.execute("UPDATE equipos_cel SET estado='asignado', updated_at=datetime('now') WHERE id=?", (equipo_id,))
    db_commit(conn)

    cur3 = conn.execute('SELECT * FROM asignaciones_cel ORDER BY id DESC LIMIT 1')
    row = fetchone_dict(cur3)
    conn.close()
    return jsonify(row), 201


@cel_bp.route('/api/asignaciones/<int:aid>/desasignar', methods=['POST'])
@editor_required
def desasignar(aid):
    data = request.get_json() or {}
    conn = get_db()
    cur = conn.execute('SELECT equipo_id FROM asignaciones_cel WHERE id=?', (aid,))
    asig = fetchone_dict(cur)
    if not asig:
        conn.close()
        return jsonify({'error': 'Asignación no encontrada'}), 404

    conn.execute('''UPDATE asignaciones_cel SET activa=0, fecha_hasta=?,
                    notas=COALESCE(?,notas), updated_at=datetime('now') WHERE id=?''',
                 (data.get('fecha_hasta'), data.get('notas'), aid))

    # Equipo vuelve a stock
    conn.execute("UPDATE equipos_cel SET estado='stock', updated_at=datetime('now') WHERE id=?",
                 (asig['equipo_id'],))
    db_commit(conn)

    cur2 = conn.execute('SELECT * FROM asignaciones_cel WHERE id=?', (aid,))
    row = fetchone_dict(cur2)
    conn.close()
    return jsonify(row)


@cel_bp.route('/api/asignaciones/<int:aid>', methods=['PUT'])
@editor_required
def update_asignacion(aid):
    data = request.get_json()
    fields = ['empleado_id', 'linea_id', 'fecha_desde', 'notas']
    sets = ', '.join([f'{f} = ?' for f in fields]) + ', updated_at = datetime(\'now\')'
    vals = [data.get(f) for f in fields] + [aid]
    conn = get_db()
    conn.execute(f'UPDATE asignaciones_cel SET {sets} WHERE id = ?', vals)
    db_commit(conn)
    cur = conn.execute('SELECT * FROM asignaciones_cel WHERE id=?', (aid,))
    row = fetchone_dict(cur)
    conn.close()
    return jsonify(row)


# ── API LÍNEAS ────────────────────────────────────────────────────────────────

@cel_bp.route('/api/lineas', methods=['GET'])
@login_required
def get_lineas():
    conn = get_db()
    cur = conn.execute('''
        SELECT l.*, e.marca, e.modelo, e.imei
        FROM lineas_cel l
        LEFT JOIN equipos_cel e ON l.equipo_id = e.id
        ORDER BY l.numero
    ''')
    rows = fetchall_dicts(cur)
    conn.close()
    return jsonify(rows)


@cel_bp.route('/api/lineas', methods=['POST'])
@editor_required
def create_linea():
    data = request.get_json()
    fields = ['numero','operadora','plan','datos_gb','vencimiento','iccid','estado','tipo','observaciones']
    vals = [data.get(f) for f in fields]
    conn = get_db()
    try:
        conn.execute(
            f'INSERT INTO lineas_cel ({",".join(fields)}) VALUES ({",".join(["?"]*len(fields))})',
            vals
        )
        db_commit(conn)
        cur = conn.execute('SELECT * FROM lineas_cel ORDER BY id DESC LIMIT 1')
        row = fetchone_dict(cur)
        conn.close()
        return jsonify(row), 201
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 409


@cel_bp.route('/api/lineas/<int:lid>', methods=['PUT'])
@editor_required
def update_linea(lid):
    data = request.get_json()
    fields = ['numero','operadora','plan','datos_gb','vencimiento','iccid','estado','tipo','observaciones','equipo_id']
    sets = ', '.join([f'{f} = ?' for f in fields]) + ', updated_at = datetime(\'now\')'
    vals = [data.get(f) for f in fields] + [lid]
    conn = get_db()
    conn.execute(f'UPDATE lineas_cel SET {sets} WHERE id = ?', vals)
    db_commit(conn)
    cur = conn.execute('SELECT * FROM lineas_cel WHERE id=?', (lid,))
    row = fetchone_dict(cur)
    conn.close()
    return jsonify(row)


# ── IMPORT EXCEL ──────────────────────────────────────────────────────────────

@cel_bp.route('/api/import', methods=['POST'])
@admin_required
def import_excel():
    """
    Acepta JSON con keys: equipos[], empleados[], asignaciones[]
    Cada equipo: {marca, modelo, imei, imei2, numero_serie, color, almacenamiento, estado, observaciones}
    Cada empleado: {legajo, nombre, apellido, puesto, sector, lugar_trabajo, email}
    Cada asignacion: {imei, legajo, linea_numero, fecha_desde, notas}
    """
    data = request.get_json()
    conn = get_db()
    stats = {'equipos': 0, 'empleados': 0, 'asignaciones': 0, 'errores': []}

    # Equipos
    for eq in data.get('equipos', []):
        try:
            conn.execute('''
                INSERT INTO equipos_cel (marca,modelo,imei,imei2,numero_serie,color,almacenamiento,estado,observaciones)
                VALUES (?,?,?,?,?,?,?,?,?)
                ON CONFLICT(imei) DO UPDATE SET
                  marca=excluded.marca, modelo=excluded.modelo,
                  imei2=excluded.imei2, numero_serie=excluded.numero_serie,
                  color=excluded.color, almacenamiento=excluded.almacenamiento,
                  observaciones=excluded.observaciones,
                  updated_at=datetime('now')
            ''', (eq.get('marca'), eq.get('modelo'), eq.get('imei'), eq.get('imei2'),
                  eq.get('numero_serie'), eq.get('color'), eq.get('almacenamiento'),
                  eq.get('estado','stock'), eq.get('observaciones')))
            stats['equipos'] += 1
        except Exception as e:
            stats['errores'].append(f"Equipo {eq.get('imei')}: {e}")

    db_commit(conn)

    # Empleados
    for emp in data.get('empleados', []):
        try:
            conn.execute('''
                INSERT INTO empleados (legajo,nombre,apellido,puesto,sector,lugar_trabajo,email)
                VALUES (?,?,?,?,?,?,?)
                ON CONFLICT(legajo) DO UPDATE SET
                  nombre=excluded.nombre, apellido=excluded.apellido,
                  puesto=excluded.puesto, sector=excluded.sector,
                  lugar_trabajo=excluded.lugar_trabajo, email=excluded.email,
                  updated_at=datetime('now')
            ''', (emp.get('legajo'), emp.get('nombre'), emp.get('apellido'),
                  emp.get('puesto'), emp.get('sector'), emp.get('lugar_trabajo'), emp.get('email')))
            stats['empleados'] += 1
        except Exception as e:
            stats['errores'].append(f"Empleado {emp.get('legajo')}: {e}")

    db_commit(conn)

    # Asignaciones (por imei + legajo)
    for asig in data.get('asignaciones', []):
        try:
            cur_e = conn.execute('SELECT id FROM equipos_cel WHERE imei=?', (asig.get('imei'),))
            eq_row = fetchone_dict(cur_e)
            cur_emp = conn.execute('SELECT id FROM empleados WHERE legajo=?', (asig.get('legajo'),))
            emp_row = fetchone_dict(cur_emp)
            if not eq_row:
                stats['errores'].append(f"Asig: IMEI {asig.get('imei')} no encontrado")
                continue
            # Cerrar asignación activa previa
            conn.execute('''UPDATE asignaciones_cel SET activa=0, updated_at=datetime('now')
                            WHERE equipo_id=? AND activa=1''', (eq_row['id'],))
            conn.execute('''
                INSERT INTO asignaciones_cel (equipo_id, empleado_id, fecha_desde, activa, notas, usuario_reg)
                VALUES (?, ?, ?, 1, ?, 'import')
            ''', (eq_row['id'], emp_row['id'] if emp_row else None,
                  asig.get('fecha_desde'), asig.get('notas')))
            if emp_row:
                conn.execute("UPDATE equipos_cel SET estado='asignado' WHERE id=?", (eq_row['id'],))
            stats['asignaciones'] += 1
        except Exception as e:
            stats['errores'].append(f"Asig IMEI {asig.get('imei')}: {e}")

    db_commit(conn)
    conn.close()
    return jsonify({'ok': True, 'stats': stats})
