from flask import render_template, request, jsonify, session
from datetime import datetime
from functools import wraps
import turso
from . import tele_bp

# ── Helpers ──────────────────────────────────────────────────

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

@tele_bp.route('/')
def index():
    if not session.get('user_id'):
        from flask import redirect, url_for
        return redirect(url_for('login'))
    return render_template('telemetria/index.html')

# ════════════════════════════════════════════════════════════
#  MÓDEMS
# ════════════════════════════════════════════════════════════

@tele_bp.route('/api/modems', methods=['GET'])
@login_required
def get_modems():
    db = get_db()
    rows = db.execute('''
        SELECT m.*,
               p.denominacion  AS perf_nombre,
               p.zona          AS perf_zona,
               p.calle         AS perf_calle,
               lt.tipo_sim     AS sim_tipo,
               lt.numero       AS sim_numero,
               lt.operadora    AS sim_operadora,
               lt.id           AS linea_tel_id
        FROM modems_telemetria m
        LEFT JOIN perforaciones p  ON p.id = m.perforacion_id
        LEFT JOIN lineas_telemetria lt ON lt.modem_id = m.id AND lt.estado = 'activa'
        ORDER BY m.tag_tablero
    ''').fetchall()
    return jsonify([dict(r) for r in rows])

@tele_bp.route('/api/modems/<int:mid>', methods=['GET'])
@login_required
def get_modem(mid):
    db = get_db()
    m = db.execute('''
        SELECT m.*,
               p.denominacion AS perf_nombre,
               p.zona         AS perf_zona,
               p.calle        AS perf_calle,
               p.marca        AS bomba_marca,
               p.modelo       AS bomba_modelo
        FROM modems_telemetria m
        LEFT JOIN perforaciones p ON p.id = m.perforacion_id
        WHERE m.id = ?
    ''', (mid,)).fetchone()
    if not m:
        return jsonify({'error': 'No encontrado'}), 404

    sensores = db.execute(
        'SELECT * FROM sensores WHERE modem_id=? ORDER BY canal', (mid,)
    ).fetchall()

    lineas = db.execute(
        'SELECT * FROM lineas_telemetria WHERE modem_id=? ORDER BY created_at DESC', (mid,)
    ).fetchall()

    intervenciones = db.execute(
        'SELECT * FROM intervenciones_telemetria WHERE modem_id=? ORDER BY fecha DESC', (mid,)
    ).fetchall()

    return jsonify({
        'modem': dict(m),
        'sensores': [dict(s) for s in sensores],
        'lineas': [dict(l) for l in lineas],
        'intervenciones': [dict(i) for i in intervenciones]
    })

