from flask import render_template, request, jsonify, session
from datetime import datetime
from functools import wraps
import turso
from . import cel_bp

# ── Auth helper ──────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return jsonify({'error': 'No autorizado'}), 401
        return f(*args, **kwargs)
    return decorated

def get_db():
    return turso.connect()

def now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def today():
    return datetime.now().strftime('%Y-%m-%d')

# ── Página principal ─────────────────────────────────────────

@cel_bp.route('/')
def index():
    if not session.get('user_id'):
        from flask import redirect, url_for
        return redirect(url_for('login'))
    return render_template('celulares/index.html')

# ════════════════════════════════════════════════════════════
#  EMPLEADOS
# ════════════════════════════════════════════════════════════

@cel_bp.route('/api/empleados', methods=['GET'])
@login_required
def get_empleados():
    db = get_db()
    rows = db.execute('''
        SELECT e.*,
               ec.marca || ' ' || ec.modelo AS equipo_actual,
               ec.id AS equipo_id
        FROM empleados e
        LEFT JOIN asignaciones_cel a ON a.empleado_id = e.id AND a.fecha_hasta IS NULL
        LEFT JOIN equipos_cel ec ON ec.id = a.equipo_id
        ORDER BY e.apellido, e.nombre
    ''').fetchall()
    return jsonify([dict(r) for r in rows])

@cel_bp.route('/api/empleados/<int:eid>', methods=['GET'])
@login_required
def get_empleado(eid):
    db = get_db()
    emp = db.execute('SELECT * FROM empleados WHERE id = ?', (eid,)).fetchone()
    if not emp:
        return jsonify({'error': 'No encontrado'}), 404
    # asignación actual
    asig = db.execute('''
        SELECT a.*, ec.marca, ec.modelo, ec.imei, l.numero AS linea
        FROM asignaciones_cel a
        JOIN equipos_cel ec ON ec.id = a.equipo_id
        LEFT JOIN lineas_cel l ON l.id = a.linea_id
        WHERE a.empleado_id = ? AND a.fecha_hasta IS NULL
    ''', (eid,)).fetchone()
    # historial
    historial = db.execute('''
        SELECT a.*, ec.marca, ec.modelo
        FROM asignaciones_cel a
        JOIN equipos_cel ec ON ec.id = a.equipo_id
        WHERE a.empleado_id = ?
        ORDER BY a.fecha_desde DESC
    ''', (eid,)).fetchall()
    return jsonify({
        'empleado': dict(emp),
        'asignacion_actual': dict(asig) if asig else None,
        'historial': [dict(h) for h in historial]
    })

@cel_bp.route('/api/empleados', methods=['POST'])
@login_required
def crear_empleado():
    d = request.json
    db = get_db()
    db.execute('''
        INSERT INTO empleados (legajo, nombre, apellido, puesto, sector,
                               lugar_trabajo, email, activo, fecha_ingreso,
                               created_at, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    ''', (d['legajo'], d['nombre'], d['apellido'],
          d.get('puesto'), d.get('sector'), d.get('lugar_trabajo'),
          d.get('email'), d.get('activo', 1), d.get('fecha_ingreso'),
          now(), now()))
    return jsonify({'ok': True}), 201

@cel_bp.route('/api/empleados/<int:eid>', methods=['PUT'])
@login_required
def editar_empleado(eid):
    d = request.json
    db = get_db()
    db.execute('''
        UPDATE empleados SET legajo=?, nombre=?, apellido=?, puesto=?,
               sector=?, lugar_trabajo=?, email=?, activo=?,
               fecha_ingreso=?, updated_at=?
        WHERE id=?
    ''', (d['legajo'], d['nombre'], d['apellido'],
          d.get('puesto'), d.get('sector'), d.get('lugar_trabajo'),
          d.get('email'), d.get('activo', 1), d.get('fecha_ingreso'),
          now(), eid))
    return jsonify({'ok': True})

@cel_bp.route('/api/empleados/<int:eid>', methods=['DELETE'])
@login_required
def eliminar_empleado(eid):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Solo admin'}), 403
    db = get_db()
    db.execute('UPDATE empleados SET activo=0, updated_at=? WHERE id=?', (now(), eid))
    return jsonify({'ok': True})

# ════════════════════════════════════════════════════════════
#  EQUIPOS CELULARES
# ════════════════════════════════════════════════════════════

@cel_bp.route('/api/equipos', methods=['GET'])
@login_required
def get_equipos():
    db = get_db()
    rows = db.execute('''
        SELECT ec.*,
               e.nombre || ' ' || e.apellido AS usuario_nombre,
               e.legajo, e.sector,
               l.numero AS linea_numero, l.operadora,
               a.fecha_desde AS asignado_desde
        FROM equipos_cel ec
        LEFT JOIN asignaciones_cel a ON a.equipo_id = ec.id AND a.fecha_hasta IS NULL
        LEFT JOIN empleados e ON e.id = a.empleado_id
        LEFT JOIN lineas_cel l ON l.id = a.linea_id
        ORDER BY ec.marca, ec.modelo
    ''').fetchall()
    return jsonify([dict(r) for r in rows])

