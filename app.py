import os, json, sqlite3, re
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'bombas-mgr-secret-2024-cambiar-en-prod')

DB_PATH = os.environ.get('DB_PATH', 'bombas.db')

# ═══════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════

def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        );

        CREATE TABLE IF NOT EXISTS perforaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            n_equipo TEXT,
            tag TEXT,
            tag_extraviado TEXT,
            zona TEXT,
            estado TEXT,
            denominacion TEXT,
            calle TEXT,
            entre TEXT,
            y_col TEXT,
            bombeo TEXT,
            marca TEXT,
            modelo TEXT,
            hp REAL,
            kw REAL,
            amperes TEXT,
            serie TEXT,
            salida TEXT,
            tazones TEXT,
            largo_mm REAL,
            ubicacion_actual TEXT,
            notificada_por TEXT,
            relevado_el TEXT,
            candado TEXT,
            tipo_cañeria TEXT,
            mts_cañeria TEXT,
            prof_trabajo_mts REAL,
            Q_m3h REAL,
            H_mca REAL,
            nivel_estatico REAL,
            nivel_dinamico REAL,
            fecha_lectura TEXT,
            fecha_notif TEXT,
            observaciones TEXT,
            id_estadio TEXT,
            sap_id TEXT,
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

    # Create default admin user if not exists
    existing = db.execute('SELECT id FROM users WHERE username = ?', ('admin',)).fetchone()
    if not existing:
        db.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                   ('admin', generate_password_hash('bombas2024'), 'admin'))

    db.commit()
    db.close()

# ═══════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'error': 'No autorizado'}), 401
            return redirect(url_for('login_page'))
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

# ═══════════════════════════════════════════
# PAGES
# ═══════════════════════════════════════════

@app.route('/')
@login_required
def index():
    return render_template('index.html', username=session.get('username'), role=session.get('role'))

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

# ═══════════════════════════════════════════
# API — PERFORACIONES
# ═══════════════════════════════════════════

def row_to_dict(row):
    return dict(row)

@app.route('/api/perforaciones', methods=['GET'])
@login_required
def get_perforaciones():
    db = get_db()
    rows = db.execute('SELECT * FROM perforaciones ORDER BY id').fetchall()
    db.close()
    return jsonify([row_to_dict(r) for r in rows])

@app.route('/api/perforaciones/<int:pid>', methods=['GET'])
@login_required
def get_perforacion(pid):
    db = get_db()
    row = db.execute('SELECT * FROM perforaciones WHERE id = ?', (pid,)).fetchone()
    db.close()
    if not row:
        return jsonify({'error': 'No encontrado'}), 404
    return jsonify(row_to_dict(row))

@app.route('/api/perforaciones', methods=['POST'])
@login_required
def create_perforacion():
    data = request.get_json()
    fields = ['n_equipo','tag','tag_extraviado','zona','estado','denominacion','calle','entre','y_col',
              'bombeo','marca','modelo','hp','kw','amperes','serie','salida','tazones','largo_mm',
              'ubicacion_actual','notificada_por','relevado_el','candado','tipo_cañeria','mts_cañeria',
              'prof_trabajo_mts','Q_m3h','H_mca','nivel_estatico','nivel_dinamico','fecha_lectura',
              'fecha_notif','observaciones','id_estadio','sap_id']
    vals = [data.get(f) for f in fields]
    placeholders = ','.join(['?']*len(fields))
    cols = ','.join(fields)
    db = get_db()
    cur = db.execute(f'INSERT INTO perforaciones ({cols}) VALUES ({placeholders})', vals)
    db.commit()
    new_id = cur.lastrowid
    row = db.execute('SELECT * FROM perforaciones WHERE id = ?', (new_id,)).fetchone()
    db.close()
    return jsonify(row_to_dict(row)), 201

@app.route('/api/perforaciones/<int:pid>', methods=['PUT'])
@login_required
def update_perforacion(pid):
    data = request.get_json()
    fields = ['n_equipo','tag','tag_extraviado','zona','estado','denominacion','calle','entre','y_col',
              'bombeo','marca','modelo','hp','kw','amperes','serie','salida','tazones','largo_mm',
              'ubicacion_actual','notificada_por','relevado_el','candado','tipo_cañeria','mts_cañeria',
              'prof_trabajo_mts','Q_m3h','H_mca','nivel_estatico','nivel_dinamico','fecha_lectura',
              'fecha_notif','observaciones','id_estadio','sap_id']
    sets = ', '.join([f'{f} = ?' for f in fields])
    sets += ', updated_at = CURRENT_TIMESTAMP'
    vals = [data.get(f) for f in fields] + [pid]
    db = get_db()
    db.execute(f'UPDATE perforaciones SET {sets} WHERE id = ?', vals)
    db.commit()
    row = db.execute('SELECT * FROM perforaciones WHERE id = ?', (pid,)).fetchone()
    db.close()
    if not row:
        return jsonify({'error': 'No encontrado'}), 404
    return jsonify(row_to_dict(row))

@app.route('/api/perforaciones/<int:pid>', methods=['DELETE'])
@admin_required
def delete_perforacion(pid):
    db = get_db()
    db.execute('DELETE FROM perforaciones WHERE id = ?', (pid,))
    db.commit()
    db.close()
    return jsonify({'ok': True})

