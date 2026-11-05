from flask import Blueprint, jsonify, request
from db import get_sql, get_mongo

api = Blueprint("api", __name__, url_prefix="/api")

# ═══════════════════ PRODUCTOS (SQL) ═══════════════════

@api.get("/productos")
def listar_productos():
    conn = get_sql()
    categoria = request.args.get("categoria")
    if categoria:
        rows = conn.execute(
            "SELECT * FROM productos WHERE activo = 1 AND categoria = ?", (categoria,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM productos WHERE activo = 1").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@api.get("/productos/<int:id>")
def obtener_producto(id):
    conn = get_sql()
    row = conn.execute("SELECT * FROM productos WHERE id = ?", (id,)).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Producto no encontrado"}), 404
    return jsonify(dict(row))

@api.post("/productos")
def crear_producto():
    data = request.get_json() or {}
    if not data.get("nombre") or not data.get("categoria"):
        return jsonify({"error": "nombre y categoria son obligatorios"}), 400
    conn = get_sql()
    cur = conn.execute(
        "INSERT INTO productos (nombre, categoria, descripcion, precio_referencia, imagen_principal) VALUES (?, ?, ?, ?, ?)",
        (data["nombre"], data["categoria"], data.get("descripcion", ""),
         data.get("precio_referencia"), data.get("imagen_principal", "")),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM productos WHERE id = ?", (cur.lastrowid,)).fetchone()
    conn.close()
    return jsonify(dict(row)), 201

@api.put("/productos/<int:id>")
def actualizar_producto(id):
    data = request.get_json() or {}
    conn = get_sql()
    row = conn.execute("SELECT * FROM productos WHERE id = ?", (id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Producto no encontrado"}), 404
    conn.execute(
        "UPDATE productos SET nombre=?, categoria=?, descripcion=?, precio_referencia=?, imagen_principal=? WHERE id=?",
        (data.get("nombre", row["nombre"]), data.get("categoria", row["categoria"]),
         data.get("descripcion", row["descripcion"]),
         data.get("precio_referencia", row["precio_referencia"]),
         data.get("imagen_principal", row["imagen_principal"]), id),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM productos WHERE id = ?", (id,)).fetchone()
    conn.close()
    return jsonify(dict(row))

@api.delete("/productos/<int:id>")
def desactivar_producto(id):
    conn = get_sql()
    cur = conn.execute("UPDATE productos SET activo = 0 WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        return jsonify({"error": "Producto no encontrado"}), 404
    return jsonify({"mensaje": "Producto desactivado"})

# ═══════════════════ CONFIGURACIONES (Mongo) ═══════════════════

@api.get("/configuraciones/<int:producto_id>")
def obtener_config(producto_id):
    doc = get_mongo().configuraciones.find_one({"_id": producto_id})
    if not doc:
        return jsonify({"error": "Configuración no encontrada"}), 404
    doc["_id"] = str(doc["_id"])
    return jsonify(doc)

@api.post("/configuraciones")
def crear_config():
    data = request.get_json() or {}
    pid = data.get("producto_id")
    if not pid:
        return jsonify({"error": "producto_id es obligatorio"}), 400
    conn = get_sql()
    row = conn.execute("SELECT id FROM productos WHERE id = ?", (pid,)).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "El producto no existe en SQL"}), 404
    if get_mongo().configuraciones.find_one({"_id": pid}):
        return jsonify({"error": "Ya existe configuración para este producto"}), 409
    doc = {
        "_id": pid,
        "caracteristicas": data.get("caracteristicas", {}),
        "especificaciones": data.get("especificaciones", ""),
    }
    get_mongo().configuraciones.insert_one(doc)
    doc["_id"] = str(doc["_id"])
    return jsonify(doc), 201

@api.put("/configuraciones/<int:producto_id>")
def actualizar_config(producto_id):
    data = request.get_json() or {}
    result = get_mongo().configuraciones.update_one(
        {"_id": producto_id},
        {"$set": {
            "caracteristicas": data.get("caracteristicas", {}),
            "especificaciones": data.get("especificaciones", ""),
        }},
    )
    if result.matched_count == 0:
        return jsonify({"error": "Configuración no encontrada"}), 404
    return jsonify({"mensaje": "Configuración actualizada"})

@api.delete("/configuraciones/<int:producto_id>")
def eliminar_config(producto_id):
    result = get_mongo().configuraciones.delete_one({"_id": producto_id})
    if result.deleted_count == 0:
        return jsonify({"error": "Configuración no encontrada"}), 404
    return jsonify({"mensaje": "Configuración eliminada"})

# ═══════════════════ ⭐ COMBINADO SQL + NoSQL ═══════════════════

@api.get("/productos/<int:id>/detalle")
def detalle_combinado(id):
    conn = get_sql()
    row = conn.execute("SELECT * FROM productos WHERE id = ? AND activo = 1", (id,)).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Producto no encontrado"}), 404

    try:
        config = get_mongo().configuraciones.find_one({"_id": id})
        if config:
            config["_id"] = str(config["_id"])
    except Exception:
        config = None

    return jsonify({"producto": dict(row), "configuracion": config})

# ═══════════════════ AUTH (Entrega JWT — mañana) ═══════════════════

# TODO Entrega JWT: descomentar y mover a auth.py
#
# @api.post("/auth/register")
# def register():
#     ...hash password con werkzeug.security...
#
# @api.post("/auth/login")
# def login():
#     ...verificar hash + generar JWT...

# ═══════════════════ ÍNDICE DE LA API ═══════════════════

@api.get("/")
def api_index():
    return jsonify({
        "servicio": "Novha API",
        "version": "1.0",
        "entrega": "2 - Persistencia Políglota",
        "endpoints": [
            "GET    /api/productos",
            "GET    /api/productos/<id>",
            "POST   /api/productos",
            "PUT    /api/productos/<id>",
            "DELETE /api/productos/<id>",
            "GET    /api/configuraciones/<producto_id>",
            "POST   /api/configuraciones",
            "PUT    /api/configuraciones/<producto_id>",
            "DELETE /api/configuraciones/<producto_id>",
            "GET    /api/productos/<id>/detalle  ⭐ SQL + NoSQL",
        ],
    })