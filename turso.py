"""
turso.py — Turso HTTP API wrapper corregido
"""

import os
import requests as req_lib
import json as jsonlib
import sys

TURSO_URL   = os.environ.get('TURSO_URL', '')
TURSO_TOKEN = os.environ.get('TURSO_TOKEN', '')
DB_PATH     = os.environ.get('DB_PATH', 'bombas.db')


def _http_url():
    return TURSO_URL.replace('libsql://', 'https://') + '/v2/pipeline'


def _headers():
    return {
        'Authorization': f'Bearer {TURSO_TOKEN}',
        'Content-Type': 'application/json'
    }


def _send_stmts(stmts):
    requests_payload = [{'type': 'execute', 'stmt': s} for s in stmts]
    requests_payload.append({'type': 'close'})

    body = jsonlib.dumps({'requests': requests_payload}, ensure_ascii=False).encode('utf-8')

    resp = req_lib.post(
        _http_url(),
        headers={**_headers(), 'Content-Type': 'application/json; charset=utf-8'},
        data=body,
        timeout=30
    )

    if not resp.ok:
        print(f"Turso {resp.status_code}: {resp.text[:600]}", file=sys.stderr)
        print(f"Payload size: {len(body)/1024:.1f} KB", file=sys.stderr)

    resp.raise_for_status()
    return resp.json()['results']


def _parse_result(result):
    if result.get('type') == 'error':
        msg = result.get('error', {})
        if isinstance(msg, dict):
            msg = msg.get('message', str(msg))
        raise Exception(f'Turso error: {msg}')

    rows = []
    if result.get('type') == 'ok':
        res = result.get('response', {}).get('result', {})
        cols = [c['name'] for c in res.get('cols', [])]
        for row in res.get('rows', []):
            d = {}
            for i, col in enumerate(cols):
                cell = row[i]
                val = cell.get('value')
                typ = cell.get('type', '')
                if typ == 'null':
                    val = None
                elif typ == 'integer':
                    val = int(val) if val is not None else None
                elif typ == 'float':
                    val = float(val) if val is not None else None
                d[col] = val
            rows.append(d)
    return rows


def _build_args(params):
    """¡ESTA ES LA FUNCIÓN CORREGIDA! value siempre como string"""
    args = []
    for p in (params or []):
        if p is None:
            args.append({'type': 'null'})
        elif isinstance(p, bool):
            args.append({'type': 'integer', 'value': str(int(p))})
        elif isinstance(p, int):
            args.append({'type': 'integer', 'value': str(p)})           # ← Corregido
        elif isinstance(p, float):
            if p != p:  # NaN
                args.append({'type': 'null'})
            else:
                args.append({'type': 'float', 'value': str(p)})         # ← Corregido
        else:
            args.append({'type': 'text', 'value': str(p)})
    return args


# ==================== Cursor y Row ====================
class TursoCursor:
    def __init__(self, rows):
        self._rows = rows
        self._pos = 0
        self.description = [(k,) for k in rows[0].keys()] if rows else []

    def fetchone(self):
        if self._pos < len(self._rows):
            r = self._rows[self._pos]
            self._pos += 1
            return TursoRow(r)
        return None

    def fetchall(self):
        rows = [TursoRow(r) for r in self._rows[self._pos:]]
        self._pos = len(self._rows)
        return rows


class TursoRow(dict):
    def __getattr__(self, k):
        try:
            return self[k]
        except KeyError:
            raise AttributeError(k)


# ==================== Connection ====================
class TursoConnection:
    def execute(self, sql, params=()):
        stmt = {'sql': sql}
        if params:
            stmt['args'] = _build_args(params)
        results = _send_stmts([stmt])
        rows = _parse_result(results[0])
        return TursoCursor(rows)

    def executemany(self, sql, seq_of_params):
        CHUNK_SIZE = 20
        params_list = list(seq_of_params)
        for i in range(0, len(params_list), CHUNK_SIZE):
            chunk = params_list[i:i+CHUNK_SIZE]
            stmts = []
            for p in chunk:
                stmt = {'sql': sql}
                if p:
                    stmt['args'] = _build_args(p)
                stmts.append(stmt)
            if stmts:
                results = _send_stmts(stmts)
                for r in results:
                    _parse_result(r)

    def executescript(self, sql):
        stmts_raw = [s.strip() for s in sql.split(';') if s.strip()]
        for stmt_sql in stmts_raw:
            try:
                _send_stmts([{'sql': stmt_sql}])
            except Exception as e:
                if 'already exists' not in str(e).lower():
                    raise

    def commit(self): pass
    def sync(self): pass
    def close(self): pass


def connect():
    if TURSO_URL and TURSO_TOKEN:
        return TursoConnection()
    else:
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
