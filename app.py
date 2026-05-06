import os, json, sqlite3, re
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'bombas-mgr-secret-2024')
DB_PATH = os.environ.get('DB_PATH', 'bombas.db')

def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db

def row_to_dict(row):
    return dict(row) if row else None

def init_db():
    db = get_db()
    db.executescript('''
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
            bomba_id INTEGER REFERENCES bombas(id),
            perforacion_id INTEGER REFERENCES perforaciones(id),
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
    existing = db.execute('SELECT id FROM users WHERE username = ?', ('admin',)).fetchone()
    if not existing:
        db.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                   ('admin', generate_password_hash('bombas2024'), 'admin'))
    db.commit()
    db.close()

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
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    db.close()
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
    db = get_db()
    rows = db.execute('''
        SELECT b.*, a.estado as estado_actual, a.fecha_montaje, a.fecha_desmontaje,
               a.id as asignacion_id, p.calle, p.entre, p.y_col, p.zona, p.id as perforacion_id
        FROM bombas b
        LEFT JOIN asignaciones a ON a.bomba_id = b.id
            AND a.id = (SELECT id FROM asignaciones WHERE bomba_id = b.id ORDER BY id DESC LIMIT 1)
        LEFT JOIN perforaciones p ON a.perforacion_id = p.id
        ORDER BY b.marca, b.modelo
    ''').fetchall()
    db.close()
    return jsonify([row_to_dict(r) for r in rows])

@app.route('/api/bombas/<int:bid>', methods=['GET'])
@login_required
def get_bomba(bid):
    db = get_db()
    row = db.execute('SELECT * FROM bombas WHERE id = ?', (bid,)).fetchone()
    if not row:
        db.close()
        return jsonify({'error': 'No encontrado'}), 404
    bomba = row_to_dict(row)
    hist = db.execute('''
        SELECT a.*, p.calle, p.entre, p.y_col, p.zona, p.id as perforacion_id
        FROM asignaciones a
        LEFT JOIN perforaciones p ON a.perforacion_id = p.id
        WHERE a.bomba_id = ? ORDER BY a.id DESC
    ''', (bid,)).fetchall()
    bomba['historial'] = [row_to_dict(h) for h in hist]
    db.close()
    return jsonify(bomba)

@app.route('/api/bombas', methods=['POST'])
@editor_required
def create_bomba():
    data = request.get_json()
    fields = ['n_equipo','tag','tag_extraviado','marca','modelo','hp','kw','amperes',
              'serie','peso_kg','largo_mm','salida','tazones','sap_id','id_estadio','observaciones']
    vals = [data.get(f) for f in fields]
    db = get_db()
    try:
        cur = db.execute(f'INSERT INTO bombas ({",".join(fields)}) VALUES ({",".join(["?"]*len(fields))})', vals)
        db.commit()
        row = db.execute('SELECT * FROM bombas WHERE id = ?', (cur.lastrowid,)).fetchone()
        db.close()
        return jsonify(row_to_dict(row)), 201
    except sqlite3.IntegrityError:
        db.close()
        return jsonify({'error': 'N° de equipo ya existe'}), 409

@app.route('/api/bombas/<int:bid>', methods=['PUT'])
@editor_required
def update_bomba(bid):
    data = request.get_json()
    fields = ['n_equipo','tag','tag_extraviado','marca','modelo','hp','kw','amperes',
              'serie','peso_kg','largo_mm','salida','tazones','sap_id','id_estadio','observaciones']
    sets = ', '.join([f'{f} = ?' for f in fields]) + ', updated_at = CURRENT_TIMESTAMP'
    vals = [data.get(f) for f in fields] + [bid]
    db = get_db()
    db.execute(f'UPDATE bombas SET {sets} WHERE id = ?', vals)
    db.commit()
    row = db.execute('SELECT * FROM bombas WHERE id = ?', (bid,)).fetchone()
    db.close()
    return jsonify(row_to_dict(row))

@app.route('/api/bombas/<int:bid>', methods=['DELETE'])
@admin_required
def delete_bomba(bid):
    db = get_db()
    db.execute('DELETE FROM asignaciones WHERE bomba_id = ?', (bid,))
    db.execute('DELETE FROM bombas WHERE id = ?', (bid,))
    db.commit()
    db.close()
    return jsonify({'ok': True})

@app.route('/api/bombas/disponibles', methods=['GET'])
@login_required
def get_bombas_disponibles():
    db = get_db()
    rows = db.execute('''
        SELECT * FROM bombas WHERE id NOT IN
        (SELECT DISTINCT bomba_id FROM asignaciones WHERE estado = 'Montado')
        ORDER BY marca, modelo, hp
    ''').fetchall()
    db.close()
    return jsonify([row_to_dict(r) for r in rows])

# ── PERFORACIONES ──
@app.route('/api/perforaciones', methods=['GET'])
@login_required
def get_perforaciones():
    db = get_db()
    rows = db.execute('''
        SELECT p.*, b.n_equipo, b.tag, b.marca, b.modelo, b.hp, b.serie, b.amperes,
               a.estado as estado_actual, a.fecha_montaje, a.fecha_desmontaje,
               a.id as asignacion_id, b.id as bomba_id
        FROM perforaciones p
        LEFT JOIN asignaciones a ON a.perforacion_id = p.id
            AND a.id = (SELECT id FROM asignaciones WHERE perforacion_id = p.id ORDER BY id DESC LIMIT 1)
        LEFT JOIN bombas b ON a.bomba_id = b.id
        ORDER BY p.zona, p.calle, p.y_col
    ''').fetchall()
    db.close()
    return jsonify([row_to_dict(r) for r in rows])

@app.route('/api/perforaciones/<int:pid>', methods=['GET'])
@login_required
def get_perforacion(pid):
    db = get_db()
    row = db.execute('SELECT * FROM perforaciones WHERE id = ?', (pid,)).fetchone()
    if not row:
        db.close()
        return jsonify({'error': 'No encontrado'}), 404
    perf = row_to_dict(row)
    hist = db.execute('''
        SELECT a.*, b.n_equipo, b.tag, b.marca, b.modelo, b.hp, b.serie, b.id as bomba_id
        FROM asignaciones a
        LEFT JOIN bombas b ON a.bomba_id = b.id
        WHERE a.perforacion_id = ? ORDER BY a.id DESC
    ''', (pid,)).fetchall()
    perf['historial'] = [row_to_dict(h) for h in hist]
    db.close()
    return jsonify(perf)

@app.route('/api/perforaciones', methods=['POST'])
@editor_required
def create_perforacion():
    data = request.get_json()
    fields = ['calle','entre','y_col','zona','bombeo','denominacion','prof_trabajo_mts',
              'tipo_cañeria','mts_cañeria','nivel_estatico','nivel_dinamico','Q_m3h','H_mca','candado','observaciones']
    vals = [data.get(f) for f in fields]
    db = get_db()
    cur = db.execute(f'INSERT INTO perforaciones ({",".join(fields)}) VALUES ({",".join(["?"]*len(fields))})', vals)
    db.commit()
    row = db.execute('SELECT * FROM perforaciones WHERE id = ?', (cur.lastrowid,)).fetchone()
    db.close()
    return jsonify(row_to_dict(row)), 201

@app.route('/api/perforaciones/<int:pid>', methods=['PUT'])
@editor_required
def update_perforacion(pid):
    data = request.get_json()
    fields = ['calle','entre','y_col','zona','bombeo','denominacion','prof_trabajo_mts',
              'tipo_cañeria','mts_cañeria','nivel_estatico','nivel_dinamico','Q_m3h','H_mca','candado','observaciones']
    sets = ', '.join([f'{f} = ?' for f in fields]) + ', updated_at = CURRENT_TIMESTAMP'
    vals = [data.get(f) for f in fields] + [pid]
    db = get_db()
    db.execute(f'UPDATE perforaciones SET {sets} WHERE id = ?', vals)
    db.commit()
    row = db.execute('SELECT * FROM perforaciones WHERE id = ?', (pid,)).fetchone()
    db.close()
    return jsonify(row_to_dict(row))

@app.route('/api/perforaciones/<int:pid>', methods=['DELETE'])
@admin_required
def delete_perforacion(pid):
    db = get_db()
    db.execute('DELETE FROM asignaciones WHERE perforacion_id = ?', (pid,))
    db.execute('DELETE FROM perforaciones WHERE id = ?', (pid,))
    db.commit()
    db.close()
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
    db = get_db()
    active = db.execute('''
        SELECT a.id, p.calle, p.y_col FROM asignaciones a
        JOIN perforaciones p ON a.perforacion_id = p.id
        WHERE a.bomba_id = ? AND a.estado = 'Montado'
    ''', (bomba_id,)).fetchone()
    if active:
        db.close()
        return jsonify({'error': f'La bomba ya está montada en {active["calle"]} y {active["y_col"]}'}), 409
    cur = db.execute('''
        INSERT INTO asignaciones (bomba_id, perforacion_id, estado, fecha_montaje, fecha_desmontaje, notificada_por, notas)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (bomba_id, perforacion_id, data.get('estado','Montado'),
          data.get('fecha_montaje'), data.get('fecha_desmontaje'),
          data.get('notificada_por'), data.get('notas')))
    db.commit()
    row = db.execute('''
        SELECT a.*, b.n_equipo, b.tag, b.marca, b.modelo, b.hp,
               p.calle, p.y_col, p.zona
        FROM asignaciones a
        JOIN bombas b ON a.bomba_id = b.id
        JOIN perforaciones p ON a.perforacion_id = p.id
        WHERE a.id = ?
    ''', (cur.lastrowid,)).fetchone()
    db.close()
    return jsonify(row_to_dict(row)), 201

