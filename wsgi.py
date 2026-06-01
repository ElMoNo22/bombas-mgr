
"""
wsgi.py — arranque seguro + mejoras UI para POZO/MGR

Usar en producción con:
    gunicorn wsgi:app

Incluye:
- Arranque seguro para Render.
- Rotación automática de contraseña inicial si corresponde.
- Cookies/headers de seguridad.
- API de búsqueda global.
- API de dashboard extendido.
- Barra flotante de búsqueda global inyectada en la app sin tocar index.html.
"""

import os
import secrets
import warnings

from flask import jsonify, request, session
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash, generate_password_hash

import app as original_app


DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "bombas2024"

app = original_app.app


def _is_truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _running_on_render() -> bool:
    return bool(os.environ.get("RENDER")) or bool(os.environ.get("RENDER_SERVICE_ID"))


def configure_secret_key() -> None:
    secret_key = os.environ.get("SECRET_KEY", "").strip()

    if not secret_key:
        if _running_on_render():
            raise RuntimeError(
                "Falta SECRET_KEY en variables de entorno. "
                "En Render agregá SECRET_KEY con Generate Value."
            )
        secret_key = secrets.token_urlsafe(48)
        warnings.warn(
            "SECRET_KEY no configurada. Usando una clave temporal solo para desarrollo local.",
            RuntimeWarning,
        )

    if secret_key == "bombas-mgr-secret-2024":
        raise RuntimeError(
            "SECRET_KEY insegura detectada. Cambiala en Render por un valor secreto."
        )

    app.secret_key = secret_key


def configure_session_security() -> None:
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=_running_on_render() or _is_truthy(os.environ.get("FORCE_HTTPS_COOKIES")),
        PERMANENT_SESSION_LIFETIME=60 * 60 * 12,
        MAX_CONTENT_LENGTH=25 * 1024 * 1024,
    )
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)


def secure_admin_user() -> None:
    admin_username = os.environ.get("ADMIN_USERNAME", DEFAULT_ADMIN_USERNAME).strip() or DEFAULT_ADMIN_USERNAME
    admin_password = os.environ.get("ADMIN_PASSWORD", "").strip()

    conn = original_app.get_db()
    try:
        cur = conn.execute("SELECT * FROM users WHERE username = ?", (admin_username,))
        user = original_app.fetchone_dict(cur)

        if user:
            uses_default_password = check_password_hash(user["password_hash"], DEFAULT_ADMIN_PASSWORD)

            if uses_default_password:
                if not admin_password or admin_password == DEFAULT_ADMIN_PASSWORD:
                    if _running_on_render():
                        raise RuntimeError(
                            f"El usuario {admin_username!r} sigue usando la contraseña inicial. "
                            "Agregá ADMIN_PASSWORD en Render con una contraseña segura."
                        )
                    warnings.warn(
                        f"El usuario {admin_username!r} sigue usando la contraseña inicial.",
                        RuntimeWarning,
                    )
                    return

                conn.execute(
                    "UPDATE users SET password_hash=? WHERE id=?",
                    (generate_password_hash(admin_password), user["id"]),
                )
                original_app.db_commit(conn)
                print(f"✓ Contraseña inicial de {admin_username!r} rotada automáticamente.")

        else:
            if admin_password:
                conn.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    (admin_username, generate_password_hash(admin_password), "admin"),
                )
                original_app.db_commit(conn)
                print(f"✓ Usuario admin {admin_username!r} creado desde variables de entorno.")
    finally:
        conn.close()


def _like(term: str) -> str:
    return f"%{term.strip()}%"


def _short(text, max_len=130):
    if text is None:
        return ""
    s = str(text).strip()
    if len(s) <= max_len:
        return s
    return s[:max_len - 1] + "…"


