"""
migrate_telecelmgr.py
Crea las tablas de CelMGR y TeleMGR en la DB existente.
Correr UNA SOLA VEZ desde la raíz del repo.

Local:
    TURSO_URL=... TURSO_TOKEN=... python migrate_telecelmgr.py

Render (one-off):
    Ir a Dashboard → tu servicio → Shell → python migrate_telecelmgr.py
"""
import turso

TABLAS = """
CREATE TABLE IF NOT EXISTS empleados (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    legajo          TEXT UNIQUE NOT NULL,
    nombre          TEXT NOT NULL,
    apellido        TEXT NOT NULL,
    puesto          TEXT,
    sector          TEXT,
    lugar_trabajo   TEXT,
    email           TEXT,
    activo          INTEGER DEFAULT 1,
    fecha_ingreso   TEXT,
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS equipos_cel (
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
);

CREATE TABLE IF NOT EXISTS lineas_cel (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    numero          TEXT UNIQUE NOT NULL,
    operadora       TEXT,
    plan            TEXT,
    datos_gb        REAL,
    vencimiento     TEXT,
    iccid           TEXT,
    equipo_id       INTEGER REFERENCES equipos_cel(id) ON DELETE SET NULL,
    estado          TEXT DEFAULT 'activa',
    observaciones   TEXT,
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS asignaciones_cel (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    equipo_id       INTEGER NOT NULL REFERENCES equipos_cel(id),
    empleado_id     INTEGER NOT NULL REFERENCES empleados(id),
    linea_id        INTEGER REFERENCES lineas_cel(id),
    fecha_desde     TEXT NOT NULL,
    fecha_hasta     TEXT,
    acta_nro        TEXT,
    observaciones   TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS tickets_cel (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nro_ticket      TEXT UNIQUE,
    equipo_id       INTEGER NOT NULL REFERENCES equipos_cel(id),
    empleado_id     INTEGER REFERENCES empleados(id),
    descripcion     TEXT NOT NULL,
    tipo            TEXT,
    estado          TEXT DEFAULT 'abierto',
    en_garantia     INTEGER DEFAULT 0,
    service_nombre  TEXT,
    service_ingreso TEXT,
    service_egreso  TEXT,
    costo           REAL,
    resolucion      TEXT,
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS modems_telemetria (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    marca             TEXT NOT NULL,
    modelo            TEXT NOT NULL,
    nro_serie         TEXT,
    imei              TEXT UNIQUE,
    firmware          TEXT,
    ip_asignada       TEXT,
    tag_tablero       TEXT UNIQUE NOT NULL,
    perforacion_id    INTEGER REFERENCES perforaciones(id) ON DELETE SET NULL,
    estado            TEXT DEFAULT 'activo',
    ultimo_contacto   TEXT,
    fecha_instalacion TEXT,
    garantia_hasta    TEXT,
    observaciones     TEXT,
    created_at        TEXT DEFAULT (datetime('now')),
    updated_at        TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS lineas_telemetria (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    numero          TEXT,
    tipo_sim        TEXT NOT NULL,
    operadora       TEXT,
    iccid           TEXT UNIQUE,
    apn             TEXT,
    ip_sim          TEXT,
    modem_id        INTEGER REFERENCES modems_telemetria(id) ON DELETE SET NULL,
    estado          TEXT DEFAULT 'activa',
    fecha_alta      TEXT,
    observaciones   TEXT,
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sensores (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    modem_id        INTEGER NOT NULL REFERENCES modems_telemetria(id) ON DELETE CASCADE,
    canal           TEXT NOT NULL,
    tipo            TEXT NOT NULL,
    descripcion     TEXT,
    tipo_senal      TEXT,
    rango_min       REAL,
    rango_max       REAL,
    unidad          TEXT,
    alarma_min      REAL,
    alarma_max      REAL,
    activo          INTEGER DEFAULT 1,
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS intervenciones_telemetria (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    modem_id        INTEGER NOT NULL REFERENCES modems_telemetria(id),
    tipo            TEXT NOT NULL,
    descripcion     TEXT NOT NULL,
    tecnico         TEXT,
    fecha           TEXT NOT NULL,
    costo           REAL,
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_asig_cel_equipo    ON asignaciones_cel(equipo_id);
CREATE INDEX IF NOT EXISTS idx_asig_cel_empleado  ON asignaciones_cel(empleado_id);
CREATE INDEX IF NOT EXISTS idx_tickets_cel_equipo ON tickets_cel(equipo_id);
CREATE INDEX IF NOT EXISTS idx_tickets_cel_estado ON tickets_cel(estado);
CREATE INDEX IF NOT EXISTS idx_modems_perf        ON modems_telemetria(perforacion_id);
CREATE INDEX IF NOT EXISTS idx_sensores_modem     ON sensores(modem_id);
CREATE INDEX IF NOT EXISTS idx_lineas_tel_modem   ON lineas_telemetria(modem_id);
"""

def main():
    db = turso.connect()
    statements = [s.strip() for s in TABLAS.split(';') if s.strip()]
    ok = 0
    skip = 0
    for stmt in statements:
        try:
            db.execute(stmt)
            ok += 1
        except Exception as e:
            if 'already exists' in str(e).lower():
                skip += 1
            else:
                print(f"  ERROR: {e}")
                print(f"  SQL: {stmt[:80]}...")
    print(f"✓ Migración completada — {ok} statements OK, {skip} ya existían")

if __name__ == '__main__':
    main()
