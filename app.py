import os, json, re
import turso as db_driver
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'bombas-mgr-secret-2024')

# ── DB CONNECTION ──
def get_db():
    return db_driver.connect()

def db_commit(conn):
    conn.commit()

def row_to_dict(row):
    if row is None: return None
    return dict(row)

def fetchall_dicts(cursor):
    rows = cursor.fetchall()
    result = []
    for r in rows:
        try:
            result.append(dict(r))
        except Exception:
            # sqlite3.Row needs keys()
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
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'viewer'
        );
        CREATE TABLE IF NOT EXISTS bombas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            n_equipo TEXT UNIQUE,
            tag TEXT,
            tag_extraviado TEXT,
            marca TEXT,
            modelo TEXT,
            hp REAL,
            kw REAL,
            amperes TEXT,
            serie TEXT,
            peso_kg REAL,
            largo_mm REAL,
            salida TEXT,
            tazones TEXT,
            sap_id TEXT,
            id_estadio TEXT,
            observaciones TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS perforaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            calle TEXT,
            entre TEXT,
            y_col TEXT,
            zona TEXT,
            bombeo TEXT,
            denominacion TEXT,
            prof_trabajo_mts REAL,
            tipo_cañeria TEXT,
            mts_cañeria TEXT,
            nivel_estatico REAL,
            nivel_dinamico REAL,
            Q_m3h REAL,
            H_mca REAL,
            candado TEXT,
            observaciones TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS asignaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bomba_id INTEGER,
            perforacion_id INTEGER,
            estado TEXT DEFAULT 'Desmontado',
            fecha_montaje TEXT,
            fecha_desmontaje TEXT,
            notificada_por TEXT,
            relevado_el TEXT,
            notas TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS catalogo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca TEXT,
            modelo TEXT,
            para TEXT,
            hp REAL,
            etapas TEXT,
            descarga TEXT,
            largo_mm TEXT,
            curva_json TEXT
        );
    ''')
    db_commit(conn)
    cur = conn.execute('SELECT id FROM users WHERE username = ?', ('admin',))
    existing = fetchone_dict(cur)
    if not existing:
        conn.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                   ('admin', generate_password_hash('bombas2024'), 'admin'))
        db_commit(conn)
    conn.close()

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
               a.id as asignacion_id, p.calle, p.entre, p.y_col, p.zona, p.id as perforacion_id
        FROM bombas b
        LEFT JOIN asignaciones a ON a.bomba_id = b.id
            AND a.id = (
                SELECT id FROM asignaciones WHERE bomba_id = b.id
                ORDER BY CASE WHEN estado = 'Montado' THEN 0 ELSE 1 END,
                CASE WHEN COALESCE(fecha_desmontaje,fecha_montaje) IS NULL THEN 1 ELSE 0 END,
                COALESCE(fecha_desmontaje,fecha_montaje) DESC, id DESC LIMIT 1
            )
        LEFT JOIN perforaciones p ON a.perforacion_id = p.id
        ORDER BY b.marca, b.modelo
    ''')
    rows = fetchall_dicts(cur)
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
        CASE WHEN COALESCE(a.fecha_desmontaje,a.fecha_montaje) IS NULL THEN 1 ELSE 0 END,
        COALESCE(a.fecha_desmontaje,a.fecha_montaje) DESC, a.id DESC
    ''', (bid,))
    bomba['historial'] = fetchall_dicts(cur2)
    conn.close()
    return jsonify(bomba)

@app.route('/api/bombas', methods=['POST'])
@editor_required
def create_bomba():
    data = request.get_json()
    fields = ['n_equipo','tag','tag_extraviado','marca','modelo','hp','kw','amperes',
              'serie','peso_kg','largo_mm','salida','tazones','sap_id','id_estadio','observaciones']
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
              'serie','peso_kg','largo_mm','salida','tazones','sap_id','id_estadio','observaciones']
    sets = ', '.join([f'{f} = ?' for f in fields]) + ', updated_at = CURRENT_TIMESTAMP'
    vals = [data.get(f) for f in fields] + [bid]
    conn = get_db()
    conn.execute(f'UPDATE bombas SET {sets} WHERE id = ?', vals)
    db_commit(conn)
    cur = conn.execute('SELECT * FROM bombas WHERE id = ?', (bid,))
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
        CASE WHEN COALESCE(a.fecha_desmontaje,a.fecha_montaje) IS NULL THEN 1 ELSE 0 END,
        COALESCE(a.fecha_desmontaje,a.fecha_montaje) DESC, a.id DESC
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
    cur = conn.execute('''
        SELECT a.id, p.calle, p.y_col FROM asignaciones a
        JOIN perforaciones p ON a.perforacion_id = p.id
        WHERE a.bomba_id = ? AND a.estado = 'Montado'
    ''', (bomba_id,))
    active = fetchone_dict(cur)
    if active:
        conn.close()
        return jsonify({'error': f'La bomba ya está montada en {active["calle"]} y {active["y_col"]}'}), 409
    conn.execute('''
        INSERT INTO asignaciones (bomba_id, perforacion_id, estado, fecha_montaje, fecha_desmontaje, notificada_por, notas)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (bomba_id, perforacion_id, data.get('estado','Montado'),
          data.get('fecha_montaje'), data.get('fecha_desmontaje'),
          data.get('notificada_por'), data.get('notas')))
    db_commit(conn)
    cur2 = conn.execute('''
        SELECT a.*, b.n_equipo, b.tag, b.marca, b.modelo, b.hp, p.calle, p.y_col, p.zona
        FROM asignaciones a JOIN bombas b ON a.bomba_id=b.id JOIN perforaciones p ON a.perforacion_id=p.id
        ORDER BY a.id DESC LIMIT 1
    ''')
    row = fetchone_dict(cur2)
    conn.close()
    return jsonify(row), 201

@app.route('/api/asignaciones/<int:aid>', methods=['PUT'])
@editor_required
def update_asignacion(aid):
    data = request.get_json()
    fields = ['estado','fecha_montaje','fecha_desmontaje','notificada_por','relevado_el','notas']
    sets = ', '.join([f'{f} = ?' for f in fields]) + ', updated_at = CURRENT_TIMESTAMP'
    vals = [data.get(f) for f in fields] + [aid]
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
        (data.get('fecha_desmontaje'), data.get('notas'), aid))
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

# ── CATALOGO ──
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
    }
    conn.close()
    return jsonify(stats)

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
    except Exception as e:
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

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