@app.route('/api/asignaciones/<int:aid>', methods=['PUT'])
@editor_required
def update_asignacion(aid):
    data = request.get_json()
    fields = ['estado','fecha_montaje','fecha_desmontaje','notificada_por','relevado_el','notas']
    sets = ', '.join([f'{f} = ?' for f in fields]) + ', updated_at = CURRENT_TIMESTAMP'
    vals = [data.get(f) for f in fields] + [aid]
    db = get_db()
    db.execute(f'UPDATE asignaciones SET {sets} WHERE id = ?', vals)
    db.commit()
    row = db.execute('SELECT * FROM asignaciones WHERE id = ?', (aid,)).fetchone()
    db.close()
    return jsonify(row_to_dict(row))

@app.route('/api/asignaciones/<int:aid>/desmontar', methods=['POST'])
@editor_required
def desmontar(aid):
    data = request.get_json() or {}
    db = get_db()
    db.execute('''UPDATE asignaciones SET estado='Desmontado', fecha_desmontaje=?,
        notas=COALESCE(?,notas), updated_at=CURRENT_TIMESTAMP WHERE id=?''',
        (data.get('fecha_desmontaje'), data.get('notas'), aid))
    db.commit()
    row = db.execute('SELECT * FROM asignaciones WHERE id = ?', (aid,)).fetchone()
    db.close()
    return jsonify(row_to_dict(row))