@app.route("/api/search/global", methods=["GET"])
@original_app.login_required
def global_search():
    q = (request.args.get("q") or "").strip()
    limit_raw = request.args.get("limit", "12")

    try:
        limit = max(3, min(int(limit_raw), 25))
    except Exception:
        limit = 12

    if len(q) < 2:
        return jsonify({"query": q, "results": []})

    conn = original_app.get_db()
    results = []

    try:
        cur = conn.execute(
            """
            SELECT
                b.id,
                b.n_equipo,
                b.tag,
                b.tag_extraviado,
                b.marca,
                b.modelo,
                b.hp,
                b.serie,
                b.sap_id,
                b.ubicacion_fisica,
                a.estado AS estado_actual,
                p.calle,
                p.y_col,
                p.zona
            FROM bombas b
            LEFT JOIN asignaciones a ON a.bomba_id = b.id
                AND a.id = (
                    SELECT id FROM asignaciones
                    WHERE bomba_id = b.id
                    ORDER BY CASE WHEN estado='Montado' THEN 0 ELSE 1 END,
                    COALESCE(fecha_desmontaje, fecha_montaje) DESC,
                    id DESC LIMIT 1
                )
            LEFT JOIN perforaciones p ON a.perforacion_id = p.id
            WHERE
                b.n_equipo LIKE ?
                OR b.tag LIKE ?
                OR b.tag_extraviado LIKE ?
                OR b.marca LIKE ?
                OR b.modelo LIKE ?
                OR b.serie LIKE ?
                OR b.sap_id LIKE ?
                OR b.ubicacion_fisica LIKE ?
            ORDER BY
                CASE WHEN b.n_equipo = ? THEN 0 ELSE 1 END,
                b.marca,
                b.modelo
            LIMIT ?
            """,
            (_like(q), _like(q), _like(q), _like(q), _like(q), _like(q), _like(q), _like(q), q, limit),
        )

        for r in original_app.fetchall_dicts(cur):
            ubicacion = r.get("ubicacion_fisica") or r.get("estado_actual") or "Sin ubicación"
            lugar = ""
            if r.get("calle"):
                lugar = f"{r.get('calle')} y {r.get('y_col') or ''}".strip()

            results.append({
                "type": "bomba",
                "label": f"Bomba {r.get('n_equipo') or 's/n'}",
                "title": " ".join(x for x in [str(r.get("marca") or ""), str(r.get("modelo") or ""), str(r.get("hp") or "") + "HP" if r.get("hp") else ""] if x).strip(),
                "meta": " · ".join(x for x in [ubicacion, lugar, r.get("zona")] if x),
                "badge": r.get("estado_actual") or ubicacion,
                "id": r.get("id"),
                "data": r,
            })

        cur = conn.execute(
            """
            SELECT
                p.id,
                p.calle,
                p.entre,
                p.y_col,
                p.zona,
                p.bombeo,
                p.denominacion,
                p.prof_trabajo_mts,
                p.observaciones,
                b.n_equipo,
                b.marca,
                b.modelo,
                b.hp,
                a.estado AS estado_actual
            FROM perforaciones p
            LEFT JOIN asignaciones a ON a.perforacion_id = p.id
                AND a.id = (
                    SELECT id FROM asignaciones
                    WHERE perforacion_id = p.id
                    ORDER BY CASE WHEN estado='Montado' THEN 0 ELSE 1 END,
                    COALESCE(fecha_desmontaje, fecha_montaje) DESC,
                    id DESC LIMIT 1
                )
            LEFT JOIN bombas b ON a.bomba_id = b.id
            WHERE
                p.calle LIKE ?
                OR p.entre LIKE ?
                OR p.y_col LIKE ?
                OR p.zona LIKE ?
                OR p.bombeo LIKE ?
                OR p.denominacion LIKE ?
                OR p.observaciones LIKE ?
            ORDER BY p.zona, p.calle, p.y_col
            LIMIT ?
            """,
            (_like(q), _like(q), _like(q), _like(q), _like(q), _like(q), _like(q), limit),
        )

        for r in original_app.fetchall_dicts(cur):
            bomba = ""
            if r.get("n_equipo"):
                bomba = f"Bomba {r.get('n_equipo')} · {r.get('marca') or ''} {r.get('modelo') or ''}".strip()

            results.append({
                "type": "perforacion",
                "label": f"Perforación {r.get('calle') or ''} y {r.get('y_col') or ''}".strip(),
                "title": r.get("denominacion") or r.get("bombeo") or "Pozo / perforación",
                "meta": " · ".join(x for x in [r.get("zona"), bomba, r.get("estado_actual")] if x),
                "badge": r.get("zona") or "Perforación",
                "id": r.get("id"),
                "data": r,
            })

        cur = conn.execute(
            """
            SELECT
                id,
                fecha_envio,
                remito,
                proveedor,
                descripcion,
                servicio,
                tag_actual,
                tag_reemplazado,
                numero_equipo,
                marca,
                modelo,
                hp,
                serie,
                presupuesto,
                costo_usd,
                estado,
                fecha_entrega,
                remito_entrega,
                responsable
            FROM reparaciones
            WHERE
                numero_equipo LIKE ?
                OR remito LIKE ?
                OR proveedor LIKE ?
                OR descripcion LIKE ?
                OR servicio LIKE ?
                OR tag_actual LIKE ?
                OR tag_reemplazado LIKE ?
                OR marca LIKE ?
                OR modelo LIKE ?
                OR serie LIKE ?
                OR presupuesto LIKE ?
                OR estado LIKE ?
                OR responsable LIKE ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (_like(q), _like(q), _like(q), _like(q), _like(q), _like(q), _like(q), _like(q), _like(q), _like(q), _like(q), _like(q), _like(q), limit),
        )

        for r in original_app.fetchall_dicts(cur):
            costo = ""
            if r.get("costo_usd") not in (None, ""):
                costo = f"USD {r.get('costo_usd')}"
            results.append({
                "type": "reparacion",
                "label": f"Reparación #{r.get('id')}",
                "title": f"Equipo {r.get('numero_equipo') or 's/n'} · {r.get('proveedor') or 'Sin proveedor'}",
                "meta": " · ".join(x for x in [r.get("estado"), r.get("fecha_envio"), costo, _short(r.get("descripcion"), 70)] if x),
                "badge": r.get("estado") or "Reparación",
                "id": r.get("id"),
                "data": r,
            })

    finally:
        conn.close()

    results = results[: max(limit, 18)]
    return jsonify({"query": q, "results": results, "count": len(results)})


@app.route("/api/dashboard-plus", methods=["GET"])
@original_app.login_required
def dashboard_plus():
    conn = original_app.get_db()

    def scalar(sql, params=()):
        cur = conn.execute(sql, params)
        row = original_app.fetchone_dict(cur)
        return list(row.values())[0] if row else 0

    try:
        data = {
            "total_bombas": scalar("SELECT COUNT(*) AS n FROM bombas"),
            "total_perforaciones": scalar("SELECT COUNT(*) AS n FROM perforaciones"),
            "montadas": scalar("SELECT COUNT(*) AS n FROM asignaciones WHERE estado='Montado'"),
            "disponibles": scalar("""
                SELECT COUNT(*) AS n FROM bombas WHERE id NOT IN
                (SELECT DISTINCT bomba_id FROM asignaciones WHERE estado='Montado')
            """),
            "en_reparacion": scalar("SELECT COUNT(*) AS n FROM reparaciones WHERE estado NOT IN ('Entregada','Cancelada')"),
            "entregadas_30d": scalar("""
                SELECT COUNT(*) AS n FROM reparaciones
                WHERE estado='Entregada'
                AND fecha_entrega IS NOT NULL
                AND fecha_entrega >= date('now','-30 day')
            """),
            "reparaciones_sin_costo": scalar("""
                SELECT COUNT(*) AS n FROM reparaciones
                WHERE estado NOT IN ('Entregada','Cancelada')
                AND (costo_usd IS NULL OR costo_usd = 0)
            """),
            "costo_reparaciones_activas_usd": scalar("""
                SELECT COALESCE(SUM(costo_usd), 0) AS n
                FROM reparaciones
                WHERE estado NOT IN ('Entregada','Cancelada')
                AND costo_usd IS NOT NULL
            """),
            "perforaciones_sin_bomba": scalar("""
                SELECT COUNT(*) AS n FROM perforaciones WHERE id NOT IN
                (SELECT DISTINCT perforacion_id FROM asignaciones WHERE estado='Montado')
            """),
        }
    finally:
        conn.close()

    return jsonify(data)


def _injected_ui() -> str:
    return """
<style id="pozo-plus-style">
  .pozo-plus-search-launcher{position:fixed;right:18px;bottom:18px;z-index:9999;border:1px solid rgba(79,142,247,.45);background:#171b26;color:#e8eaf0;border-radius:999px;padding:10px 14px;font:500 13px 'IBM Plex Sans',system-ui,sans-serif;box-shadow:0 10px 30px rgba(0,0,0,.35);cursor:pointer;display:flex;gap:8px;align-items:center}
  .pozo-plus-search-launcher:hover{border-color:#4f8ef7;color:#4f8ef7}
  .pozo-plus-kbd{font:600 10px 'IBM Plex Mono',monospace;color:#8b91a8;border:1px solid #353b52;border-radius:5px;padding:2px 5px}
  .pozo-plus-modal{position:fixed;inset:0;background:rgba(0,0,0,.62);backdrop-filter:blur(4px);z-index:10000;display:none;align-items:flex-start;justify-content:center;padding:70px 14px 20px}
  .pozo-plus-modal.open{display:flex}
  .pozo-plus-box{width:min(760px,96vw);background:#171b26;border:1px solid #353b52;border-radius:14px;box-shadow:0 20px 60px rgba(0,0,0,.45);overflow:hidden}
  .pozo-plus-head{padding:14px;border-bottom:1px solid #2a2f42;display:flex;gap:10px;align-items:center}
  .pozo-plus-input{flex:1;background:#1e2332;border:1px solid #2a2f42;color:#e8eaf0;border-radius:9px;padding:12px 13px;font-size:15px;outline:none}
  .pozo-plus-input:focus{border-color:#4f8ef7}
  .pozo-plus-close{background:#1e2332;border:1px solid #2a2f42;color:#8b91a8;border-radius:8px;padding:9px 12px;cursor:pointer}
  .pozo-plus-close:hover{color:#e8eaf0;border-color:#4f8ef7}
  .pozo-plus-results{max-height:62vh;overflow:auto;padding:8px}
  .pozo-plus-empty{padding:24px;text-align:center;color:#555d78;font-size:13px}
  .pozo-plus-item{display:grid;grid-template-columns:94px 1fr auto;gap:10px;align-items:center;padding:10px;border-bottom:1px solid #242a3b;border-radius:8px;cursor:pointer}
  .pozo-plus-item:hover{background:rgba(79,142,247,.07)}
  .pozo-plus-type{font:600 10px 'IBM Plex Mono',monospace;text-transform:uppercase;color:#4f8ef7;border:1px solid rgba(79,142,247,.3);border-radius:999px;padding:4px 7px;text-align:center}
  .pozo-plus-title{font-weight:600;font-size:13px;color:#e8eaf0;margin-bottom:2px}
  .pozo-plus-meta{font-size:12px;color:#8b91a8;line-height:1.35}
  .pozo-plus-badge{font:600 10px 'IBM Plex Mono',monospace;color:#34c77b;background:rgba(52,199,123,.08);border:1px solid rgba(52,199,123,.25);padding:4px 7px;border-radius:999px;white-space:nowrap}
  .pozo-plus-dash{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:10px}
  .pozo-plus-card{background:#171b26;border:1px solid #2a2f42;border-radius:10px;padding:12px 13px}
  .pozo-plus-card .n{font:700 24px 'IBM Plex Mono',monospace;color:#e8eaf0}
  .pozo-plus-card .l{font:600 10px 'IBM Plex Mono',monospace;color:#8b91a8;text-transform:uppercase;letter-spacing:.08em;margin-top:3px}
  .pozo-plus-card.warn .n{color:#f5a623}
  .pozo-plus-card.good .n{color:#34c77b}
  @media(max-width:900px){.pozo-plus-dash{grid-template-columns:repeat(2,1fr)}.pozo-plus-item{grid-template-columns:1fr}.pozo-plus-type{width:fit-content}.pozo-plus-badge{width:fit-content}.pozo-plus-search-launcher{left:14px;right:14px;justify-content:center}}
</style>

<div class="pozo-plus-modal" id="pozoPlusModal" aria-hidden="true">
  <div class="pozo-plus-box">
    <div class="pozo-plus-head">
      <input class="pozo-plus-input" id="pozoPlusInput" placeholder="Buscar bomba, tag, serie, calle, proveedor, remito..." autocomplete="off">
      <button class="pozo-plus-close" id="pozoPlusClose">Cerrar</button>
    </div>
    <div class="pozo-plus-results" id="pozoPlusResults">
      <div class="pozo-plus-empty">Escribí al menos 2 caracteres para buscar en todo el sistema.</div>
    </div>
  </div>
</div>

<button class="pozo-plus-search-launcher" id="pozoPlusLauncher" type="button">
  🔎 Buscador global <span class="pozo-plus-kbd">Ctrl K</span>
</button>

<script id="pozo-plus-script">
(function(){
  const modal = document.getElementById('pozoPlusModal');
  const input = document.getElementById('pozoPlusInput');
  const results = document.getElementById('pozoPlusResults');
  const launcher = document.getElementById('pozoPlusLauncher');
  const closeBtn = document.getElementById('pozoPlusClose');
  let timer = null;

  function esc(s){
    return String(s ?? '').replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  }

  function openSearch(){
    modal.classList.add('open');
    modal.setAttribute('aria-hidden','false');
    setTimeout(()=>input.focus(), 30);
  }

  function closeSearch(){
    modal.classList.remove('open');
    modal.setAttribute('aria-hidden','true');
  }

  async function doSearch(){
    const q = input.value.trim();
    if(q.length < 2){
      results.innerHTML = '<div class="pozo-plus-empty">Escribí al menos 2 caracteres para buscar en todo el sistema.</div>';
      return;
    }
    results.innerHTML = '<div class="pozo-plus-empty">Buscando...</div>';
    try{
      const res = await fetch('/api/search/global?q=' + encodeURIComponent(q) + '&limit=10');
      const data = await res.json();
      const arr = data.results || [];
      if(!arr.length){
        results.innerHTML = '<div class="pozo-plus-empty">No encontré resultados para <b>' + esc(q) + '</b>.</div>';
        return;
      }
      results.innerHTML = arr.map(item => `
        <div class="pozo-plus-item" data-type="${esc(item.type)}" data-id="${esc(item.id)}">
          <div class="pozo-plus-type">${esc(item.type)}</div>
          <div>
            <div class="pozo-plus-title">${esc(item.label)} ${item.title ? '— ' + esc(item.title) : ''}</div>
            <div class="pozo-plus-meta">${esc(item.meta || '')}</div>
          </div>
          <div class="pozo-plus-badge">${esc(item.badge || '')}</div>
        </div>
      `).join('');
    }catch(e){
      results.innerHTML = '<div class="pozo-plus-empty">Error buscando. Revisá sesión o conexión.</div>';
    }
  }

  function debounceSearch(){
    clearTimeout(timer);
    timer = setTimeout(doSearch, 220);
  }

  launcher.addEventListener('click', openSearch);
  closeBtn.addEventListener('click', closeSearch);
  input.addEventListener('input', debounceSearch);

  modal.addEventListener('click', (ev)=>{
    if(ev.target === modal) closeSearch();
  });

  document.addEventListener('keydown', (ev)=>{
    if((ev.ctrlKey || ev.metaKey) && ev.key.toLowerCase() === 'k'){
      ev.preventDefault();
      openSearch();
    }
    if(ev.key === 'Escape' && modal.classList.contains('open')){
      closeSearch();
    }
  });

  results.addEventListener('click', (ev)=>{
    const item = ev.target.closest('.pozo-plus-item');
    if(!item) return;
    const type = item.dataset.type;
    closeSearch();

    const map = {
      bomba: 'inventario',
      perforacion: 'perforaciones',
      reparacion: 'reparaciones'
    };
    const panel = map[type];

    if(panel && typeof window.showPanel === 'function'){
      window.showPanel(panel);
    }
  });

  async function injectDashboard(){
    try{
      const container = document.querySelector('#dashboard') || document.querySelector('.panel.active') || document.querySelector('.main');
      if(!container || document.getElementById('pozoPlusDash')) return;

      const res = await fetch('/api/dashboard-plus');
      const d = await res.json();
      const money = Number(d.costo_reparaciones_activas_usd || 0).toLocaleString('es-AR', {maximumFractionDigits:0});

      const wrap = document.createElement('div');
      wrap.id = 'pozoPlusDash';
      wrap.className = 'pozo-plus-dash';
      wrap.innerHTML = `
        <div class="pozo-plus-card"><div class="n">${esc(d.total_bombas)}</div><div class="l">Bombas total</div></div>
        <div class="pozo-plus-card good"><div class="n">${esc(d.montadas)}</div><div class="l">Montadas</div></div>
        <div class="pozo-plus-card"><div class="n">${esc(d.disponibles)}</div><div class="l">Disponibles</div></div>
        <div class="pozo-plus-card warn"><div class="n">${esc(d.en_reparacion)}</div><div class="l">En reparación</div></div>
        <div class="pozo-plus-card"><div class="n">USD ${esc(money)}</div><div class="l">Costo rep. activas</div></div>
      `;

      const firstCard = container.querySelector('.card');
      if(firstCard) container.insertBefore(wrap, firstCard);
      else container.prepend(wrap);
    }catch(e){}
  }

  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', injectDashboard);
  }else{
    injectDashboard();
  }
})();
</script>
"""


@app.before_request
def make_session_permanent():
    session.permanent = True


@app.after_request
def add_security_headers_and_ui(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")

    if response.content_type and "text/html" in response.content_type:
        response.headers.setdefault("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        response.headers.setdefault("Pragma", "no-cache")

        if request.path == "/" and "user_id" in session:
            try:
                body = response.get_data(as_text=True)
                if "pozo-plus-script" not in body and "</body>" in body:
                    body = body.replace("</body>", _injected_ui() + "\n</body>")
                    response.set_data(body)
                    response.headers["Content-Length"] = str(len(response.get_data()))
            except Exception:
                pass

    return response


configure_secret_key()
configure_session_security()
secure_admin_user()