@cel_bp.route('/api/equipos/<int:eid>', methods=['GET'])
@login_required
def get_equipo(eid):
    db = get_db()
    eq = db.execute('SELECT * FROM equipos_cel WHERE id=?', (eid,)).fetchone()
    if not eq:
        return jsonify({'error': 'No encontrado'}), 404
    tickets = db.execute(
        'SELECT * FROM tickets_cel WHERE equipo_id=? ORDER BY created_at DESC', (eid,)
    ).fetchall()
    historial = db.execute('''
        SELECT a.*, e.nombre || ' ' || e.apellido AS empleado_nombre,
               e.legajo, e.sector, l.numero AS linea
        FROM asignaciones_cel a
        LEFT JOIN empleados e ON e.id = a.empleado_id
        LEFT JOIN lineas_cel l ON l.id = a.linea_id
        WHERE a.equipo_id = ?
        ORDER BY a.fecha_desde DESC
    ''', (eid,)).fetchall()
    return jsonify({
        'equipo': dict(eq),
        'tickets': [dict(t) for t in tickets],
        'historial': [dict(h) for h in historial]
    })

@cel_bp.route('/api/equipos', methods=['POST'])
@login_required
def crear_equipo():
    d = request.json
    db = get_db()
    db.execute('''
        INSERT INTO equipos_cel (marca, modelo, imei, imei2, numero_serie,
                                  color, almacenamiento, estado, garantia_hasta,
                                  accesorios, observaciones, created_at, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', (d['marca'], d['modelo'], d['imei'], d.get('imei2'),
          d.get('numero_serie'), d.get('color'), d.get('almacenamiento'),
          d.get('estado', 'stock'), d.get('garantia_hasta'),
          d.get('accesorios'), d.get('observaciones'), now(), now()))
    return jsonify({'ok': True}), 201

@cel_bp.route('/api/equipos/<int:eid>', methods=['PUT'])
@login_required
def editar_equipo(eid):
    d = request.json
    db = get_db()
    db.execute('''
        UPDATE equipos_cel SET marca=?, modelo=?, imei=?, imei2=?,
               numero_serie=?, color=?, almacenamiento=?, estado=?,
               garantia_hasta=?, accesorios=?, observaciones=?,
               motivo_baja=?, fecha_baja=?, updated_at=?
        WHERE id=?
    ''', (d['marca'], d['modelo'], d['imei'], d.get('imei2'),
          d.get('numero_serie'), d.get('color'), d.get('almacenamiento'),
          d.get('estado', 'stock'), d.get('garantia_hasta'),
          d.get('accesorios'), d.get('observaciones'),
          d.get('motivo_baja'), d.get('fecha_baja'), now(), eid))
    return jsonify({'ok': True})

# ── Asignar equipo a empleado ────────────────────────────────

@cel_bp.route('/api/equipos/<int:eid>/asignar', methods=['POST'])
@login_required
def asignar_equipo(eid):
    d = request.json
    db = get_db()
    # cerrar asignación anterior si existe
    db.execute('''
        UPDATE asignaciones_cel SET fecha_hasta=?
        WHERE equipo_id=? AND fecha_hasta IS NULL
    ''', (today(), eid))
    # crear nueva asignación
    db.execute('''
        INSERT INTO asignaciones_cel (equipo_id, empleado_id, linea_id,
                                       fecha_desde, acta_nro, observaciones, created_at)
        VALUES (?,?,?,?,?,?,?)
    ''', (eid, d['empleado_id'], d.get('linea_id'),
          d.get('fecha_desde', today()), d.get('acta_nro'),
          d.get('observaciones'), now()))
    db.execute("UPDATE equipos_cel SET estado='asignado', updated_at=? WHERE id=?", (now(), eid))
    return jsonify({'ok': True})

@cel_bp.route('/api/equipos/<int:eid>/desasignar', methods=['POST'])
@login_required
def desasignar_equipo(eid):
    db = get_db()
    db.execute('''
        UPDATE asignaciones_cel SET fecha_hasta=?
        WHERE equipo_id=? AND fecha_hasta IS NULL
    ''', (today(), eid))
    db.execute("UPDATE equipos_cel SET estado='stock', updated_at=? WHERE id=?", (now(), eid))
    return jsonify({'ok': True})

# ════════════════════════════════════════════════════════════
#  LÍNEAS CELULARES
# ════════════════════════════════════════════════════════════

@cel_bp.route('/api/lineas', methods=['GET'])
@login_required
def get_lineas():
    db = get_db()
    rows = db.execute('''
        SELECT l.*,
               ec.marca || ' ' || ec.modelo AS equipo_nombre
        FROM lineas_cel l
        LEFT JOIN equipos_cel ec ON ec.id = l.equipo_id
        ORDER BY l.numero
    ''').fetchall()
    return jsonify([dict(r) for r in rows])

@cel_bp.route('/api/lineas', methods=['POST'])
@login_required
def crear_linea():
    d = request.json
    db = get_db()
    db.execute('''
        INSERT INTO lineas_cel (numero, operadora, plan, datos_gb,
                                 vencimiento, iccid, equipo_id, estado,
                                 observaciones, created_at, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    ''', (d['numero'], d.get('operadora'), d.get('plan'),
          d.get('datos_gb'), d.get('vencimiento'), d.get('iccid'),
          d.get('equipo_id'), d.get('estado', 'activa'),
          d.get('observaciones'), now(), now()))
    return jsonify({'ok': True}), 201

@cel_bp.route('/api/lineas/<int:lid>', methods=['PUT'])
@login_required
def editar_linea(lid):
    d = request.json
    db = get_db()
    db.execute('''
        UPDATE lineas_cel SET numero=?, operadora=?, plan=?, datos_gb=?,
               vencimiento=?, iccid=?, equipo_id=?, estado=?,
               observaciones=?, updated_at=?
        WHERE id=?
    ''', (d['numero'], d.get('operadora'), d.get('plan'),
          d.get('datos_gb'), d.get('vencimiento'), d.get('iccid'),
          d.get('equipo_id'), d.get('estado', 'activa'),
          d.get('observaciones'), now(), lid))
    return jsonify({'ok': True})

# ════════════════════════════════════════════════════════════
#  TICKETS
# ════════════════════════════════════════════════════════════

@cel_bp.route('/api/tickets', methods=['GET'])
@login_required
def get_tickets():
    db = get_db()
    rows = db.execute('''
        SELECT t.*,
               ec.marca || ' ' || ec.modelo AS equipo_nombre,
               e.nombre || ' ' || e.apellido AS empleado_nombre
        FROM tickets_cel t
        JOIN equipos_cel ec ON ec.id = t.equipo_id
        LEFT JOIN empleados e ON e.id = t.empleado_id
        ORDER BY t.created_at DESC
    ''').fetchall()
    return jsonify([dict(r) for r in rows])

@cel_bp.route('/api/tickets', methods=['POST'])
@login_required
def crear_ticket():
    d = request.json
    db = get_db()
    # generar nro_ticket
    count = db.execute('SELECT COUNT(*) as c FROM tickets_cel').fetchone()
    nro = f"TK-{(count['c'] + 1):04d}"
    db.execute('''
        INSERT INTO tickets_cel (nro_ticket, equipo_id, empleado_id, descripcion,
                                  tipo, estado, en_garantia, service_nombre,
                                  service_ingreso, created_at, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    ''', (nro, d['equipo_id'], d.get('empleado_id'), d['descripcion'],
          d.get('tipo'), d.get('estado', 'abierto'), d.get('en_garantia', 0),
          d.get('service_nombre'), d.get('service_ingreso'), now(), now()))
    # si el equipo va a reparación, actualizar estado
    if d.get('estado') in ('abierto', 'en_service'):
        db.execute("UPDATE equipos_cel SET estado='reparacion', updated_at=? WHERE id=?",
                   (now(), d['equipo_id']))
    return jsonify({'ok': True, 'nro_ticket': nro}), 201

@cel_bp.route('/api/tickets/<int:tid>', methods=['PUT'])
@login_required
def editar_ticket(tid):
    d = request.json
    db = get_db()
    db.execute('''
        UPDATE tickets_cel SET estado=?, service_nombre=?, service_ingreso=?,
               service_egreso=?, costo=?, resolucion=?, updated_at=?
        WHERE id=?
    ''', (d.get('estado'), d.get('service_nombre'), d.get('service_ingreso'),
          d.get('service_egreso'), d.get('costo'), d.get('resolucion'),
          now(), tid))
    # si se cierra el ticket, volver el equipo a stock o asignado
    if d.get('estado') == 'cerrado':
        ticket = db.execute('SELECT equipo_id FROM tickets_cel WHERE id=?', (tid,)).fetchone()
        if ticket:
            asig = db.execute(
                'SELECT id FROM asignaciones_cel WHERE equipo_id=? AND fecha_hasta IS NULL',
                (ticket['equipo_id'],)
            ).fetchone()
            nuevo_estado = 'asignado' if asig else 'stock'
            db.execute("UPDATE equipos_cel SET estado=?, updated_at=? WHERE id=?",
                       (nuevo_estado, now(), ticket['equipo_id']))
    return jsonify({'ok': True})

# ════════════════════════════════════════════════════════════
#  STATS para dashboard
# ════════════════════════════════════════════════════════════

@cel_bp.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    db = get_db()
    total     = db.execute("SELECT COUNT(*) as c FROM equipos_cel").fetchone()['c']
    asignados = db.execute("SELECT COUNT(*) as c FROM equipos_cel WHERE estado='asignado'").fetchone()['c']
    reparacion= db.execute("SELECT COUNT(*) as c FROM equipos_cel WHERE estado='reparacion'").fetchone()['c']
    stock     = db.execute("SELECT COUNT(*) as c FROM equipos_cel WHERE estado='stock'").fetchone()['c']
    t_abiertos= db.execute("SELECT COUNT(*) as c FROM tickets_cel WHERE estado != 'cerrado'").fetchone()['c']
    return jsonify({
        'total': total,
        'asignados': asignados,
        'reparacion': reparacion,
        'stock': stock,
        'tickets_abiertos': t_abiertos
    })
