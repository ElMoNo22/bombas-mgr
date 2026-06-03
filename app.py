import os, json, re
import urllib.request
import urllib.error
import turso as db_driver
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'bombas-mgr-secret-2024')

# ── DB CONNECTION ──
def norm_fecha(s):
    """Normalize date to yyyy-mm-dd internally (for correct DB sorting)"""
    if not s: return None
    s = str(s).strip()
    if s in ('nan','NaT','None',''): return None
    m = re.match(r'^(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})$', s)
    if m: return f"{m.group(3)}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}"
    if re.match(r'^\d{4}-\d{2}-\d{2}$', s): return s
    return s

def norm_neq(v):
    """Normaliza número de equipo: quita .0 y espacios."""
    if v is None: return ''
    s = str(v).strip()
    if s.endswith('.0'): s = s[:-2]
    return s

def check_garantia(numero_equipo, conn):
    """Devuelve la reparación más reciente entregada dentro de los 6 meses, o None."""
    from datetime import date, timedelta
    hoy = date.today()
    hace_6m = (hoy - timedelta(days=183)).isoformat()
    neq = norm_neq(numero_equipo)
    cur = conn.execute("""
        SELECT id, fecha_entrega, proveedor, remito_entrega, descripcion
        FROM reparaciones
        WHERE REPLACE(numero_equipo, '.0', '') = ?
        AND estado = 'Entregada'
        AND fecha_entrega IS NOT NULL
        AND fecha_entrega >= ?
        ORDER BY fecha_entrega DESC LIMIT 1
    """, (neq, hace_6m))
    return fetchone_dict(cur)

def get_db():
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
    if row is None: return None
    try:
        return dict(row)
    except Exception:
        return {k: row[k] for k in row.keys()}

def init_db():
    conn = get_db()
    tables = [
        '''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL, role TEXT DEFAULT 'viewer')''',
        '''CREATE TABLE IF NOT EXISTS bombas (
            id INTEGER PRIMARY KEY AUTOINCREMENT, n_equipo TEXT UNIQUE,
            tag TEXT, tag_extraviado TEXT, marca TEXT, modelo TEXT,
            hp REAL, kw REAL, amperes TEXT, serie TEXT,
            peso_kg REAL, largo_mm REAL, salida TEXT, tazones TEXT,
            sap_id TEXT, id_estadio TEXT, observaciones TEXT, ubicacion_fisica TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''',
        '''CREATE TABLE IF NOT EXISTS perforaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            calle TEXT, entre TEXT, y_col TEXT, zona TEXT, bombeo TEXT,
            denominacion TEXT, prof_trabajo_mts REAL, tipo_cañeria TEXT,
            mts_cañeria TEXT, nivel_estatico REAL, nivel_dinamico REAL,
            Q_m3h REAL, H_mca REAL, candado TEXT, observaciones TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''',
        '''CREATE TABLE IF NOT EXISTS asignaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bomba_id INTEGER, perforacion_id INTEGER,
            estado TEXT DEFAULT 'Desmontado',
            fecha_montaje TEXT, fecha_desmontaje TEXT,
            notificada_por TEXT, relevado_el TEXT, notas TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''',
        '''CREATE TABLE IF NOT EXISTS catalogo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca TEXT, modelo TEXT, para TEXT, hp REAL,
            etapas TEXT, descarga TEXT, largo_mm TEXT, curva_json TEXT)''',
        # ── REPARACIONES ──
        '''CREATE TABLE IF NOT EXISTS reparaciones (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_envio          TEXT,
            remito               TEXT,
            proveedor            TEXT,
            descripcion          TEXT,
            servicio             TEXT,
            tag_actual           TEXT,
            tag_reemplazado      TEXT,
            numero_equipo        TEXT,
            marca                TEXT,
            modelo               TEXT,
            hp                   TEXT,
            kw                   TEXT,
            amperes              TEXT,
            serie                TEXT,
            centro               TEXT,
            ceco                 TEXT,
            referencia           TEXT,
            presupuesto          TEXT,
            fecha_cotizacion     TEXT,
            costo_usd            REAL,
            estado_autorizacion  TEXT,
            fecha_autorizacion   TEXT,
            om                   TEXT,
            solped               TEXT,
            fecha_solped         TEXT,
            liberacion           TEXT,
            fecha_liberacion     TEXT,
            estadio              TEXT,
            gcp                  TEXT,
            nota_justificacion   TEXT,
            np                   TEXT,
            fecha_np_generacion  TEXT,
            fecha_np_envio_prov  TEXT,
            estado_entrega       TEXT,
            fecha_entrega        TEXT,
            remito_entrega       TEXT,
            observaciones        TEXT,
            responsable          TEXT,
            estado               TEXT DEFAULT 'En reparación',
            usuario_registro     TEXT,
            sin_desmontaje       INTEGER DEFAULT 0,
            dias_limite_preventivo INTEGER DEFAULT 90,
            created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''',
        # ── HISTORIAL DE TAGS ──
        '''CREATE TABLE IF NOT EXISTS tags_historial (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            bomba_id    INTEGER NOT NULL,
            n_equipo    TEXT NOT NULL,
            tag         TEXT NOT NULL,
            fecha_desde TEXT,
            fecha_hasta TEXT,
            motivo      TEXT,
            usuario     TEXT,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP)'''
    ]
    for t in tables:
        try:
            conn.execute(t)
            db_commit(conn)
        except Exception as e:
            if 'already exists' not in str(e).lower():
                raise
    # Migrations
    for migration in [
        'ALTER TABLE bombas ADD COLUMN ubicacion_fisica TEXT',
        'ALTER TABLE reparaciones ADD COLUMN sin_desmontaje INTEGER DEFAULT 0',
        'ALTER TABLE reparaciones ADD COLUMN dias_limite_preventivo INTEGER DEFAULT 90',
    ]:
        try:
            conn.execute(migration)
            db_commit(conn)
        except Exception:
            pass
    # Clean .0 suffix from n_equipo (imported from Excel as float)
    try:
        conn.execute("""
            UPDATE bombas SET n_equipo = REPLACE(n_equipo, '.0', '')
            WHERE n_equipo LIKE '%.0'
        """)
        db_commit(conn)
    except Exception:
        pass
    # Migrar tag_extraviado existente → tags_historial (solo si no fue migrado aún)
    try:
        cur_check = conn.execute('SELECT COUNT(*) as n FROM tags_historial')
        already = fetchone_dict(cur_check)
        if already and already['n'] == 0:
            cur_b = conn.execute(
                "SELECT id, n_equipo, tag, tag_extraviado FROM bombas WHERE tag_extraviado IS NOT NULL AND tag_extraviado != ''"
            )
            bombas_con_tag_viejo = fetchall_dicts(cur_b)
            for b in bombas_con_tag_viejo:
                # Puede haber varios tags separados por " / "
                tags_viejos = [t.strip() for t in str(b['tag_extraviado']).split('/') if t.strip()]
                for tag_v in tags_viejos:
                    conn.execute(
                        '''INSERT INTO tags_historial (bomba_id, n_equipo, tag, fecha_desde, fecha_hasta, motivo, usuario)
                           VALUES (?, ?, ?, NULL, NULL, 'Migrado desde tag_extraviado', 'sistema')''',
                        (b['id'], b['n_equipo'] or '', tag_v)
                    )
            db_commit(conn)
    except Exception:
        pass

    cur = conn.execute('SELECT id FROM users WHERE username = ?', ('admin',))
    if not fetchone_dict(cur):
        conn.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                   ('admin', generate_password_hash('bombas2024'), 'admin'))
        db_commit(conn)
    conn.close()

# ── AUTH DECORATORS ──
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'error': 'No autorizado'}), 401
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated

def editor_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'No autorizado'}), 401
        if session.get('role') not in ('editor', 'admin'):
            return jsonify({'error': 'Se requiere rol editor o admin'}), 403
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'No autorizado'}), 401
        if session.get('role') != 'admin':
            return jsonify({'error': 'Se requiere rol admin'}), 403
        return f(*args, **kwargs)
    return decorated

# ── PAGES ──
@app.route('/')
@login_required
def index():
    return render_template('index.html', username=session.get('username'),
        role=session.get('role'), user_id=session.get('user_id', 0))

