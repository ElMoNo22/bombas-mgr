-- ╔══════════════════════════════════════════════════════════╗
-- ║  telemetria_import.sql  —  generado desde Excel          ║
-- ║  107 módems · 104 líneas                                 ║
-- ║                                                          ║
-- ║  ORDEN DE EJECUCIÓN EN TURSO (1 statement por vez):      ║
-- ║  1. Ejecutar los 7 ALTER TABLE                           ║
-- ║  2. Ejecutar los 107 INSERT modems_telemetria            ║
-- ║  3. Ejecutar los 104 INSERT lineas_telemetria            ║
-- ╚══════════════════════════════════════════════════════════╝

-- ═══════════════════════════════════════════
-- PASO 1: columnas nuevas en modems_telemetria
-- (correr de a 1 si ya existe alguna)
-- ═══════════════════════════════════════════
ALTER TABLE modems_telemetria ADD COLUMN oid_externo INTEGER;
ALTER TABLE modems_telemetria ADD COLUMN unitid INTEGER;
ALTER TABLE modems_telemetria ADD COLUMN grdid INTEGER;
ALTER TABLE modems_telemetria ADD COLUMN tipo_establecimiento TEXT;
ALTER TABLE modems_telemetria ADD COLUMN numero_establecimiento INTEGER;
ALTER TABLE modems_telemetria ADD COLUMN sucursal TEXT;
ALTER TABLE modems_telemetria ADD COLUMN sap TEXT;

