"""
pozo_plus.py — mejoras modulares para POZO/MGR

Agrega:
- /api/pozo-plus/dashboard
- /api/pozo-plus/search
- UI visible inyectada en la pantalla principal
"""

from flask import jsonify, request, session, url_for

import app as original_app


app = original_app.app


def _like(term):
    return f"%{str(term or '').strip()}%"


def _short(text, max_len=130):
    if text is None:
        return ""
    s = str(text).strip()
    if len(s) <= max_len:
        return s
    return s[:max_len - 1] + "…"


@app.route("/api/pozo-plus/dashboard", methods=["GET"])
@original_app.login_required
def pozo_plus_dashboard():
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
            "en_reparacion": scalar("""
                SELECT COUNT(*) AS n FROM reparaciones
                WHERE estado NOT IN ('Entregada','Cancelada')
            """),
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


@app.route("/api/pozo-plus/search", methods=["GET"])
@original_app.login_required
def pozo_plus_search():
    q = (request.args.get("q") or "").strip()
    limit_raw = request.args.get("limit", "10")

    try:
        limit = max(3, min(int(limit_raw), 25))
    except Exception:
        limit = 10

    if len(q) < 2:
        return jsonify({"query": q, "count": 0, "results": []})

    conn = original_app.get_db()
    results = []

    try:
        # Bombas
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
                "title": " ".join(x for x in [
                    str(r.get("marca") or ""),
                    str(r.get("modelo") or ""),
                    str(r.get("hp") or "") + "HP" if r.get("hp") else "",
                ] if x).strip(),
                "meta": " · ".join(x for x in [ubicacion, lugar, r.get("zona")] if x),
                "badge": r.get("estado_actual") or ubicacion,
                "id": r.get("id"),
            })

        # Perforaciones
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
                p.observaciones,
                b.n_equipo,
                b.marca,
                b.modelo,
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
            })

        # Reparaciones
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
            })

    finally:
        conn.close()

    results = results[: max(limit, 18)]
    return jsonify({"query": q, "count": len(results), "results": results})


@app.before_request
def pozo_plus_session_lifetime():
    session.permanent = True


@app.after_request
def pozo_plus_headers_and_assets(response):
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
                if "pozo_plus.js" not in body and "</body>" in body:
                    css = url_for("static", filename="pozo_plus.css")
                    js = url_for("static", filename="pozo_plus.js")
                    assets = f'\n<link rel="stylesheet" href="{css}">\n<script src="{js}" defer></script>\n'
                    body = body.replace("</body>", assets + "</body>")
                    response.set_data(body)
                    response.headers["Content-Length"] = str(len(response.get_data()))
            except Exception:
                pass

    return response