@app.route('/api/perforaciones/<int:pid>/estado', methods=['PATCH'])
@login_required
def cambiar_estado(pid):
    data = request.get_json()
    nuevo_estado = data.get('estado')
    if not nuevo_estado:
        return jsonify({'error': 'Estado requerido'}), 400
    db = get_db()
    db.execute('UPDATE perforaciones SET estado = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
               (nuevo_estado, pid))
    db.commit()
    row = db.execute('SELECT * FROM perforaciones WHERE id = ?', (pid,)).fetchone()
    db.close()
    return jsonify(row_to_dict(row))

@app.route('/api/perforaciones/historial', methods=['GET'])
@login_required
def get_historial():
    calle = request.args.get('calle','').strip()
    y_col = request.args.get('y_col','').strip()
    exclude_id = request.args.get('exclude_id', type=int)
    if not calle or not y_col:
        return jsonify([])
    db = get_db()
    rows = db.execute(
        'SELECT * FROM perforaciones WHERE calle = ? AND y_col = ? AND id != ? ORDER BY fecha_notif DESC',
        (calle, y_col, exclude_id or 0)
    ).fetchall()
    db.close()
    return jsonify([row_to_dict(r) for r in rows])

# ═══════════════════════════════════════════
# API — CATÁLOGO
# ═══════════════════════════════════════════

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

@app.route('/api/catalogo/<int:cid>', methods=['GET'])
@login_required
def get_catalogo_item(cid):
    db = get_db()
    row = db.execute('SELECT * FROM catalogo WHERE id = ?', (cid,)).fetchone()
    db.close()
    if not row:
        return jsonify({'error': 'No encontrado'}), 404
    d = row_to_dict(row)
    d['curva'] = json.loads(d['curva_json']) if d.get('curva_json') else []
    del d['curva_json']
    return jsonify(d)

# ═══════════════════════════════════════════
# API — IMPORTAR EXCEL (JSON payload)
# ═══════════════════════════════════════════

@app.route('/api/import/perforaciones', methods=['POST'])
@admin_required
def import_perforaciones():
    data = request.get_json()
    records = data.get('records', [])
    if not records:
        return jsonify({'error': 'Sin datos'}), 400
    db = get_db()
    # Clear and reimport
    db.execute('DELETE FROM perforaciones')
    fields = ['n_equipo','tag','tag_extraviado','zona','estado','denominacion','calle','entre','y_col',
              'bombeo','marca','modelo','hp','kw','amperes','serie','salida','tazones','largo_mm',
              'ubicacion_actual','notificada_por','relevado_el','candado','tipo_cañeria','mts_cañeria',
              'prof_trabajo_mts','Q_m3h','H_mca','nivel_estatico','nivel_dinamico','fecha_lectura',
              'fecha_notif','observaciones','id_estadio','sap_id']
    placeholders = ','.join(['?']*len(fields))
    cols = ','.join(fields)
    for r in records:
        vals = [r.get(f) for f in fields]
        db.execute(f'INSERT INTO perforaciones ({cols}) VALUES ({placeholders})', vals)
    db.commit()
    count = db.execute('SELECT COUNT(*) FROM perforaciones').fetchone()[0]
    db.close()
    return jsonify({'ok': True, 'count': count})

@app.route('/api/import/catalogo', methods=['POST'])
@admin_required
def import_catalogo():
    data = request.get_json()
    records = data.get('records', [])
    if not records:
        return jsonify({'error': 'Sin datos'}), 400
    db = get_db()
    db.execute('DELETE FROM catalogo')
    for r in records:
        db.execute(
            'INSERT INTO catalogo (marca, modelo, para, hp, etapas, descarga, largo_mm, curva_json) VALUES (?,?,?,?,?,?,?,?)',
            (r.get('marca'), r.get('modelo'), r.get('para'), r.get('hp'),
             r.get('etapas'), r.get('descarga'), r.get('largo_mm'),
             json.dumps(r.get('curva', [])))
        )
    db.commit()
    count = db.execute('SELECT COUNT(*) FROM catalogo').fetchone()[0]
    db.close()
    return jsonify({'ok': True, 'count': count})

# ═══════════════════════════════════════════
# API — USUARIOS (solo admin)
# ═══════════════════════════════════════════

@app.route('/api/users', methods=['GET'])
@admin_required
def get_users():
    db = get_db()
    rows = db.execute('SELECT id, username, role FROM users').fetchall()
    db.close()
    return jsonify([row_to_dict(r) for r in rows])

@app.route('/api/users', methods=['POST'])
@admin_required
def create_user():
    data = request.get_json()
    username = data.get('username','').strip()
    password = data.get('password','')
    role = data.get('role', 'user')
    if not username or not password:
        return jsonify({'error': 'Usuario y contraseña requeridos'}), 400
    db = get_db()
    try:
        db.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
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

@app.route('/api/me/password', methods=['PUT'])
@login_required
def change_password():
    data = request.get_json()
    current = data.get('current','')
    new_pw = data.get('new','')
    if not new_pw or len(new_pw) < 6:
        return jsonify({'error': 'La nueva contraseña debe tener al menos 6 caracteres'}), 400
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    if not user or not check_password_hash(user['password_hash'], current):
        db.close()
        return jsonify({'error': 'Contraseña actual incorrecta'}), 401
    db.execute('UPDATE users SET password_hash = ? WHERE id = ?',
               (generate_password_hash(new_pw), session['user_id']))
    db.commit()
    db.close()
    return jsonify({'ok': True})

# ═══════════════════════════════════════════
# API — SESSION INFO
# ═══════════════════════════════════════════

@app.route('/api/me')
@login_required
def me():
    return jsonify({'username': session['username'], 'role': session['role']})

# ═══════════════════════════════════════════
# INIT & RUN
# ═══════════════════════════════════════════

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