-- ═══════════════════════════════════════════
-- PASO 2: INSERT modems (107 registros)
-- ═══════════════════════════════════════════
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  98, '163', 163, 55, 'EXEMYS', 'GRD',
  'POZO', 58,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 61 Y 31' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  1613, '592', 592, 409, 'EXEMYS', 'GRD',
  'POZO', 63,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 609 Y 16' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  54, '217', 217, 98, 'EXEMYS', 'GRD',
  'POZO', 54,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 139 Y 60' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  215, '271', 271, 160, 'EXEMYS', 'GRD',
  'POZO', 1,
  'Magdalena', 'MGD',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo Vieytes' LIMIT 1),
  'inactivo',
  'LINEA PENDIENTE DE REACTIVACIÓN',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  91, '159', 159, 51, 'EXEMYS', 'GRD',
  'EEC', 1,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'EEC 31 Y 38' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  204, '268', 268, 148, 'EXEMYS', 'GRD',
  'EEA', 2,
  'Magdalena', 'MGD',
  (SELECT id FROM perforaciones WHERE denominacion = 'EEA Arbuco' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  78, '594', 594, 410, 'EXEMYS', 'GRD',
  'POZO', 43,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 67 Y 146' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  143, '263', 263, 144, 'EXEMYS', 'GRD',
  'POZO', 99,
  'Manuel B. Gonnet', 'GON',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 25 Y 511' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  52, '358', 358, 86, 'EXEMYS', 'GRD',
  'POZO', 30,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 137 Y 90' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  47, '382', 382, 693, 'EXEMYS', 'GRD',
  'POZO', 27,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 134 Y 531' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  2028, '412', 412, 423, 'EXEMYS', 'GRD',
  'POZO', 74,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 167 Y 70' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  89, '150', 150, 50, 'EXEMYS', 'GRD',
  'EEA', 3,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'EEA Usina Parque San Martin' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  1579, '178', 178, 70, 'EXEMYS', 'GRD',
  'POZO', 164,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 31 y 522' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  93, '161', 161, 52, 'EXEMYS', 'GRD',
  'EEA', 2,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'EEA 131 Y 68' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  9, '274', 274, 116, 'EXEMYS', 'GRD',
  'POZO', 6,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 25 Y 60' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  2022, '609', 609, 430, 'EXEMYS', 'GRD',
  'POZO', 0,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 169 Y 60' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  102, '376', 376, 687, 'EXEMYS', 'GRD',
  'POZO', 58,
  'La Plata Norte', 'LPN',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 10 Y 80' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  355, '374', 374, 685, 'EXEMYS', 'GRD',
  'POZO', 145,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 173 y 75' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  26, '521', 521, 703, 'EXEMYS', 'GRD',
  'POZO', 16,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 161 Y 47' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  1588, '584', 584, 406, 'EXEMYS', 'GRD',
  'POZO', 165,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo DIAG 73 Y 31' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  343, '390', 390, 1000, 'EXEMYS', 'GRD',
  'TOMA', 1,
  'Ensenada', 'ENS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Toma Punta Lara' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  68, '225', 225, 93, 'EXEMYS', 'GRD',
  'POZO', 38,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 143 Y 52' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  23, '352', 352, 664, 'EXEMYS', 'GRD',
  'POZO', 13,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 131 Y 42' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  2034, '610', 610, 711, 'EXEMYS', 'GRD',
  'POZO', 138,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = '29 Y 520' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  44, '601', 601, 417, 'EXEMYS', 'GRD',
  'POZO', 135,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 134 Y 33' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  40, '219', 219, 87, 'EXEMYS', 'GRD',
  'POZO', 23,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 80 Y 137' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  330, '372', 372, 683, 'EXEMYS', 'GRD',
  'POZO', 0,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 72 y 170' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  11, '364', 364, 141, 'EXEMYS', 'GRD',
  'POZO', 7,
  'Manuel B. Gonnet', 'GON',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 25 Y 514' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  86, '603', 603, 419, 'EXEMYS', 'GRD',
  'POZO', 48,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 155 Y 45' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  66, '597', 597, 413, 'EXEMYS', 'GRD',
  'POZO', 37,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 143 Y 47' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  80, '602', 602, 418, 'EXEMYS', 'GRD',
  'POZO', 44,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 148 Y 32' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  74, '171', 171, 63, 'EXEMYS', 'GRD',
  'POZO', 41,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 143 Y 70' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  17, '351', 351, 663, 'EXEMYS', 'GRD',
  'POZO', 10,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 25 Y 32' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  64, '599', 599, 415, 'EXEMYS', 'GRD',
  'POZO', 36,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 143 42 Y 43' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  329, '363', 363, 670, 'EXEMYS', 'GRD',
  'POZO', 0,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 72 Y 165' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  62, '598', 598, 414, 'EXEMYS', 'GRD',
  'POZO', 35,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 143 40 Y 41' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  126, '386', 386, 696, 'EXEMYS', 'GRD',
  'POZO', 82,
  'La Plata Norte', 'LPN',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 6 Y 99' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  42, '353', 353, 665, 'EXEMYS', 'GRD',
  'POZO', 24,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 131 Y 37' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  2029, '589', 589, 1003, 'EXEMYS', 'GRD',
  'EEA', 1,
  'La Plata Norte', 'LPN',
  (SELECT id FROM perforaciones WHERE denominacion = 'EEA Usina Bosque HMI' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  1156, '563', 563, 401, 'EXEMYS', 'GRD',
  'POZO', NULL,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 137 Y 68' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  342, '384', 384, 695, 'EXEMYS', 'GRD',
  'POZO', 43,
  'La Plata Norte', 'LPN',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 12 Y 87' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  1153, '3004', 3004, 3004, 'TESACOM', 'TESACOM',
  'CAUDALIMETRO', 0,
  'Gonnet', 'GON',
  (SELECT id FROM perforaciones WHERE denominacion = 'INC SA' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  305, '3003', 3003, 3003, 'TESACOM', 'TESACOM',
  'CAUDALIMETRO', 9,
  'La Plata Norte', 'LPN',
  (SELECT id FROM perforaciones WHERE denominacion = 'UP 9 La Plata' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  352, '520', 520, 702, 'EXEMYS', 'GRD',
  'EEC', 1,
  'Pipinas', 'PPN',
  (SELECT id FROM perforaciones WHERE denominacion = 'EEC Pipinas' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  354, '375', 375, 686, 'EXEMYS', 'GRD',
  'POZO', 84,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 134 y 90' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  306, '3005', 3005, 3005, 'TESACOM', 'TESACOM',
  'CAUDALIMETRO', 5,
  'Ensenada', 'ENS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Ternium Ensenada' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  220, '288', 288, 212, 'EXEMYS', 'GRD',
  'EEA', 1,
  'La Plata Norte', 'LPN',
  (SELECT id FROM perforaciones WHERE denominacion = 'EEA Usina Parque Saavedra' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  1587, '585', 585, 407, 'EXEMYS', 'GRD',
  'POZO', 0,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 527 Y 28' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  219, '287', 287, 211, 'EXEMYS', 'GRD',
  'POZO', 1,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 19 Y 66' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  30, '527', 527, 1002, 'EXEMYS', 'GRD',
  'POZO', 18,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 30 Y 77' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  318, '3000', 3000, 3000, 'TESACOM', 'TESACOM',
  'CAUDALIMETRO', 0,
  'Gonnet', 'GON',
  (SELECT id FROM perforaciones WHERE denominacion = 'Walmart La Plata' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  309, '349', 349, 661, 'EXEMYS', 'GRD',
  'EEA', 1,
  'La Plata Norte', 'LPN',
  (SELECT id FROM perforaciones WHERE denominacion = 'EEA 120 Y 33' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  108, '361', 361, 674, 'EXEMYS', 'GRD',
  'POZO', 61,
  'La Plata Norte', 'LPN',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 12B Y 82' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  49, '600', 600, 416, 'EXEMYS', 'GRD',
  'POZO', 28,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 137 E/33 Y 34' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  206, '270', 270, 151, 'EXEMYS', 'GRD',
  'POZO', NULL,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 149 Y 35' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  72, '227', 227, 95, 'EXEMYS', 'GRD',
  'POZO', 40,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 143 E/65 Y 66' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  70, '354', 354, 668, 'EXEMYS', 'GRD',
  'POZO', 39,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 143 Y 60' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  1565, '582', 582, 684, 'EXEMYS', 'GRD',
  'POZO', 66,
  'La Plata Norte', 'LPN',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 116 Y 96' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  216, '275', 275, 202, 'EXEMYS', 'GRD',
  'POZO', 61,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 158 Y 38' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  5, '342', 342, 140, 'EXEMYS', 'GRD',
  'POZO', 3,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 22 Y 611' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  244, '331', 331, 329, 'EXEMYS', 'GRD',
  'POZO', 11,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 167 Y 66' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  119, '177', 177, 69, 'EXEMYS', 'GRD',
  'POZO', 74,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 24 Y 76' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  339, '541', 541, 1010, 'EXEMYS', 'GRD',
  'EEA', 1,
  'La Plata Norte', 'LPN',
  (SELECT id FROM perforaciones WHERE denominacion = 'EEA Usina Bosque' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  247, '334', 334, 332, 'EXEMYS', 'GRD',
  'POZO', 0,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 27 Y 52' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  341, '383', 383, 694, 'EXEMYS', 'GRD',
  'POZO', NULL,
  'La Plata Norte', 'LPN',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 9 Y 76' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  101, '165', 165, 57, 'EXEMYS', 'GRD',
  'POZO', 10,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 47 Y 22' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  136, '387', 387, 697, 'EXEMYS', 'GRD',
  'POZO', 92,
  'La Plata Norte', 'LPN',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 7 Y 80' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  246, '333', 333, 331, 'EXEMYS', 'GRD',
  'POZO', 0,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 54 Y 26 PSM' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  87, '221', 221, 89, 'EXEMYS', 'GRD',
  'POZO', 49,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 155 Y 58' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  344, '391', 391, 1001, 'EXEMYS', 'GRD',
  'PPA', 1,
  'Ensenada', 'ENS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Cisternas Punta Lara' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  28, '224', 224, 92, 'EXEMYS', 'GRD',
  'POZO', 17,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 52 Y 147' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  131, '377', 377, 688, 'EXEMYS', 'GRD',
  'POZO', 87,
  'La Plata Norte', 'LPN',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 7 Y 616' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  122, '273', 273, 200, 'EXEMYS', 'GRD',
  'POZO', 78,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 38 Y 24' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  2036, '614', 614, 114, 'EXEMYS', 'GRD',
  'POZO', 120,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 19 Y 526' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  2037, '615', 615, 997, 'EXEMYS', 'GRD',
  'POZO', 7,
  'Magdalena', 'MGD',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 7 Magdalena' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  32, '172', 172, 64, 'EXEMYS', 'GRD',
  'POZO', 19,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 69 Y 140' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  1564, '581', 581, 405, 'EXEMYS', 'GRD',
  'POZO', 8,
  'Manuel B. Gonnet', 'GON',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 489 Y 20' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  103, '166', 166, 58, 'EXEMYS', 'GRD',
  'POZO', 32,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 30 Y 35' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  129, '223', 223, 91, 'EXEMYS', 'GRD',
  'POZO', 85,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 63 Y 140' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  1619, '604', 604, 420, 'EXEMYS', 'GRD',
  'POZO', 25,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 149 Y 74' LIMIT 1),
  'fuera_servicio',
  'TABLERO F/S',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  1621, '605', 605, 421, 'EXEMYS', 'GRD',
  'POZO', 27,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 66 Y 31' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  82, '355', 355, 666, 'EXEMYS', 'GRD',
  'POZO', 45,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 66 Y 149' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  144, '262', 262, 143, 'EXEMYS', 'GRD',
  'POZO', 100,
  'Manuel B. Gonnet', 'GON',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 511 Y 21' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  90, '596', 596, 412, 'EXEMYS', 'GRD',
  'POZO', 50,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 155 Y 66' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  59, '229', 229, 97, 'EXEMYS', 'GRD',
  'POZO', 33,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 140 Y 52' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  36, '226', 226, 94, 'EXEMYS', 'GRD',
  'POZO', 21,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 74 Y 143' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  125, '389', 389, 699, 'EXEMYS', 'GRD',
  'POZO', 81,
  'La Plata Norte', 'LPN',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 6 BIS Y 613' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  105, '167', 167, 59, 'EXEMYS', 'GRD',
  'POZO', 0,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 56 Y 140' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  57, '176', 176, 68, 'EXEMYS', 'GRD',
  'POZO', 76,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 140 Y 40' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  123, '388', 388, 698, 'EXEMYS', 'GRD',
  'POZO', 79,
  'La Plata Norte', 'LPN',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 5 Y 618' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  2038, '611', 611, 999, 'EXEMYS', 'GRD',
  'EEA', 1,
  'Ensenada', 'ENS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Cestino Y Moreno' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  34, '218', 218, 85, 'EXEMYS', 'GRD',
  'POZO', 20,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 71 Y 25' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  113, '228', 228, 96, 'EXEMYS', 'GRD',
  'POZO', 67,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 137 E/45 Y 46' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  2039, '616', 616, 995, 'EXEMYS', 'GRD',
  'POZO', 10,
  'La Plata Norte', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 16 Y 526' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  172, '169', 169, 61, 'EXEMYS', 'GRD',
  'POZO', 115,
  'La Plata Norte', 'LPN',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo Belgrano Y 514' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  315, '347', 347, 142, 'EXEMYS', 'GRD',
  'POZO', 50,
  'La Plata Norte', 'LPN',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 7 Y 626' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  84, '356', 356, 671, 'EXEMYS', 'GRD',
  'POZO', 46,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 152 Y 60' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  158, '571', 571, 402, 'EXEMYS', 'GRD',
  'POZO', 107,
  'Manuel B. Gonnet', 'GON',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 17 Y 495' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  134, '170', 170, 62, 'EXEMYS', 'GRD',
  'POZO', 90,
  'La Plata Norte', 'LPN',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 7 Y 630' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  51, '230', 230, 99, 'EXEMYS', 'GRD',
  'POZO', 92,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 137 E/56 Y 57' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  149, '266', 266, 147, 'EXEMYS', 'GRD',
  'POZO', 103,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 511 Y 139' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  94, '595', 595, 411, 'EXEMYS', 'GRD',
  'POZO', 92,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 155 Y 74' LIMIT 1),
  'fuera_servicio',
  'TABLERO F/S',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  1566, '583', 583, 662, 'EXEMYS', 'GRD',
  'POZO', 91,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 78 y 25' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  2025, '346', 346, 660, 'EXEMYS', 'GRD',
  'POZO', 139,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 19 Y 38' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  2046, '617', 617, 998, 'EXEMYS', 'GRD',
  'POZO', 21,
  'La Plata Sur', 'LPS',
  (SELECT id FROM perforaciones WHERE denominacion = 'Pozo 610 Y 11' LIMIT 1),
  'activo',
  '',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  2031, '591', 591, 1004, 'EXEMYS', 'GRD',
  'EEA', 1,
  'La Plata Norte', 'LPN',
  (SELECT id FROM perforaciones WHERE denominacion = 'EEA Usina Parque Saavedra HMI' LIMIT 1),
  'activo',
  'LINEA ACTIVA NO RESPONDE SMS',
  datetime('now'), datetime('now')
);
INSERT INTO modems_telemetria (
  oid_externo, tag_tablero, unitid, grdid, marca, modelo,
  tipo_establecimiento, numero_establecimiento, sucursal, sap,
  perforacion_id, estado, observaciones, created_at, updated_at
) VALUES (
  205, '269', 269, 149, 'EXEMYS', 'GRD',
  'EEA', 1,
  'Magdalena', 'MGD',
  (SELECT id FROM perforaciones WHERE denominacion = 'EEA Empalme' LIMIT 1),
  'inactivo',
  'LINEA PENDIENTE DE REACTIVACIÓN',
  datetime('now'), datetime('now')
);

-- ═══════════════════════════════════════════
-- PASO 3: INSERT lineas_telemetria (104 registros)
-- ═══════════════════════════════════════════
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '1138980359', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 163 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '1138980359', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 592 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2213030830', 'kite', 'CLARO',
  (SELECT id FROM modems_telemetria WHERE unitid = 217 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2213032855', 'kite', 'CLARO',
  (SELECT id FROM modems_telemetria WHERE unitid = 271 LIMIT 1),
  'baja',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2213033485', 'kite', 'CLARO',
  (SELECT id FROM modems_telemetria WHERE unitid = 159 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2213036306', 'kite', 'CLARO',
  (SELECT id FROM modems_telemetria WHERE unitid = 268 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2213198926', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 594 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2213563937', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 263 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2213568100', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 358 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2213599038', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 382 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2214200496', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 412 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2214208745', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 150 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2214361642', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 178 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2214364572', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 161 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2214369174', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 274 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215047291', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 609 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215057450', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 376 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215221192', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 374 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215225741', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 521 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215246652', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 584 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215257253', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 390 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215378492', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 225 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215381786', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 352 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215435906', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 610 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215438599', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 601 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215456956', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 219 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215462455', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 372 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215469485', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 364 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215481802', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 603 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215481864', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 597 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215482023', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 602 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215482092', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 171 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215482177', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 351 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215482237', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 599 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215482256', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 363 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215482515', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 598 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215482529', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 386 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215482564', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 353 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215624956', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 589 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215641579', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 563 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215655677', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 384 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215756419', 'standard', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 3004 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215891858', 'standard', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 3003 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215892008', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 520 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215914709', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 375 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215992821', 'standard', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 3005 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216017075', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 288 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216126335', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 585 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216146469', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 287 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216154307', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 527 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216169443', 'standard', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 3000 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216206054', 'kite', 'CLARO',
  (SELECT id FROM modems_telemetria WHERE unitid = 349 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216206064', 'kite', 'CLARO',
  (SELECT id FROM modems_telemetria WHERE unitid = 361 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216206068', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 600 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216206069', 'kite', 'CLARO',
  (SELECT id FROM modems_telemetria WHERE unitid = 270 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216206078', 'kite', 'CLARO',
  (SELECT id FROM modems_telemetria WHERE unitid = 227 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216206079', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 354 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216206092', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 582 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216206098', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 275 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216206099', 'kite', 'CLARO',
  (SELECT id FROM modems_telemetria WHERE unitid = 342 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216206101', 'kite', 'CLARO',
  (SELECT id FROM modems_telemetria WHERE unitid = 331 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216206106', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 177 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216206108', 'kite', 'CLARO',
  (SELECT id FROM modems_telemetria WHERE unitid = 541 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216206109', 'kite', 'CLARO',
  (SELECT id FROM modems_telemetria WHERE unitid = 334 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216373494', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 383 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216381771', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 165 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216427888', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 387 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216549071', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 333 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216681272', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 221 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216683510', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 391 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216694440', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 224 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216719295', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 377 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216720007', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 273 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216720009', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 614 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216720013', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 615 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216720021', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 172 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216720026', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 581 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216720037', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 166 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216720040', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 223 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216720042', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 604 LIMIT 1),
  'baja',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216720048', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 605 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216720052', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 355 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216720053', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 262 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216720059', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 596 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216720062', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 229 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216720064', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 226 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216720067', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 389 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216720071', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 167 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216720077', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 176 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216720079', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 388 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216720080', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 611 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216720084', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 218 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216720087', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 228 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216720093', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 616 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216720095', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 169 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216720097', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 347 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216720101', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 356 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216720110', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 571 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216726015', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 170 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216730302', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 230 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216775713', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 266 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216206083', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 583 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2215077248', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 346 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
INSERT INTO lineas_telemetria (
  numero, tipo_sim, operadora, modem_id, estado, fecha_alta, created_at, updated_at
) VALUES (
  '2216726015', 'kite', 'MOVISTAR',
  (SELECT id FROM modems_telemetria WHERE unitid = 617 LIMIT 1),
  'activa',
  date('now'), datetime('now'), datetime('now')
);