@tele_bp.route('/api/modems', methods=['POST'])
@login_required
def crear_modem():
    d = request.json
    db = get_db()
    db.execute('''
        INSERT INTO modems_telemetria (marca, modelo, nro_serie, imei, firmware,
                                       ip_asignada, tag_tablero, perforacion_id,
                                       estado, fecha_instalacion, garantia_hasta,
                                       observaciones, created_at, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', (d['marca'], d['modelo'], d.get('nro_serie'), d.get('imei'),
          d.get('firmware'), d.get('ip_asignada'), d['tag_tablero'],
          d.get('perforacion_id'), d.get('estado', 'activo'),
          d.get('fecha_instalacion'), d.get('garantia_hasta'),
          d.get('observaciones'), now(), now()))
    return jsonify({'ok': True}), 201

@tele_bp.route('/api/modems/<int:mid>', methods=['PUT'])
@login_required
def editar_modem(mid):
    d = request.json
    db = get_db()
    db.execute('''
        UPDATE modems_telemetria SET marca=?, modelo=?, nro_serie=?, imei=?,
               firmware=?, ip_asignada=?, tag_tablero=?, perforacion_id=?,
               estado=?, fecha_instalacion=?, garantia_hasta=?,
               observaciones=?, updated_at=?
        WHERE id=?
    ''', (d['marca'], d['modelo'], d.get('nro_serie'), d.get('imei'),
          d.get('firmware'), d.get('ip_asignada'), d['tag_tablero'],
          d.get('perforacion_id'), d.get('estado', 'activo'),
          d.get('fecha_instalacion'), d.get('garantia_hasta'),
          d.get('observaciones'), now(), mid))
    return jsonify({'ok': True})

@tele_bp.route('/api/modems/<int:mid>/ultimo_contacto', methods=['POST'])
@login_required
def actualizar_contacto(mid):
    """Actualiza timestamp de último contacto (puede llamarse desde scripts externos)"""
    db = get_db()
    db.execute('UPDATE modems_telemetria SET ultimo_contacto=? WHERE id=?', (now(), mid))
    return jsonify({'ok': True})

# ════════════════════════════════════════════════════════════
#  SENSORES
# ════════════════════════════════════════════════════════════

@tele_bp.route('/api/sensores', methods=['GET'])
@login_required
def get_sensores():
    db = get_db()
    rows = db.execute('''
        SELECT s.*,
               m.tag_tablero,
               m.marca    AS modem_marca,
               m.modelo   AS modem_modelo,
               p.denominacion AS perf_nombre,
               p.zona         AS perf_zona
        FROM sensores s
        JOIN modems_telemetria m ON m.id = s.modem_id
        LEFT JOIN perforaciones p ON p.id = m.perforacion_id
        WHERE s.activo = 1
        ORDER BY m.tag_tablero, s.canal
    ''').fetchall()
    return jsonify([dict(r) for r in rows])

@tele_bp.route('/api/modems/<int:mid>/sensores', methods=['GET'])
@login_required
def get_sensores_modem(mid):
    db = get_db()
    rows = db.execute(
        'SELECT * FROM sensores WHERE modem_id=? ORDER BY canal', (mid,)
    ).fetchall()
    return jsonify([dict(r) for r in rows])

@tele_bp.route('/api/modems/<int:mid>/sensores', methods=['POST'])
@login_required
def crear_sensor(mid):
    d = request.json
    db = get_db()
    db.execute('''
        INSERT INTO sensores (modem_id, canal, tipo, descripcion, tipo_senal,
                               rango_min, rango_max, unidad,
                               alarma_min, alarma_max, activo, created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    ''', (mid, d['canal'], d['tipo'], d.get('descripcion'),
          d.get('tipo_senal'), d.get('rango_min'), d.get('rango_max'),
          d.get('unidad'), d.get('alarma_min'), d.get('alarma_max'),
          d.get('activo', 1), now()))
    return jsonify({'ok': True}), 201

@tele_bp.route('/api/sensores/<int:sid>', methods=['PUT'])
@login_required
def editar_sensor(sid):
    d = request.json
    db = get_db()
    db.execute('''
        UPDATE sensores SET canal=?, tipo=?, descripcion=?, tipo_senal=?,
               rango_min=?, rango_max=?, unidad=?,
               alarma_min=?, alarma_max=?, activo=?
        WHERE id=?
    ''', (d['canal'], d['tipo'], d.get('descripcion'), d.get('tipo_senal'),
          d.get('rango_min'), d.get('rango_max'), d.get('unidad'),
          d.get('alarma_min'), d.get('alarma_max'), d.get('activo', 1), sid))
    return jsonify({'ok': True})

@tele_bp.route('/api/sensores/<int:sid>', methods=['DELETE'])
@login_required
def desactivar_sensor(sid):
    db = get_db()
    db.execute('UPDATE sensores SET activo=0 WHERE id=?', (sid,))
    return jsonify({'ok': True})

# ════════════════════════════════════════════════════════════
#  LÍNEAS SIM TELEMETRÍA
# ════════════════════════════════════════════════════════════

@tele_bp.route('/api/lineas', methods=['GET'])
@login_required
def get_lineas():
    db = get_db()
    rows = db.execute('''
        SELECT lt.*,
               m.tag_tablero,
               m.marca  AS modem_marca,
               m.modelo AS modem_modelo,
               p.denominacion AS perf_nombre
        FROM lineas_telemetria lt
        LEFT JOIN modems_telemetria m ON m.id = lt.modem_id
        LEFT JOIN perforaciones p ON p.id = m.perforacion_id
        ORDER BY lt.tipo_sim, lt.numero
    ''').fetchall()
    return jsonify([dict(r) for r in rows])

@tele_bp.route('/api/lineas', methods=['POST'])
@login_required
def crear_linea():
    d = request.json
    db = get_db()
    db.execute('''
        INSERT INTO lineas_telemetria (numero, tipo_sim, operadora, iccid,
                                       apn, ip_sim, modem_id, estado,
                                       fecha_alta, observaciones, created_at, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    ''', (d.get('numero'), d['tipo_sim'], d.get('operadora'), d.get('iccid'),
          d.get('apn'), d.get('ip_sim'), d.get('modem_id'),
          d.get('estado', 'activa'), d.get('fecha_alta', today()),
          d.get('observaciones'), now(), now()))
    return jsonify({'ok': True}), 201

@tele_bp.route('/api/lineas/<int:lid>', methods=['PUT'])
@login_required
def editar_linea(lid):
    d = request.json
    db = get_db()
    db.execute('''
        UPDATE lineas_telemetria SET numero=?, tipo_sim=?, operadora=?, iccid=?,
               apn=?, ip_sim=?, modem_id=?, estado=?,
               fecha_alta=?, observaciones=?, updated_at=?
        WHERE id=?
    ''', (d.get('numero'), d['tipo_sim'], d.get('operadora'), d.get('iccid'),
          d.get('apn'), d.get('ip_sim'), d.get('modem_id'),
          d.get('estado', 'activa'), d.get('fecha_alta'),
          d.get('observaciones'), now(), lid))
    return jsonify({'ok': True})

# ════════════════════════════════════════════════════════════
#  INTERVENCIONES
# ════════════════════════════════════════════════════════════

@tele_bp.route('/api/modems/<int:mid>/intervenciones', methods=['POST'])
@login_required
def crear_intervencion(mid):
    d = request.json
    db = get_db()
    db.execute('''
        INSERT INTO intervenciones_telemetria (modem_id, tipo, descripcion,
                                               tecnico, fecha, costo, created_at)
        VALUES (?,?,?,?,?,?,?)
    ''', (mid, d['tipo'], d['descripcion'], d.get('tecnico'),
          d.get('fecha', today()), d.get('costo'), now()))
    return jsonify({'ok': True}), 201

# ════════════════════════════════════════════════════════════
#  PERFORACIONES (solo lectura, para el selector)
# ════════════════════════════════════════════════════════════

@tele_bp.route('/api/perforaciones', methods=['GET'])
@login_required
def get_perforaciones():
    """Lista de perforaciones de POZO/MGR para usar en selectores"""
    db = get_db()
    rows = db.execute('''
        SELECT id, denominacion, zona, calle
        FROM perforaciones
        ORDER BY zona, denominacion
    ''').fetchall()
    return jsonify([dict(r) for r in rows])

# ════════════════════════════════════════════════════════════
#  STATS para dashboard
# ════════════════════════════════════════════════════════════

@tele_bp.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    db = get_db()
    total    = db.execute("SELECT COUNT(*) as c FROM modems_telemetria WHERE estado='activo'").fetchone()['c']
    kite     = db.execute("SELECT COUNT(*) as c FROM lineas_telemetria WHERE tipo_sim='kite' AND estado='activa'").fetchone()['c']
    normal   = db.execute("SELECT COUNT(*) as c FROM lineas_telemetria WHERE tipo_sim='normal' AND estado='activa'").fetchone()['c']
    sin_sim  = db.execute('''
        SELECT COUNT(*) as c FROM modems_telemetria m
        WHERE m.estado='activo'
        AND NOT EXISTS (SELECT 1 FROM lineas_telemetria lt WHERE lt.modem_id=m.id AND lt.estado='activa')
    ''').fetchone()['c']
    sensores = db.execute("SELECT COUNT(*) as c FROM sensores WHERE activo=1").fetchone()['c']
    return jsonify({
        'total_modems': total,
        'lineas_kite': kite,
        'lineas_normal': normal,
        'sin_sim': sin_sim,
        'sensores_activos': sensores
    })
