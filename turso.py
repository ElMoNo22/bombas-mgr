"""
turso.py — Turso HTTP API wrapper that mimics sqlite3 interface
Uses Turso's /v2/pipeline endpoint
"""
import os, requests, json as jsonlib

TURSO_URL   = os.environ.get('TURSO_URL', '')
TURSO_TOKEN = os.environ.get('TURSO_TOKEN', '')

class TursoRow(dict):
    """Dict that also supports attribute access like sqlite3.Row"""
    def __getattr__(self, key):
        try: return self[key]
        except KeyError: raise AttributeError(key)
    def keys(self):
        return super().keys()

class TursoCursor:
    def __init__(self, results):
        self._rows = results
        self._pos = 0
        self.description = None
        if results and isinstance(results[0], dict):
            self.description = [(k,) for k in results[0].keys()]

    def fetchone(self):
        if self._pos < len(self._rows):
            row = self._rows[self._pos]
            self._pos += 1
            return TursoRow(row)
        return None

    def fetchall(self):
        rows = self._rows[self._pos:]
        self._pos = len(self._rows)
        return [TursoRow(r) for r in rows]

    def __iter__(self):
        return iter([TursoRow(r) for r in self._rows])

class TursoConnection:
    def __init__(self, url, token):
        self.url = url.replace('libsql://', 'https://') + '/v2/pipeline'
        self.token = token
        self._pending = []  # batch of statements to send

    def _send(self, stmts):
        """Send statements via HTTP pipeline"""
        requests_payload = [{'type': 'execute', 'stmt': s} for s in stmts]
        requests_payload.append({'type': 'close'})
        resp = requests.post(self.url,
            headers={'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'},
            json={'requests': requests_payload},
            timeout=30)
        resp.raise_for_status()
        return resp.json()['results']

    def _build_stmt(self, sql, params=()):
        stmt = {'sql': sql}
        if params:
            args = []
            for p in params:
                if p is None:
                    args.append({'type': 'null'})
                elif isinstance(p, bool):
                    args.append({'type': 'integer', 'value': str(int(p))})
                elif isinstance(p, int):
                    args.append({'type': 'integer', 'value': str(p)})
                elif isinstance(p, float):
                    args.append({'type': 'float', 'value': str(p)})
                else:
                    args.append({'type': 'text', 'value': str(p)})
            stmt['args'] = args
        return stmt

    def execute(self, sql, params=()):
        stmt = self._build_stmt(sql, params)
        results = self._send([stmt])
        result = results[0]
        if result.get('type') == 'error':
            raise Exception(result.get('error', {}).get('message', 'Turso error'))
        rows = []
        if result.get('type') == 'ok':
            res = result.get('response', {}).get('result', {})
            cols = [c['name'] for c in res.get('cols', [])]
            for row in res.get('rows', []):
                d = {}
                for i, col in enumerate(cols):
                    cell = row[i]
                    val = cell.get('value')
                    typ = cell.get('type')
                    if typ == 'null': val = None
                    elif typ == 'integer': val = int(val)
                    elif typ == 'float': val = float(val)
                    d[col] = val
                rows.append(d)
        return TursoCursor(rows)

    def executescript(self, sql):
        """Execute multiple statements separated by semicolons"""
        stmts = [s.strip() for s in sql.split(';') if s.strip()]
        built = [self._build_stmt(s) for s in stmts]
        self._send(built)

    def commit(self):
        pass  # Turso auto-commits each execute

    def sync(self):
        pass

    def close(self):
        pass

def connect():
    if TURSO_URL and TURSO_TOKEN:
        return TursoConnection(TURSO_URL, TURSO_TOKEN)
    else:
        import sqlite3
        conn = sqlite3.connect(os.environ.get('DB_PATH', 'bombas.db'))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