@app.route('/api/asignaciones/<int:aid>', methods=['DELETE'])
@admin_required
def delete_asignacion(aid):
    db = get_db()
    db.execute('DELETE FROM asignaciones WHERE id = ?', (aid,))
    db.commit()
    db.close()
    return jsonify({'ok': True})

# ── CATALOGO ──
@app.route('/api/catalogo', methods=['GET'])
@login_required
def get_catalogo():
    db = get_db()
    rows = db.execute('SELECT * FROM catalogo ORDER BY hp, modelo').fetchall()
    db.close()
    result = []
    for r in rows:
        d = row_to_dict(r)
        d['curva'] = json.loads(d['curva_json']) if d.get('curva_json') else []
        del d['curva_json']
        result.append(d)
    return jsonify(result)

@app.route('/api/import/catalogo', methods=['POST'])
@admin_required
def import_catalogo():
    data = request.get_json()
    records = data.get('records', [])
    db = get_db()
    db.execute('DELETE FROM catalogo')
    for r in records:
        db.execute('INSERT INTO catalogo (marca,modelo,para,hp,etapas,descarga,largo_mm,curva_json) VALUES (?,?,?,?,?,?,?,?)',
            (r.get('marca'),r.get('modelo'),r.get('para'),r.get('hp'),
             r.get('etapas'),r.get('descarga'),r.get('largo_mm'),json.dumps(r.get('curva',[]))))
    db.commit()
    count = db.execute('SELECT COUNT(*) FROM catalogo').fetchone()[0]
    db.close()
    return jsonify({'ok': True, 'count': count})