@app.route('/login', methods=['GET'])
def login_page():
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username','').strip()
    password = data.get('password','')
    conn = get_db()
    cur = conn.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = fetchone_dict(cur)
    conn.close()
    if user and check_password_hash(user['password_hash'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        return jsonify({'ok': True, 'username': user['username'], 'role': user['role']})
    return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

# ── BOMBAS ──
@app.route('/api/bombas', methods=['GET'])
@login_required
def get_bombas():
    conn = get_db()
    cur = conn.execute('''
        SELECT b.*, a.estado as estado_actual, a.fecha_montaje, a.fecha_desmontaje,
               a.id as asignacion_id, p.calle, p.entre, p.y_col, p.zona, p.id as perforacion_id,
               CASE WHEN r.id IS NOT NULL THEN 1 ELSE 0 END as tiene_rep_activa,
               r.id as rep_activa_id, r.proveedor as rep_proveedor, r.estado as rep_estado
        FROM bombas b
        LEFT JOIN asignaciones a ON a.bomba_id = b.id
            AND a.id = (
                SELECT id FROM asignaciones WHERE bomba_id = b.id
                ORDER BY CASE WHEN estado = 'Montado' THEN 0 ELSE 1 END,
                CASE WHEN COALESCE(fecha_desmontaje,fecha_montaje) IS NULL THEN 1 ELSE 0 END,
                COALESCE(fecha_desmontaje,fecha_montaje) DESC, id DESC LIMIT 1
            )
        LEFT JOIN perforaciones p ON a.perforacion_id = p.id
        LEFT JOIN reparaciones r ON r.numero_equipo = b.n_equipo
            AND r.estado NOT IN ('Entregada', 'Cancelada')
            AND r.id = (
                SELECT id FROM reparaciones
                WHERE numero_equipo = b.n_equipo
                AND estado NOT IN ('Entregada', 'Cancelada')
                ORDER BY id DESC LIMIT 1
            )
        ORDER BY b.marca, b.modelo
    ''')
    rows = fetchall_dicts(cur)
    # Si tiene reparación activa y no está montada, pisar ubicacion_fisica
    for r in rows:
        if r.get('tiene_rep_activa') and r.get('estado_actual') != 'Montado':
            r['ubicacion_fisica'] = 'En reparación'
    # Agregar info de garantía
    from datetime import date, timedelta
    hoy = date.today()
    hace_6m = (hoy - timedelta(days=183)).isoformat()
    cur_g = conn.execute("""
        SELECT numero_equipo, fecha_entrega, id as rep_id
        FROM reparaciones
        WHERE estado = 'Entregada'
        AND fecha_entrega IS NOT NULL
        AND fecha_entrega >= ?
    """, (hace_6m,))
    # Normalize: strip trailing .0 from both sides for matching (usa norm_neq global)
    en_garantia = {norm_neq(r['numero_equipo']): r for r in fetchall_dicts(cur_g)}
    for r in rows:
        g = en_garantia.get(norm_neq(r.get('n_equipo')))
        if g:
            r['en_garantia'] = True
            r['garantia_hasta'] = g['fecha_entrega']  # +6m calculado en frontend
            r['garantia_rep_id'] = g['rep_id']
        else:
            r['en_garantia'] = False
    conn.close()
    return jsonify(rows)

@app.route('/api/bombas/<int:bid>', methods=['GET'])
@login_required
def get_bomba(bid):
    conn = get_db()
    cur = conn.execute('SELECT * FROM bombas WHERE id = ?', (bid,))
    bomba = fetchone_dict(cur)
    if not bomba:
        conn.close()
        return jsonify({'error': 'No encontrado'}), 404
    cur2 = conn.execute('''
        SELECT a.*, p.calle, p.entre, p.y_col, p.zona, p.id as perforacion_id
        FROM asignaciones a LEFT JOIN perforaciones p ON a.perforacion_id = p.id
        WHERE a.bomba_id = ?
        ORDER BY CASE WHEN a.estado='Montado' THEN 0 ELSE 1 END,
        CASE WHEN a.fecha_montaje IS NULL THEN 1 ELSE 0 END,
        a.fecha_montaje DESC, a.id DESC
    ''', (bid,))
    bomba['historial'] = fetchall_dicts(cur2)
    # Reparación activa
    neq = norm_neq(bomba.get('n_equipo'))
    cur3 = conn.execute('''
        SELECT * FROM reparaciones
        WHERE REPLACE(numero_equipo,'.0','') = ?
        AND estado NOT IN ('Entregada', 'Cancelada')
        ORDER BY id DESC LIMIT 1
    ''', (neq,))
    rep_activa = fetchone_dict(cur3)
    if rep_activa:
        bomba['rep_activa'] = rep_activa
        if bomba.get('estado_actual') != 'Montado':
            bomba['ubicacion_fisica'] = 'En reparación'
    # Garantía
    from datetime import date, timedelta
    rep_gar = check_garantia(neq, conn)
    if rep_gar:
        fecha_ent = rep_gar.get('fecha_entrega','')
        try:
            hasta = (date.fromisoformat(fecha_ent) + timedelta(days=183)).isoformat()
            dias = (date.fromisoformat(hasta) - date.today()).days
        except:
            hasta = None
            dias = None
        bomba['en_garantia'] = True
        bomba['garantia_hasta'] = fecha_ent
        bomba['garantia_rep_id'] = rep_gar['id']
        bomba['garantia_dias'] = dias
        bomba['garantia_proveedor'] = rep_gar.get('proveedor')
        bomba['garantia_remito'] = rep_gar.get('remito_entrega')
    else:
        bomba['en_garantia'] = False
    conn.close()
    return jsonify(bomba)

@app.route('/api/bombas', methods=['POST'])
@editor_required
def create_bomba():
    data = request.get_json()
    fields = ['n_equipo','tag','tag_extraviado','marca','modelo','hp','kw','amperes',
              'serie','peso_kg','largo_mm','salida','tazones','sap_id','id_estadio','observaciones','ubicacion_fisica']
    vals = [data.get(f) for f in fields]
    conn = get_db()
    try:
        conn.execute(f'INSERT INTO bombas ({",".join(fields)}) VALUES ({",".join(["?"]*len(fields))})', vals)
        db_commit(conn)
        cur = conn.execute('SELECT * FROM bombas WHERE n_equipo = ?', (data.get('n_equipo'),))
        row = fetchone_dict(cur)
        conn.close()
        return jsonify(row), 201
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 409

@app.route('/api/bombas/<int:bid>', methods=['PUT'])
@editor_required
def update_bomba(bid):
    data = request.get_json()
    fields = ['n_equipo','tag','tag_extraviado','marca','modelo','hp','kw','amperes',
              'serie','peso_kg','largo_mm','salida','tazones','sap_id','id_estadio','observaciones','ubicacion_fisica']
    sets = ', '.join([f'{f} = ?' for f in fields]) + ', updated_at = CURRENT_TIMESTAMP'
    vals = [data.get(f) for f in fields] + [bid]
    conn = get_db()
    conn.execute(f'UPDATE bombas SET {sets} WHERE id = ?', vals)
    db_commit(conn)
    cur = conn.execute('SELECT * FROM bombas WHERE id = ?', (bid,))
    row = fetchone_dict(cur)
    conn.close()
    return jsonify(row)

@app.route('/api/bombas/<int:bid>/ubicacion', methods=['PATCH'])
@editor_required
def set_ubicacion(bid):
    data = request.get_json()
    ubicacion = data.get('ubicacion_fisica')
    conn = get_db()
    conn.execute('UPDATE bombas SET ubicacion_fisica=?, updated_at=CURRENT_TIMESTAMP WHERE id=?',
                (ubicacion, bid))
    db_commit(conn)
    cur = conn.execute('SELECT * FROM bombas WHERE id=?', (bid,))
    row = fetchone_dict(cur)
    conn.close()
    return jsonify(row)

@app.route('/api/bombas/<int:bid>', methods=['DELETE'])
@admin_required
def delete_bomba(bid):
    conn = get_db()
    conn.execute('DELETE FROM asignaciones WHERE bomba_id = ?', (bid,))
    conn.execute('DELETE FROM bombas WHERE id = ?', (bid,))
    db_commit(conn)
    conn.close()
    return jsonify({'ok': True})

@app.route('/api/bombas/disponibles', methods=['GET'])
@login_required
def get_bombas_disponibles():
    conn = get_db()
    cur = conn.execute('''
        SELECT * FROM bombas WHERE id NOT IN
        (SELECT DISTINCT bomba_id FROM asignaciones WHERE estado = 'Montado')
        ORDER BY marca, modelo, hp
    ''')
    rows = fetchall_dicts(cur)
    conn.close()
    return jsonify(rows)

# ── PERFORACIONES ──
@app.route('/api/perforaciones', methods=['GET'])
@login_required
def get_perforaciones():
    conn = get_db()
    cur = conn.execute('''
        SELECT p.*, b.n_equipo, b.tag, b.marca, b.modelo, b.hp, b.serie, b.amperes,
               a.estado as estado_actual, a.fecha_montaje, a.fecha_desmontaje,
               a.id as asignacion_id, b.id as bomba_id
        FROM perforaciones p
        LEFT JOIN asignaciones a ON a.perforacion_id = p.id
            AND a.id = (
                SELECT id FROM asignaciones WHERE perforacion_id = p.id
                ORDER BY CASE WHEN estado='Montado' THEN 0 ELSE 1 END,
                CASE WHEN COALESCE(fecha_desmontaje,fecha_montaje) IS NULL THEN 1 ELSE 0 END,
                COALESCE(fecha_desmontaje,fecha_montaje) DESC, id DESC LIMIT 1
            )
        LEFT JOIN bombas b ON a.bomba_id = b.id
        ORDER BY p.zona, p.calle, p.y_col
    ''')
    rows = fetchall_dicts(cur)
    conn.close()
    return jsonify(rows)

@app.route('/api/perforaciones/<int:pid>', methods=['GET'])
@login_required
def get_perforacion(pid):
    conn = get_db()
    cur = conn.execute('SELECT * FROM perforaciones WHERE id = ?', (pid,))
    perf = fetchone_dict(cur)
    if not perf:
        conn.close()
        return jsonify({'error': 'No encontrado'}), 404
    cur2 = conn.execute('''
        SELECT a.*, b.n_equipo, b.tag, b.marca, b.modelo, b.hp, b.serie, b.id as bomba_id
        FROM asignaciones a LEFT JOIN bombas b ON a.bomba_id = b.id
        WHERE a.perforacion_id = ?
        ORDER BY CASE WHEN a.estado='Montado' THEN 0 ELSE 1 END,
        CASE WHEN a.fecha_montaje IS NULL THEN 1 ELSE 0 END,
        a.fecha_montaje DESC, a.id DESC
    ''', (pid,))
    perf['historial'] = fetchall_dicts(cur2)
    conn.close()
    return jsonify(perf)

@app.route('/api/perforaciones', methods=['POST'])
@editor_required
def create_perforacion():
    data = request.get_json()
    fields = ['calle','entre','y_col','zona','bombeo','denominacion','prof_trabajo_mts',
              'tipo_cañeria','mts_cañeria','nivel_estatico','nivel_dinamico','Q_m3h','H_mca','candado','observaciones']
    vals = [data.get(f) for f in fields]
    conn = get_db()
    conn.execute(f'INSERT INTO perforaciones ({",".join(fields)}) VALUES ({",".join(["?"]*len(fields))})', vals)
    db_commit(conn)
    cur = conn.execute('SELECT * FROM perforaciones ORDER BY id DESC LIMIT 1')
    row = fetchone_dict(cur)
    conn.close()
    return jsonify(row), 201

@app.route('/api/perforaciones/<int:pid>', methods=['PUT'])
@editor_required
def update_perforacion(pid):
    data = request.get_json()
    fields = ['calle','entre','y_col','zona','bombeo','denominacion','prof_trabajo_mts',
              'tipo_cañeria','mts_cañeria','nivel_estatico','nivel_dinamico','Q_m3h','H_mca','candado','observaciones']
    sets = ', '.join([f'{f} = ?' for f in fields]) + ', updated_at = CURRENT_TIMESTAMP'
    vals = [data.get(f) for f in fields] + [pid]
    conn = get_db()
    conn.execute(f'UPDATE perforaciones SET {sets} WHERE id = ?', vals)
    db_commit(conn)
    cur = conn.execute('SELECT * FROM perforaciones WHERE id = ?', (pid,))
    row = fetchone_dict(cur)
    conn.close()
    return jsonify(row)

@app.route('/api/perforaciones/<int:pid>', methods=['DELETE'])
@admin_required
def delete_perforacion(pid):
    conn = get_db()
    conn.execute('DELETE FROM asignaciones WHERE perforacion_id = ?', (pid,))
    conn.execute('DELETE FROM perforaciones WHERE id = ?', (pid,))
    db_commit(conn)
    conn.close()
    return jsonify({'ok': True})

# ══════════════════════════════════════════════════════════════════
# ── VALIDACIONES DE NEGOCIO ──
# ══════════════════════════════════════════════════════════════════

def _get_bomba_estado(bomba_id, conn):
    """
    Devuelve un dict con el estado actual completo de una bomba:
      montada_en   : dict con info de la perforación si está Montado, o None
      rep_activa   : dict con info de la reparación activa, o None
      preventivo   : dict si tiene mantenimiento preventivo activo, o None
    """
    # ¿Está montada?
    cur = conn.execute('''
        SELECT a.id as asig_id, a.fecha_montaje, a.sin_desmontaje,
               p.id as perf_id, p.calle, p.entre, p.y_col, p.zona
        FROM asignaciones a
        JOIN perforaciones p ON a.perforacion_id = p.id
        WHERE a.bomba_id = ? AND a.estado = 'Montado'
        ORDER BY a.fecha_montaje DESC LIMIT 1
    ''', (bomba_id,))
    montada_en = fetchone_dict(cur)

    # ¿Tiene reparación activa?
    cur2 = conn.execute('''
        SELECT r.id, r.proveedor, r.estado, r.fecha_envio,
               r.sin_desmontaje, r.dias_limite_preventivo, r.fecha_envio as f_envio
        FROM reparaciones r
        JOIN bombas b ON REPLACE(r.numero_equipo, '.0', '') = b.n_equipo
        WHERE b.id = ? AND r.estado NOT IN ('Entregada', 'Cancelada')
        ORDER BY r.id DESC LIMIT 1
    ''', (bomba_id,))
    rep_activa = fetchone_dict(cur2)

    # Mantenimiento preventivo: rep activa con sin_desmontaje=1
    preventivo = None
    if rep_activa and rep_activa.get('sin_desmontaje'):
        from datetime import date, timedelta
        try:
            dias = int(rep_activa.get('dias_limite_preventivo') or 90)
            f_envio = rep_activa.get('f_envio')
            if f_envio:
                desde = date.fromisoformat(str(f_envio))
                vence = desde + timedelta(days=dias)
                dias_restantes = (vence - date.today()).days
                preventivo = {
                    'rep_id': rep_activa['id'],
                    'proveedor': rep_activa['proveedor'],
                    'fecha_envio': f_envio,
                    'vence': vence.isoformat(),
                    'dias_restantes': dias_restantes,
                    'vencido': dias_restantes < 0,
                }
        except Exception:
            pass

    return {
        'montada_en': montada_en,
        'rep_activa': rep_activa,
        'preventivo': preventivo,
    }


def _validar_montar(bomba_id, perforacion_id, conn):
    """
    Valida si es posible montar una bomba en una perforación.
    Retorna (ok, mensaje_error) — si ok=True, mensaje_error=None.
    """
    estado = _get_bomba_estado(bomba_id, conn)

    # Ya está montada en otro lugar
    if estado['montada_en']:
        m = estado['montada_en']
        lugar = f"calle {m['calle']} y {m['y_col']}"
        if m.get('zona'):
            lugar += f" ({m['zona']})"
        desde = f" desde {m['fecha_montaje']}" if m.get('fecha_montaje') else ''
        return False, f"La bomba ya está montada en {lugar}{desde}. Desmontala primero."

    # Está en reparación activa (sin preventivo)
    if estado['rep_activa'] and not estado['rep_activa'].get('sin_desmontaje'):
        r = estado['rep_activa']
        prov = r.get('proveedor') or 'taller'
        fecha = f" desde {r['fecha_envio']}" if r.get('fecha_envio') else ''
        return False, f"La bomba está en reparación con {prov}{fecha} (estado: {r['estado']}). Cerrá la reparación primero."

    # La perforación ya tiene otra bomba montada
    cur = conn.execute('''
        SELECT a.id, b.n_equipo, b.tag, b.marca, b.modelo
        FROM asignaciones a JOIN bombas b ON a.bomba_id = b.id
        WHERE a.perforacion_id = ? AND a.estado = 'Montado'
        LIMIT 1
    ''', (perforacion_id,))
    otra = fetchone_dict(cur)
    if otra:
        desc = f"equipo {otra['n_equipo']}" if otra.get('n_equipo') else f"tag {otra.get('tag', '?')}"
        return False, f"La perforación ya tiene montada la bomba {desc} ({otra.get('marca', '')} {otra.get('modelo', '')}). Desmontala primero."

    return True, None


def _validar_reparacion(bomba_id, sin_desmontaje, conn):
    """
    Valida si es posible registrar una reparación para una bomba.
    Retorna (ok, mensaje_error, es_advertencia).
    es_advertencia=True → el frontend debe pedir confirmación, no bloquear.
    """
    estado = _get_bomba_estado(bomba_id, conn)

    # Está montada y NO es preventivo → bloqueo
    if estado['montada_en'] and not sin_desmontaje:
        m = estado['montada_en']
        lugar = f"calle {m['calle']} y {m['y_col']}"
        if m.get('zona'):
            lugar += f" ({m['zona']})"
        desde = f" desde {m['fecha_montaje']}" if m.get('fecha_montaje') else ''
        return False, f"La bomba está montada en {lugar}{desde}. Desmontala antes de enviarla a reparar.", False

    # Ya tiene otra reparación activa → advertencia (puede haber 2 presupuestos)
    if estado['rep_activa']:
        r = estado['rep_activa']
        prov = r.get('proveedor') or 'otro taller'
        return False, f"La bomba ya tiene una reparación activa con {prov} (estado: {r['estado']}). ¿Confirmás que querés registrar otra?", True

    return True, None, False


# ── ASIGNACIONES ──
@app.route('/api/asignaciones', methods=['POST'])
@editor_required
def create_asignacion():
    data = request.get_json()
    bomba_id = data.get('bomba_id')
    perforacion_id = data.get('perforacion_id')
    if not bomba_id or not perforacion_id:
        return jsonify({'error': 'bomba_id y perforacion_id requeridos'}), 400

    conn = get_db()
    try:
        ok, error = _validar_montar(bomba_id, perforacion_id, conn)
        if not ok:
            return jsonify({'error': error, 'code': 'VALIDACION'}), 409

        conn.execute('''
            INSERT INTO asignaciones (bomba_id, perforacion_id, estado, fecha_montaje, fecha_desmontaje, notificada_por, notas)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (bomba_id, perforacion_id, data.get('estado', 'Montado'),
              norm_fecha(data.get('fecha_montaje')), norm_fecha(data.get('fecha_desmontaje')),
              data.get('notificada_por'), data.get('notas')))
        if data.get('estado', 'Montado') == 'Montado':
            conn.execute("UPDATE bombas SET ubicacion_fisica='Montada' WHERE id=?", (bomba_id,))
        db_commit(conn)
        cur2 = conn.execute('''
            SELECT a.*, b.n_equipo, b.tag, b.marca, b.modelo, b.hp, p.calle, p.y_col, p.zona
            FROM asignaciones a JOIN bombas b ON a.bomba_id=b.id JOIN perforaciones p ON a.perforacion_id=p.id
            ORDER BY a.id DESC LIMIT 1
        ''')
        row = fetchone_dict(cur2)
        return jsonify(row), 201
    finally:
        conn.close()

@app.route('/api/asignaciones/<int:aid>', methods=['PUT'])
@editor_required
def update_asignacion(aid):
    data = request.get_json()
    fields = ['estado','fecha_montaje','fecha_desmontaje','notificada_por','relevado_el','notas']
    sets = ', '.join([f'{f} = ?' for f in fields]) + ', updated_at = CURRENT_TIMESTAMP'
    raw = [data.get(f) for f in fields]
    raw[1] = norm_fecha(raw[1])
    raw[2] = norm_fecha(raw[2])
    vals = raw + [aid]
    conn = get_db()
    conn.execute(f'UPDATE asignaciones SET {sets} WHERE id = ?', vals)
    db_commit(conn)
    cur = conn.execute('SELECT * FROM asignaciones WHERE id = ?', (aid,))
    row = fetchone_dict(cur)
    conn.close()
    return jsonify(row)

@app.route('/api/asignaciones/<int:aid>/desmontar', methods=['POST'])
@editor_required
def desmontar(aid):
    data = request.get_json() or {}
    conn = get_db()
    conn.execute('''UPDATE asignaciones SET estado='Desmontado', fecha_desmontaje=?,
        notas=COALESCE(?,notas), updated_at=CURRENT_TIMESTAMP WHERE id=?''',
        (norm_fecha(data.get('fecha_desmontaje')), data.get('notas'), aid))
    cur_a = conn.execute('SELECT bomba_id FROM asignaciones WHERE id=?', (aid,))
    asig = fetchone_dict(cur_a)
    if asig:
        conn.execute("UPDATE bombas SET ubicacion_fisica=NULL WHERE id=?", (asig['bomba_id'],))
    db_commit(conn)
    cur = conn.execute('SELECT * FROM asignaciones WHERE id = ?', (aid,))
    row = fetchone_dict(cur)
    conn.close()
    return jsonify(row)

@app.route('/api/asignaciones/<int:aid>', methods=['DELETE'])
@admin_required
def delete_asignacion(aid):
    conn = get_db()
    conn.execute('DELETE FROM asignaciones WHERE id = ?', (aid,))
    db_commit(conn)
    conn.close()
    return jsonify({'ok': True})

# ── CATÁLOGO ──
@app.route('/api/catalogo', methods=['GET'])
@login_required
def get_catalogo():
    conn = get_db()
    cur = conn.execute('SELECT * FROM catalogo ORDER BY hp, modelo')
    rows = fetchall_dicts(cur)
    conn.close()
    result = []
    for r in rows:
        r['curva'] = json.loads(r['curva_json']) if r.get('curva_json') else []
        del r['curva_json']
        result.append(r)
    return jsonify(result)

@app.route('/api/import/catalogo', methods=['POST'])
@admin_required
def import_catalogo():
    data = request.get_json()
    records = data.get('records', [])
    conn = get_db()
    conn.execute('DELETE FROM catalogo')
    for r in records:
        conn.execute('INSERT INTO catalogo (marca,modelo,para,hp,etapas,descarga,largo_mm,curva_json) VALUES (?,?,?,?,?,?,?,?)',
            (r.get('marca'),r.get('modelo'),r.get('para'),r.get('hp'),
             r.get('etapas'),r.get('descarga'),r.get('largo_mm'),json.dumps(r.get('curva',[]))))
    db_commit(conn)
    cur = conn.execute('SELECT COUNT(*) as n FROM catalogo')
    count = fetchone_dict(cur)['n']
    conn.close()
    return jsonify({'ok': True, 'count': count})

# ── STATS ──
@app.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    conn = get_db()
    def scalar(sql, params=()):
        cur = conn.execute(sql, params)
        row = fetchone_dict(cur)
        return list(row.values())[0] if row else 0
    def many(sql):
        cur = conn.execute(sql)
        return fetchall_dicts(cur)
    stats = {
        'total_bombas': scalar('SELECT COUNT(*) as n FROM bombas'),
        'total_perforaciones': scalar('SELECT COUNT(*) as n FROM perforaciones'),
        'montadas': scalar("SELECT COUNT(*) as n FROM asignaciones WHERE estado='Montado'"),
        'disponibles': scalar('''SELECT COUNT(*) as n FROM bombas WHERE id NOT IN
            (SELECT DISTINCT bomba_id FROM asignaciones WHERE estado='Montado')'''),
        'por_zona': many('''SELECT p.zona, COUNT(*) as n FROM asignaciones a
            JOIN perforaciones p ON a.perforacion_id=p.id
            WHERE a.estado='Montado' GROUP BY p.zona'''),
        'por_hp': many('''SELECT b.hp, COUNT(*) as n FROM asignaciones a
            JOIN bombas b ON a.bomba_id=b.id
            WHERE a.estado='Montado' AND b.hp IS NOT NULL GROUP BY b.hp ORDER BY b.hp'''),
        'por_marca': many('''SELECT marca, COUNT(*) as n FROM bombas WHERE marca IS NOT NULL
            GROUP BY marca ORDER BY n DESC'''),
        'modelos_top': many('''SELECT b.modelo, COUNT(*) as n FROM asignaciones a
            JOIN bombas b ON a.bomba_id=b.id
            WHERE a.estado='Montado' AND b.modelo IS NOT NULL
            GROUP BY b.modelo ORDER BY n DESC LIMIT 10'''),
        'en_reparacion': scalar("SELECT COUNT(*) as n FROM reparaciones WHERE estado NOT IN ('Entregada','Cancelada')"),
    }
    conn.close()
    return jsonify(stats)

# ── REPARACIONES ──
ESTADOS_REPARACION = [
    'Pendiente cotización',
    'En reparación',
    'Esperando SOLPED',
    'Esperando NP',
    'Esperando retiro',
    'Entregada',
    'Cancelada',
]

REP_FIELDS = [
    'fecha_envio','remito','proveedor','descripcion','servicio',
    'tag_actual','tag_reemplazado','numero_equipo','marca','modelo',
    'hp','kw','amperes','serie','centro','ceco','referencia',
    'presupuesto','fecha_cotizacion','costo_usd',
    'estado_autorizacion','fecha_autorizacion',
    'om','solped','fecha_solped','liberacion','fecha_liberacion',
    'estadio','gcp','nota_justificacion',
    'np','fecha_np_generacion','fecha_np_envio_prov',
    'estado_entrega','fecha_entrega','remito_entrega',
    'observaciones','responsable','estado','usuario_registro'
]
REP_DATE_FIELDS = {
    'fecha_envio','fecha_cotizacion','fecha_autorizacion','fecha_solped',
    'fecha_liberacion','fecha_np_generacion','fecha_np_envio_prov','fecha_entrega'
}

@app.route('/api/reparaciones', methods=['GET'])
@login_required
def get_reparaciones():
    conn = get_db()
    numero_equipo = request.args.get('numero_equipo', '').strip()
    estado        = request.args.get('estado', '').strip()
    proveedor     = request.args.get('proveedor', '').strip()
    activa        = request.args.get('activa', '').strip()

    query = 'SELECT * FROM reparaciones WHERE 1=1'
    params = []
    if numero_equipo:
        query += ' AND numero_equipo LIKE ?'
        params.append(f'%{numero_equipo}%')
    if estado:
        query += ' AND estado = ?'
        params.append(estado)
    if proveedor:
        query += ' AND proveedor LIKE ?'
        params.append(f'%{proveedor}%')
    if activa == '1':
        query += " AND estado NOT IN ('Entregada','Cancelada')"
    elif activa == '0':
        query += " AND estado IN ('Entregada','Cancelada')"
    query += ' ORDER BY fecha_envio DESC, id DESC'

    cur = conn.execute(query, params)
    rows = fetchall_dicts(cur)
    conn.close()
    return jsonify(rows)

@app.route('/api/reparaciones/<int:rid>', methods=['GET'])
@login_required
def get_reparacion(rid):
    conn = get_db()
    cur = conn.execute('SELECT * FROM reparaciones WHERE id = ?', (rid,))
    row = fetchone_dict(cur)
    conn.close()
    if not row:
        return jsonify({'error': 'No encontrado'}), 404
    return jsonify(row)

@app.route('/api/reparaciones', methods=['POST'])
@editor_required
def create_reparacion():
    data = request.get_json()
    sin_desmontaje = int(data.get('sin_desmontaje') or 0)
    forzar = bool(data.get('forzar'))  # True cuando el usuario confirmó la advertencia

    # Buscar bomba por numero_equipo para validar
    numero_equipo = norm_neq(data.get('numero_equipo') or '')
    conn = get_db()
    try:
        bomba_id = None
        if numero_equipo:
            cur_b = conn.execute(
                "SELECT id FROM bombas WHERE REPLACE(n_equipo,'.0','') = ?", (numero_equipo,)
            )
            b = fetchone_dict(cur_b)
            if b:
                bomba_id = b['id']

        if bomba_id:
            ok, mensaje, es_advertencia = _validar_reparacion(bomba_id, sin_desmontaje, conn)
            if not ok:
                if es_advertencia and forzar:
                    pass  # usuario confirmó, seguimos
                else:
                    return jsonify({
                        'error': mensaje,
                        'code': 'VALIDACION',
                        'advertencia': es_advertencia
                    }), 409

        fields = REP_FIELDS + ['sin_desmontaje', 'dias_limite_preventivo']
        vals = []
        for f in fields:
            v = data.get(f)
            if f in REP_DATE_FIELDS:
                v = norm_fecha(v)
            if f == 'usuario_registro' and not v:
                v = session.get('username', 'sistema')
            if f == 'sin_desmontaje':
                v = sin_desmontaje
            if f == 'dias_limite_preventivo':
                v = int(data.get('dias_limite_preventivo') or 90)
            vals.append(v)

        conn.execute(
            f'INSERT INTO reparaciones ({",".join(fields)}) VALUES ({",".join(["?"]*len(fields))})',
            vals
        )
        db_commit(conn)
        cur = conn.execute('SELECT * FROM reparaciones ORDER BY id DESC LIMIT 1')
        row = fetchone_dict(cur)
        return jsonify(row), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/reparaciones/<int:rid>', methods=['PUT'])
@editor_required
def update_reparacion(rid):
    data = request.get_json()
    fields = [f for f in REP_FIELDS if f != 'usuario_registro']
    vals = []
    for f in fields:
        v = data.get(f)
        if f in REP_DATE_FIELDS:
            v = norm_fecha(v)
        vals.append(v)
    sets = ', '.join([f'{f} = ?' for f in fields]) + ', updated_at = CURRENT_TIMESTAMP'
    vals.append(rid)
    conn = get_db()
    conn.execute(f'UPDATE reparaciones SET {sets} WHERE id = ?', vals)
    db_commit(conn)
    cur = conn.execute('SELECT * FROM reparaciones WHERE id = ?', (rid,))
    row = fetchone_dict(cur)
    conn.close()
    return jsonify(row)

@app.route('/api/reparaciones/<int:rid>', methods=['DELETE'])
@admin_required
def delete_reparacion(rid):
    conn = get_db()
    conn.execute('DELETE FROM reparaciones WHERE id = ?', (rid,))
    db_commit(conn)
    conn.close()
    return jsonify({'ok': True})

@app.route('/api/garantia/<n_equipo>', methods=['GET'])
@login_required
def check_garantia_endpoint(n_equipo):
    conn = get_db()
    rep = check_garantia(norm_neq(n_equipo), conn)
    conn.close()
    if rep:
        from datetime import date, timedelta
        fecha_ent = rep.get('fecha_entrega','')
        try:
            desde = date.fromisoformat(fecha_ent)
            hasta = desde + timedelta(days=183)
            dias_restantes = (hasta - date.today()).days
        except:
            hasta = None
            dias_restantes = None
        return jsonify({
            'en_garantia': True,
            'rep_id': rep['id'],
            'fecha_entrega': rep['fecha_entrega'],
            'hasta': hasta.isoformat() if hasta else None,
            'dias_restantes': dias_restantes,
            'proveedor': rep.get('proveedor'),
            'remito_entrega': rep.get('remito_entrega'),
            'descripcion': rep.get('descripcion'),
        })
    return jsonify({'en_garantia': False})

@app.route('/api/reparaciones/estados', methods=['GET'])
@login_required
def get_estados_reparacion():
    return jsonify(ESTADOS_REPARACION)

@app.route('/api/import/reparaciones', methods=['POST'])
@admin_required
def import_reparaciones():
    """Importa registros desde seed_reparaciones.json usando executemany (chunks de 10)."""
    import os as _os, urllib.request as _urllib
    records = None

    # 1) Intentar leer localmente
    seed_path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'seed_reparaciones.json')
    if _os.path.exists(seed_path):
        try:
            with open(seed_path, encoding='utf-8') as f:
                records = json.load(f)
        except Exception as e:
            return jsonify({'error': f'Error leyendo archivo local: {str(e)}'}), 500

    # 2) Fallback: leer desde GitHub raw
    if records is None:
        try:
            url = 'https://raw.githubusercontent.com/ElMoNo22/bombas-mgr/refs/heads/main/seed_reparaciones.json'
            with _urllib.urlopen(url, timeout=30) as resp:
                records = json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            return jsonify({'error': f'No se encontró el archivo: {str(e)}'}), 500

    conn = get_db()
    try:
        # Traer existentes en una sola query
        cur = conn.execute('SELECT remito, numero_equipo FROM reparaciones')
        existentes = set(
            (r['remito'], str(r['numero_equipo'] or '')) for r in fetchall_dicts(cur)
        )
    except Exception as e:
        conn.close()
        return jsonify({'error': f'Error leyendo tabla: {str(e)}'}), 500

    # Filtrar duplicados
    to_insert = []
    skipped = 0
    for r in records:
        key = (r.get('remito'), str(r.get('numero_equipo') or ''))
        if key in existentes:
            skipped += 1
        else:
            to_insert.append([r.get(f) for f in REP_FIELDS])

    # Insertar en batch con executemany (chunks de 10 internamente)
    insert_sql = f'INSERT INTO reparaciones ({",".join(REP_FIELDS)}) VALUES ({",".join(["?"]*len(REP_FIELDS))})'
    errors = 0
    err_list = []
    try:
        conn.executemany(insert_sql, to_insert)
        inserted = len(to_insert)
    except Exception as e:
        # Si falla el batch, intentar uno por uno para rescatar los que se pueda
        inserted = 0
        for vals in to_insert:
            try:
                conn.execute(insert_sql, vals)
                inserted += 1
            except Exception as e2:
                errors += 1
                if len(err_list) < 5:
                    err_list.append(str(e2))

    conn.close()
    return jsonify({'ok': True, 'inserted': inserted, 'skipped': skipped,
                    'errors': errors, 'error_list': err_list})


# ── TAGS HISTORIAL ──

@app.route('/api/bombas/<int:bid>/tags', methods=['GET'])
@login_required
def get_tags_historial(bid):
    conn = get_db()
    cur = conn.execute(
        'SELECT * FROM tags_historial WHERE bomba_id = ? ORDER BY fecha_desde DESC, id DESC',
        (bid,)
    )
    rows = fetchall_dicts(cur)
    conn.close()
    return jsonify(rows)

@app.route('/api/bombas/<int:bid>/tags', methods=['POST'])
@editor_required
def add_tag_historial(bid):
    """Registra un cambio de tag en una bomba.
    Cierra el tag anterior (si hay uno activo) y abre el nuevo.
    """
    data = request.get_json()
    tag_nuevo = (data.get('tag') or '').strip()
    motivo = (data.get('motivo') or '').strip()
    fecha_desde = norm_fecha(data.get('fecha_desde')) or __import__('datetime').date.today().isoformat()

    if not tag_nuevo:
        return jsonify({'error': 'tag requerido'}), 400

    conn = get_db()
    try:
        # Cerrar el tag activo anterior si existe
        cur = conn.execute(
            "SELECT id FROM tags_historial WHERE bomba_id = ? AND (fecha_hasta IS NULL OR fecha_hasta = '') ORDER BY id DESC LIMIT 1",
            (bid,)
        )
        activo = fetchone_dict(cur)
        if activo:
            conn.execute(
                "UPDATE tags_historial SET fecha_hasta = ? WHERE id = ?",
                (fecha_desde, activo['id'])
            )

        # Obtener n_equipo de la bomba
        cur_b = conn.execute('SELECT n_equipo FROM bombas WHERE id = ?', (bid,))
        bomba = fetchone_dict(cur_b)
        n_equipo = bomba['n_equipo'] if bomba else ''

        # Insertar nuevo tag
        conn.execute(
            '''INSERT INTO tags_historial (bomba_id, n_equipo, tag, fecha_desde, motivo, usuario)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (bid, n_equipo, tag_nuevo, fecha_desde, motivo, session.get('username', 'sistema'))
        )

        # Actualizar tag actual en bombas
        conn.execute(
            'UPDATE bombas SET tag = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (tag_nuevo, bid)
        )
        db_commit(conn)

        cur2 = conn.execute(
            'SELECT * FROM tags_historial WHERE bomba_id = ? ORDER BY id DESC LIMIT 1', (bid,)
        )
        row = fetchone_dict(cur2)
        return jsonify(row), 201
    finally:
        conn.close()


# ── ANALÍTICA — ERRORES DE INTEGRIDAD ──

@app.route('/api/analitica/errores', methods=['GET'])
@login_required
def get_errores_integridad():
    """
    Detecta inconsistencias en la base de datos y las devuelve categorizadas.
    Usado por el panel de Analítica para mostrar errores corregibles.
    """
    from datetime import date, timedelta
    conn = get_db()
    errores = []

    try:
        # ── 1. Bombas montadas en más de un lugar al mismo tiempo ──
        cur = conn.execute('''
            SELECT b.id as bomba_id, b.n_equipo, b.tag, b.marca, b.modelo,
                   COUNT(*) as cant_montajes
            FROM asignaciones a JOIN bombas b ON a.bomba_id = b.id
            WHERE a.estado = 'Montado'
            GROUP BY a.bomba_id
            HAVING COUNT(*) > 1
        ''')
        for r in fetchall_dicts(cur):
            cur2 = conn.execute('''
                SELECT a.id as asig_id, a.fecha_montaje, p.calle, p.y_col, p.zona
                FROM asignaciones a JOIN perforaciones p ON a.perforacion_id = p.id
                WHERE a.bomba_id = ? AND a.estado = 'Montado'
                ORDER BY a.fecha_montaje DESC
            ''', (r['bomba_id'],))
            montajes = fetchall_dicts(cur2)
            errores.append({
                'tipo': 'doble_montado',
                'severidad': 'error',
                'titulo': f"Bomba montada en {r['cant_montajes']} lugares al mismo tiempo",
                'descripcion': f"Equipo {r['n_equipo']} ({r['marca']} {r['modelo']}) figura como Montado en {r['cant_montajes']} perforaciones.",
                'bomba_id': r['bomba_id'],
                'n_equipo': r['n_equipo'],
                'tag': r['tag'],
                'detalle': montajes,
                'accion': 'Corregir manualmente desde el perfil de la bomba'
            })

        # ── 2. Bombas Montadas con reparación activa (sin flag preventivo) ──
        cur = conn.execute('''
            SELECT DISTINCT b.id as bomba_id, b.n_equipo, b.tag, b.marca, b.modelo,
                   p.calle, p.y_col, p.zona, a.fecha_montaje,
                   r.id as rep_id, r.proveedor, r.estado as rep_estado,
                   r.fecha_envio, r.sin_desmontaje
            FROM bombas b
            JOIN asignaciones a ON a.bomba_id = b.id AND a.estado = 'Montado'
            JOIN perforaciones p ON a.perforacion_id = p.id
            JOIN reparaciones r ON REPLACE(r.numero_equipo,'.0','') = b.n_equipo
                AND r.estado NOT IN ('Entregada','Cancelada')
                AND (r.sin_desmontaje IS NULL OR r.sin_desmontaje = 0)
        ''')
        for r in fetchall_dicts(cur):
            errores.append({
                'tipo': 'montada_en_reparacion',
                'severidad': 'error',
                'titulo': 'Bomba Montada con reparación activa',
                'descripcion': f"Equipo {r['n_equipo']} ({r['marca']} {r['modelo']}) está Montado en {r['calle']} y {r['y_col']} pero también tiene una reparación activa con {r['proveedor']} (estado: {r['rep_estado']}).",
                'bomba_id': r['bomba_id'],
                'n_equipo': r['n_equipo'],
                'rep_id': r['rep_id'],
                'detalle': r,
                'accion': 'Verificar: ¿se desmontó y no se registró? Corregir estado.'
            })

        # ── 3. Bombas con preventivo vencido ──
        hoy = date.today().isoformat()
        cur = conn.execute('''
            SELECT b.id as bomba_id, b.n_equipo, b.tag, b.marca, b.modelo,
                   r.id as rep_id, r.proveedor, r.estado as rep_estado,
                   r.fecha_envio, r.dias_limite_preventivo
            FROM bombas b
            JOIN reparaciones r ON REPLACE(r.numero_equipo,'.0','') = b.n_equipo
            WHERE r.estado NOT IN ('Entregada','Cancelada')
              AND r.sin_desmontaje = 1
              AND r.fecha_envio IS NOT NULL
        ''')
        for r in fetchall_dicts(cur):
            try:
                dias = int(r.get('dias_limite_preventivo') or 90)
                desde = date.fromisoformat(str(r['fecha_envio']))
                vence = desde + timedelta(days=dias)
                dias_rest = (vence - date.today()).days
                if dias_rest < 0:
                    errores.append({
                        'tipo': 'preventivo_vencido',
                        'severidad': 'advertencia',
                        'titulo': 'Mantenimiento preventivo vencido',
                        'descripcion': f"Equipo {r['n_equipo']} ({r['marca']} {r['modelo']}) tiene un mantenimiento preventivo con {r['proveedor']} abierto hace {abs(dias_rest)} días (venció el {vence.isoformat()}).",
                        'bomba_id': r['bomba_id'],
                        'n_equipo': r['n_equipo'],
                        'rep_id': r['rep_id'],
                        'dias_vencido': abs(dias_rest),
                        'accion': 'Cerrar el mantenimiento o extender el plazo'
                    })
            except Exception:
                pass

        # ── 4. Reparaciones activas cuyo n_equipo no existe en bombas ──
        cur = conn.execute('''
            SELECT r.id, r.numero_equipo, r.marca, r.modelo, r.tag_actual,
                   r.proveedor, r.estado, r.fecha_envio, r.hp
            FROM reparaciones r
            WHERE r.estado NOT IN ('Entregada','Cancelada')
              AND NOT EXISTS (
                SELECT 1 FROM bombas b
                WHERE REPLACE(b.n_equipo,'.0','') = REPLACE(r.numero_equipo,'.0','')
              )
            ORDER BY r.fecha_envio DESC
        ''')
        for r in fetchall_dicts(cur):
            errores.append({
                'tipo': 'rep_sin_bomba',
                'severidad': 'advertencia',
                'titulo': 'Reparación activa sin bomba en inventario',
                'descripcion': f"Reparación #{r['id']} del equipo {r['numero_equipo']} ({r['marca']} {r['modelo']}) no tiene bomba correspondiente en el inventario.",
                'rep_id': r['id'],
                'n_equipo': r['numero_equipo'],
                'detalle': r,
                'accion': 'Agregar la bomba al inventario con ese N° de equipo'
            })

        # ── 5. Marcas con nombres duplicados/similares ──
        cur = conn.execute('SELECT DISTINCT marca FROM bombas WHERE marca IS NOT NULL')
        marcas = [r['marca'].strip() for r in fetchall_dicts(cur) if r.get('marca')]
        cur2 = conn.execute('SELECT DISTINCT proveedor FROM reparaciones WHERE proveedor IS NOT NULL')
        proveedores = [r['proveedor'].strip() for r in fetchall_dicts(cur2) if r.get('proveedor')]

        def _similares(lista):
            grupos = []
            vistos = set()
            for i, a in enumerate(lista):
                if a in vistos:
                    continue
                grupo = [a]
                a_norm = a.upper().replace(' ', '').replace('-', '').replace('.', '')
                for b in lista[i+1:]:
                    b_norm = b.upper().replace(' ', '').replace('-', '').replace('.', '')
                    if a_norm == b_norm or (len(a_norm) > 4 and (a_norm in b_norm or b_norm in a_norm)):
                        grupo.append(b)
                        vistos.add(b)
                if len(grupo) > 1:
                    grupos.append(grupo)
                    vistos.add(a)
            return grupos

        for grupo in _similares(marcas):
            errores.append({
                'tipo': 'marca_duplicada',
                'severidad': 'advertencia',
                'titulo': 'Marca con nombres inconsistentes',
                'descripcion': f"Posibles duplicados de marca: {' | '.join(grupo)}",
                'valores': grupo,
                'accion': 'Unificar el nombre de la marca en todas las bombas afectadas'
            })

        for grupo in _similares(proveedores):
            errores.append({
                'tipo': 'proveedor_duplicado',
                'severidad': 'advertencia',
                'titulo': 'Proveedor con nombres inconsistentes',
                'descripcion': f"Posibles duplicados de proveedor: {' | '.join(grupo)}",
                'valores': grupo,
                'accion': 'Unificar el nombre del proveedor en todas las reparaciones afectadas'
            })

    finally:
        conn.close()

    resumen = {
        'total': len(errores),
        'errores': len([e for e in errores if e['severidad'] == 'error']),
        'advertencias': len([e for e in errores if e['severidad'] == 'advertencia']),
    }
    return jsonify({'resumen': resumen, 'items': errores})


@app.route('/api/analitica/unificar-marca', methods=['POST'])
@admin_required
def unificar_marca():
    """Reemplaza todas las variantes de una marca por el nombre canónico."""
    data = request.get_json()
    variantes = data.get('variantes', [])
    canonical = (data.get('canonical') or '').strip()
    if not canonical or not variantes:
        return jsonify({'error': 'canonical y variantes requeridos'}), 400
    conn = get_db()
    try:
        updated = 0
        for v in variantes:
            if v == canonical:
                continue
            conn.execute('UPDATE bombas SET marca = ? WHERE marca = ?', (canonical, v))
            updated += 1
        db_commit(conn)
        return jsonify({'ok': True, 'updated_variantes': updated})
    finally:
        conn.close()


@app.route('/api/analitica/unificar-proveedor', methods=['POST'])
@admin_required
def unificar_proveedor():
    """Reemplaza todas las variantes de un proveedor por el nombre canónico."""
    data = request.get_json()
    variantes = data.get('variantes', [])
    canonical = (data.get('canonical') or '').strip()
    if not canonical or not variantes:
        return jsonify({'error': 'canonical y variantes requeridos'}), 400
    conn = get_db()
    try:
        updated = 0
        for v in variantes:
            if v == canonical:
                continue
            conn.execute('UPDATE reparaciones SET proveedor = ? WHERE proveedor = ?', (canonical, v))
            updated += 1
        db_commit(conn)
        return jsonify({'ok': True, 'updated_variantes': updated})
    finally:
        conn.close()


# ── USERS ──
@app.route('/api/users', methods=['GET'])
@admin_required
def get_users():
    conn = get_db()
    cur = conn.execute('SELECT id,username,role FROM users')
    rows = fetchall_dicts(cur)
    conn.close()
    return jsonify(rows)

@app.route('/api/users', methods=['POST'])
@admin_required
def create_user():
    data = request.get_json()
    username = data.get('username','').strip()
    password = data.get('password','')
    role = data.get('role','viewer')
    if not username or not password:
        return jsonify({'error': 'Usuario y contraseña requeridos'}), 400
    conn = get_db()
    try:
        conn.execute('INSERT INTO users (username,password_hash,role) VALUES (?,?,?)',
                   (username, generate_password_hash(password), role))
        db_commit(conn)
    except Exception:
        conn.close()
        return jsonify({'error': 'Usuario ya existe'}), 409
    conn.close()
    return jsonify({'ok': True}), 201

@app.route('/api/users/<int:uid>', methods=['DELETE'])
@admin_required
def delete_user(uid):
    if uid == session.get('user_id'):
        return jsonify({'error': 'No podés eliminarte a vos mismo'}), 400
    conn = get_db()
    conn.execute('DELETE FROM users WHERE id = ?', (uid,))
    db_commit(conn)
    conn.close()
    return jsonify({'ok': True})

@app.route('/api/users/<int:uid>/role', methods=['PATCH'])
@admin_required
def change_role(uid):
    data = request.get_json()
    new_role = data.get('role','').strip()
    if new_role not in ('viewer','editor','admin'):
        return jsonify({'error': 'Rol inválido'}), 400
    if uid == session.get('user_id'):
        return jsonify({'error': 'No podés cambiar tu propio rol'}), 400
    conn = get_db()
    conn.execute('UPDATE users SET role=? WHERE id=?', (new_role, uid))
    db_commit(conn)
    conn.close()
    return jsonify({'ok': True})

@app.route('/api/me/password', methods=['PUT'])
@login_required
def change_password():
    data = request.get_json()
    current = data.get('current','')
    new_pw = data.get('new','')
    if not new_pw or len(new_pw) < 6:
        return jsonify({'error': 'Mínimo 6 caracteres'}), 400
    conn = get_db()
    cur = conn.execute('SELECT * FROM users WHERE id=?', (session['user_id'],))
    user = fetchone_dict(cur)
    if not user or not check_password_hash(user['password_hash'], current):
        conn.close()
        return jsonify({'error': 'Contraseña actual incorrecta'}), 401
    conn.execute('UPDATE users SET password_hash=? WHERE id=?',
               (generate_password_hash(new_pw), session['user_id']))
    db_commit(conn)
    conn.close()
    return jsonify({'ok': True})

# ── ADMIN UTILS ──
@app.route('/api/admin/reseed-asignaciones', methods=['POST'])
@admin_required
def reseed_asignaciones():
    conn = get_db()
    cur = conn.execute('SELECT COUNT(*) as n FROM asignaciones')
    count = fetchone_dict(cur)['n']
    if count > 0:
        conn.close()
        return jsonify({'ok': True, 'msg': f'Ya existen {count} asignaciones'})
    seed_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'seed_asignaciones.json')
    if not os.path.exists(seed_path):
        conn.close()
        return jsonify({'error': f'Archivo no encontrado: {seed_path}'}), 404
    try:
        with open(seed_path, encoding='utf-8') as f:
            asigs = json.load(f)
    except Exception as e:
        conn.close()
        return jsonify({'error': f'Error leyendo archivo: {str(e)}'}), 500
    cur_b = conn.execute('SELECT id, n_equipo FROM bombas')
    bombas_map = {str(r['n_equipo']): r['id'] for r in fetchall_dicts(cur_b)}
    cur_p = conn.execute('SELECT id, calle, entre, y_col FROM perforaciones')
    perfs_map = {}
    for p in fetchall_dicts(cur_p):
        key = f"{p['calle']}|{p['entre'] or '0'}|{p['y_col'] or '0'}"
        perfs_map[key] = p['id']
    inserted = skipped = failed = 0
    errors = []
    for a in asigs:
        bid = bombas_map.get(str(a.get('n_equipo','')))
        pid = perfs_map.get(a.get('perf_key',''))
        if not bid or not pid:
            skipped += 1
            continue
        try:
            conn.execute('''INSERT INTO asignaciones
                (bomba_id,perforacion_id,estado,fecha_montaje,fecha_desmontaje,notificada_por,notas)
                VALUES (?,?,?,?,?,?,?)''',
                (bid, pid, a.get('estado','Desmontado'),
                 a.get('fecha_montaje'), a.get('fecha_desmontaje'),
                 a.get('notificada_por'), a.get('notas')))
            db_commit(conn)
            inserted += 1
        except Exception as e:
            failed += 1
            if len(errors) < 5:
                errors.append(str(e))
    conn.close()
    return jsonify({'ok': True, 'inserted': inserted, 'skipped': skipped,
                   'failed': failed, 'errors': errors})

@app.route('/api/admin/fix-fechas', methods=['POST'])
@admin_required
def fix_fechas():
    conn = get_db()
    cur = conn.execute('SELECT id, fecha_montaje, fecha_desmontaje FROM asignaciones')
    rows = fetchall_dicts(cur)
    fixed = 0
    for r in rows:
        fm = norm_fecha(r.get('fecha_montaje'))
        fd = norm_fecha(r.get('fecha_desmontaje'))
        if fm != r.get('fecha_montaje') or fd != r.get('fecha_desmontaje'):
            conn.execute('UPDATE asignaciones SET fecha_montaje=?, fecha_desmontaje=? WHERE id=?',
                        (fm, fd, r['id']))
            fixed += 1
    db_commit(conn)
    conn.close()
    return jsonify({'ok': True, 'fixed': fixed})

# ── CHAT con Gemini ──

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

def build_context(conn):
    """Arma un resumen de la base de datos para pasarle como contexto a Gemini."""
    def scalar(sql, params=()):
        cur = conn.execute(sql, params)
        row = fetchone_dict(cur)
        return list(row.values())[0] if row else 0

    def many(sql, params=()):
        cur = conn.execute(sql, params)
        return fetchall_dicts(cur)

    ctx = {}

    # Stats generales
    ctx['total_bombas'] = scalar('SELECT COUNT(*) as n FROM bombas')
    ctx['total_perforaciones'] = scalar('SELECT COUNT(*) as n FROM perforaciones')
    ctx['montadas'] = scalar("SELECT COUNT(*) as n FROM asignaciones WHERE estado='Montado'")
    ctx['disponibles'] = scalar('''SELECT COUNT(*) as n FROM bombas WHERE id NOT IN
        (SELECT DISTINCT bomba_id FROM asignaciones WHERE estado='Montado')''')
    ctx['en_reparacion'] = scalar("SELECT COUNT(*) as n FROM reparaciones WHERE estado NOT IN ('Entregada','Cancelada')")

    # Bombas en reparación
    ctx['reparaciones_activas'] = many('''
        SELECT numero_equipo, marca, modelo, proveedor, estado, fecha_envio, costo_usd
        FROM reparaciones
        WHERE estado NOT IN ('Entregada','Cancelada')
        ORDER BY fecha_envio DESC
    ''')

    # Bombas montadas por zona
    ctx['por_zona'] = many('''
        SELECT p.zona, COUNT(*) as n
        FROM asignaciones a JOIN perforaciones p ON a.perforacion_id=p.id
        WHERE a.estado='Montado' GROUP BY p.zona ORDER BY n DESC
    ''')

    # Bombas disponibles (no montadas)
    ctx['bombas_disponibles'] = many('''
        SELECT n_equipo, marca, modelo, hp, ubicacion_fisica
        FROM bombas WHERE id NOT IN
        (SELECT DISTINCT bomba_id FROM asignaciones WHERE estado='Montado')
        ORDER BY marca, modelo
        LIMIT 50
    ''')

    # Reparaciones recientes entregadas
    ctx['reparaciones_recientes'] = many('''
        SELECT numero_equipo, marca, modelo, proveedor, estado,
               fecha_envio, fecha_entrega, costo_usd, descripcion
        FROM reparaciones
        ORDER BY id DESC LIMIT 20
    ''')

    # Perforaciones sin bomba
    ctx['perforaciones_sin_bomba'] = scalar('''
        SELECT COUNT(*) as n FROM perforaciones WHERE id NOT IN
        (SELECT DISTINCT perforacion_id FROM asignaciones WHERE estado='Montado')
    ''')

    # Costo total reparaciones activas
    ctx['costo_total_reparaciones_activas'] = scalar('''
        SELECT COALESCE(SUM(costo_usd), 0) as n FROM reparaciones
        WHERE estado NOT IN ('Entregada','Cancelada') AND costo_usd IS NOT NULL
    ''')

    # Por marca
    ctx['por_marca'] = many('''
        SELECT marca, COUNT(*) as n FROM bombas
        WHERE marca IS NOT NULL GROUP BY marca ORDER BY n DESC
    ''')

    return ctx


@app.route('/api/chat', methods=['POST'])
@login_required
def chat_gemini():
    if not GEMINI_API_KEY:
        return jsonify({'error': 'GEMINI_API_KEY no configurada en el servidor'}), 500

    data = request.get_json()
    pregunta = (data.get('message') or '').strip()
    if not pregunta:
        return jsonify({'error': 'Mensaje vacío'}), 400

    conn = get_db()
    try:
        ctx = build_context(conn)
    finally:
        conn.close()

    system_prompt = f"""Sos un asistente experto del sistema de gestión de bombas de pozo profundo "POZO/MGR".
Respondé siempre en español, de forma clara y concisa.
Cuando hagas reportes o listas, usá formato legible (con saltos de línea, bullets, etc).
No inventes datos — solo usá la información del contexto provisto.

=== DATOS ACTUALES DEL SISTEMA ===
{json.dumps(ctx, ensure_ascii=False, indent=2)}
===================================

El usuario puede preguntarte sobre:
- Estado general del sistema (cuántas bombas hay, cuántas montadas, disponibles, etc.)
- Reparaciones activas o historial de reparaciones
- Bombas por zona, marca, modelo, HP
- Perforaciones sin bomba asignada
- Costos de reparaciones
- Cualquier análisis o reporte sobre los datos anteriores

Si la pregunta está fuera del alcance de los datos disponibles, indicalo amablemente.
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": system_prompt},
                    {"text": f"Pregunta del usuario: {pregunta}"}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 1024
        }
    }

    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent?key={GEMINI_API_KEY}"
    try:
        req = urllib.request.Request(
            gemini_url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode('utf-8'))
        
        respuesta = result['candidates'][0]['content']['parts'][0]['text']
        return jsonify({'reply': respuesta})

    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        return jsonify({'error': f'Error Gemini: {error_body}'}), 502
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
