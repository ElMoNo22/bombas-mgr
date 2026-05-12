"""
import_reparaciones.py
─────────────────────
Importa el historial completo de reparaciones desde seed_reparaciones.json a Turso.
Crea la tabla si no existe, y salta registros duplicados (por remito + n_equipo).

Uso:
    python import_reparaciones.py

Requiere: turso.py en el mismo directorio (ya existente en el proyecto).
"""

import json, os, sys
import turso as db_driver

SEED_FILE = os.path.join(os.path.dirname(__file__), 'seed_reparaciones.json')

CREATE_TABLE = '''
CREATE TABLE IF NOT EXISTS reparaciones (
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
    usuario_registro     TEXT DEFAULT 'importacion',
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
'''

INSERT_SQL = '''
INSERT INTO reparaciones (
    fecha_envio, remito, proveedor, descripcion, servicio,
    tag_actual, tag_reemplazado, numero_equipo, marca, modelo,
    hp, kw, amperes, serie, centro, ceco, referencia,
    presupuesto, fecha_cotizacion, costo_usd,
    estado_autorizacion, fecha_autorizacion,
    om, solped, fecha_solped, liberacion, fecha_liberacion,
    estadio, gcp, nota_justificacion,
    np, fecha_np_generacion, fecha_np_envio_prov,
    estado_entrega, fecha_entrega, remito_entrega,
    observaciones, responsable, estado, usuario_registro
) VALUES (
    ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
)
'''

def main():
    if not os.path.exists(SEED_FILE):
        print(f"ERROR: No se encontró {SEED_FILE}")
        sys.exit(1)

    with open(SEED_FILE, encoding='utf-8') as f:
        records = json.load(f)

    print(f"Cargando {len(records)} registros...")

    conn = db_driver.connect()

    # Crear tabla si no existe
    conn.execute(CREATE_TABLE)
    conn.commit()
    print("Tabla reparaciones OK")

    # También agregar columnas nuevas si la tabla ya existía con schema viejo
    new_cols = [
        ('tag_actual',          'TEXT'),
        ('tag_reemplazado',     'TEXT'),
        ('marca',               'TEXT'),
        ('modelo',              'TEXT'),
        ('hp',                  'TEXT'),
        ('kw',                  'TEXT'),
        ('amperes',             'TEXT'),
        ('serie',               'TEXT'),
        ('centro',              'TEXT'),
        ('ceco',                'TEXT'),
        ('referencia',          'TEXT'),
        ('fecha_cotizacion',    'TEXT'),
        ('costo_usd',           'REAL'),
        ('estado_autorizacion', 'TEXT'),
        ('fecha_autorizacion',  'TEXT'),
        ('om',                  'TEXT'),
        ('fecha_np_generacion', 'TEXT'),
        ('fecha_np_envio_prov', 'TEXT'),
        ('estado_entrega',      'TEXT'),
        ('remito_entrega',      'TEXT'),
        ('liberacion',          'TEXT'),
        ('fecha_liberacion',    'TEXT'),
        ('estadio',             'TEXT'),
        ('gcp',                 'TEXT'),
        ('fecha_cotizacion',    'TEXT'),
    ]
    for col, typ in new_cols:
        try:
            conn.execute(f'ALTER TABLE reparaciones ADD COLUMN {col} {typ}')
            conn.commit()
            print(f"  + columna {col}")
        except Exception:
            pass  # ya existe

    inserted = skipped = errors = 0
    for r in records:
        # Skip duplicates by remito+n_equipo
        cur = conn.execute(
            'SELECT id FROM reparaciones WHERE remito=? AND numero_equipo=?',
            (r.get('remito'), r.get('numero_equipo'))
        )
        if cur.fetchone():
            skipped += 1
            continue
        try:
            conn.execute(INSERT_SQL, (
                r.get('fecha_envio'),    r.get('remito'),        r.get('proveedor'),
                r.get('descripcion'),   r.get('servicio'),      r.get('tag_actual'),
                r.get('tag_reemplazado'), r.get('numero_equipo'), r.get('marca'),
                r.get('modelo'),        r.get('hp'),            r.get('kw'),
                r.get('amperes'),       r.get('serie'),         r.get('centro'),
                r.get('ceco'),          r.get('referencia'),    r.get('presupuesto'),
                r.get('fecha_cotizacion'), r.get('costo_usd'),
                r.get('estado_autorizacion'), r.get('fecha_autorizacion'),
                r.get('om'),            r.get('solped'),        r.get('fecha_solped'),
                r.get('liberacion'),    r.get('fecha_liberacion'),
                r.get('estadio'),       r.get('gcp'),           r.get('nota_justificacion'),
                r.get('np'),            r.get('fecha_np_generacion'), r.get('fecha_np_envio_prov'),
                r.get('estado_entrega'), r.get('fecha_entrega'), r.get('remito_entrega'),
                r.get('observaciones'), r.get('responsable'),   r.get('estado'),
                'importacion_excel'
            ))
            conn.commit()
            inserted += 1
        except Exception as e:
            print(f"  ERROR fila {r.get('numero_equipo')}: {e}")
            errors += 1

    conn.close()
    print(f"\n✅ Listo: {inserted} insertados, {skipped} duplicados saltados, {errors} errores")

if __name__ == '__main__':
    main()