# ── STATS ──
@app.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    db = get_db()
    stats = {
        'total_bombas': db.execute('SELECT COUNT(*) FROM bombas').fetchone()[0],
        'total_perforaciones': db.execute('SELECT COUNT(*) FROM perforaciones').fetchone()[0],
        'montadas': db.execute("SELECT COUNT(*) FROM asignaciones WHERE estado='Montado'").fetchone()[0],
        'disponibles': db.execute('''SELECT COUNT(*) FROM bombas WHERE id NOT IN
            (SELECT DISTINCT bomba_id FROM asignaciones WHERE estado='Montado')''').fetchone()[0],
        'por_zona': [row_to_dict(r) for r in db.execute('''
            SELECT p.zona, COUNT(*) as n FROM asignaciones a
            JOIN perforaciones p ON a.perforacion_id=p.id
            WHERE a.estado='Montado' GROUP BY p.zona''').fetchall()],
        'por_hp': [row_to_dict(r) for r in db.execute('''
            SELECT b.hp, COUNT(*) as n FROM asignaciones a
            JOIN bombas b ON a.bomba_id=b.id
            WHERE a.estado='Montado' AND b.hp IS NOT NULL GROUP BY b.hp ORDER BY b.hp''').fetchall()],
        'por_marca': [row_to_dict(r) for r in db.execute('''
            SELECT marca, COUNT(*) as n FROM bombas WHERE marca IS NOT NULL
            GROUP BY marca ORDER BY n DESC''').fetchall()],
        'modelos_top': [row_to_dict(r) for r in db.execute('''
            SELECT b.modelo, COUNT(*) as n FROM asignaciones a
            JOIN bombas b ON a.bomba_id=b.id
            WHERE a.estado='Montado' AND b.modelo IS NOT NULL
            GROUP BY b.modelo ORDER BY n DESC LIMIT 10''').fetchall()],
    }
    db.close()
    return jsonify(stats)

# ── USERS ──
@app.route('/api/users', methods=['GET'])
@admin_required
def get_users():
    db = get_db()
    rows = db.execute('SELECT id,username,role FROM users').fetchall()
    db.close()
    return jsonify([row_to_dict(r) for r in rows])

@app.route('/api/users', methods=['POST'])
@admin_required
def create_user():
    data = request.get_json()
    username = data.get('username','').strip()
    password = data.get('password','')
    role = data.get('role','viewer')
    if not username or not password:
        return jsonify({'error': 'Usuario y contraseña requeridos'}), 400
    db = get_db()
    try:
        db.execute('INSERT INTO users (username,password_hash,role) VALUES (?,?,?)',
                   (username, generate_password_hash(password), role))
        db.commit()
    except sqlite3.IntegrityError:
        db.close()
        return jsonify({'error': 'Usuario ya existe'}), 409
    db.close()
    return jsonify({'ok': True}), 201

@app.route('/api/users/<int:uid>', methods=['DELETE'])
@admin_required
def delete_user(uid):
    if uid == session.get('user_id'):
        return jsonify({'error': 'No podés eliminarte a vos mismo'}), 400
    db = get_db()
    db.execute('DELETE FROM users WHERE id = ?', (uid,))
    db.commit()
    db.close()
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
    db = get_db()
    db.execute('UPDATE users SET role=? WHERE id=?', (new_role, uid))
    db.commit()
    db.close()
    return jsonify({'ok': True})

@app.route('/api/me/password', methods=['PUT'])
@login_required
def change_password():
    data = request.get_json()
    current = data.get('current','')
    new_pw = data.get('new','')
    if not new_pw or len(new_pw) < 6:
        return jsonify({'error': 'Mínimo 6 caracteres'}), 400
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id=?', (session['user_id'],)).fetchone()
    if not user or not check_password_hash(user['password_hash'], current):
        db.close()
        return jsonify({'error': 'Contraseña actual incorrecta'}), 401
    db.execute('UPDATE users SET password_hash=? WHERE id=?',
               (generate_password_hash(new_pw), session['user_id']))
    db.commit()
    db.close()
    return jsonify({'ok': True})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
