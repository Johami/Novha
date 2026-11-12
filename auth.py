"""
auth.py — Autenticación JWT para Novha
=======================================
Expone dos blueprints:

  auth_api  (prefijo /api)
      POST /api/registro   → Crea usuario (hashea password con werkzeug)
      POST /api/login      → Devuelve JWT (Bearer) en JSON
      GET  /api/perfil     → Ruta protegida con Bearer (retorna datos del usuario)
      POST /api/refresh    → Renueva el token si aún es válido

  auth_web  (sin prefijo)
      GET/POST /registro   → Formulario HTML de registro
      GET/POST /login      → Formulario HTML de login (guarda JWT en cookie)
      GET      /perfil     → Página protegida por cookie HTTP-only
      GET      /logout     → Elimina la cookie JWT
"""

from functools import wraps

from flask import (
    Blueprint, jsonify, request, render_template,
    redirect, url_for, flash, make_response,
)
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity, get_jwt,
    set_access_cookies, unset_jwt_cookies, verify_jwt_in_request,
)
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError

from db import get_sql

# ─────────────────────────────────────────────────────────────
# Blueprints
# ─────────────────────────────────────────────────────────────
auth_api = Blueprint("auth_api", __name__, url_prefix="/api")
auth_web = Blueprint("auth_web", __name__)


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
def email_valido(email: str) -> bool:
    try:
        validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False


def _claims_de(user: dict) -> dict:
    """Claims que viajan dentro del JWT (NO incluir contraseña)."""
    return {
        "email":  user["email"],
        "nombre": user["nombre"] or "",
        "rol":    user["rol"],
    }


def _crear_token(user: dict) -> str:
    return create_access_token(
        identity=str(user["id"]),
        additional_claims=_claims_de(user),
    )


def login_required_html(f):
    """
    Decorador para rutas HTML: si no hay JWT válido en cookie,
    redirige a /login (en lugar de devolver 401 JSON).
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request(locations=["cookies"])
        except Exception:
            flash("Debes iniciar sesión para acceder a esa página.", "warning")
            return redirect(url_for("auth_web.login"))
        return f(*args, **kwargs)
    return wrapper


# ═════════════════════════════════════════════════════════════
# ENDPOINTS JSON — API (Bearer)
# ═════════════════════════════════════════════════════════════

@auth_api.post("/registro")
def api_registro():
    """
    Body JSON:
        { "nombre": "...", "email": "...", "password": "..." }

    201 → usuario creado (sin contraseña)
    400 → datos inválidos
    409 → email ya registrado
    """
    data = request.get_json(silent=True) or {}
    nombre   = (data.get("nombre") or "").strip()
    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    # Validaciones
    if not all([nombre, email, password]):
        return jsonify({"error": "nombre, email y password son obligatorios"}), 400

    if not email_valido(email):
        return jsonify({"error": "El email no es válido"}), 400

    if len(password) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400

    conn = get_sql()
    try:
        if conn.execute("SELECT id FROM usuarios WHERE email = ?", (email,)).fetchone():
            return jsonify({"error": "Ya existe un usuario con ese email"}), 409

        cur = conn.execute(
            """INSERT INTO usuarios (email, password_hash, nombre, rol, activo)
               VALUES (?, ?, ?, 'cliente', 1)""",
            (email, generate_password_hash(password), nombre),
        )
        conn.commit()
        user_id = cur.lastrowid
    finally:
        conn.close()

    return jsonify({
        "mensaje": "Usuario registrado correctamente",
        "usuario": {"id": user_id, "email": email, "nombre": nombre, "rol": "cliente"},
    }), 201


@auth_api.post("/login")
def api_login():
    """
    Body JSON:
        { "email": "...", "password": "..." }

    200 → { token, tipo, expira_en, usuario }
    401 → credenciales inválidas
    403 → usuario inactivo
    """
    data = request.get_json(silent=True) or {}
    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "email y password son obligatorios"}), 400

    conn = get_sql()
    try:
        user = conn.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
    finally:
        conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Credenciales inválidas"}), 401

    if user["activo"] != 1:
        return jsonify({"error": "Usuario inactivo, contacta al administrador"}), 403

    token = _crear_token(user)
    return jsonify({
        "token":     token,
        "tipo":      "Bearer",
        "expira_en": "2h",
        "usuario": {
            "id": user["id"], "email": user["email"],
            "nombre": user["nombre"], "rol": user["rol"],
        },
    }), 200


@auth_api.get("/perfil")
@jwt_required()                       # ← busca el token en header Authorization
def api_perfil():
    """
    Ruta protegida de prueba (ejemplo del enunciado).

    Header requerido:
        Authorization: Bearer <token>
    """
    user_id = get_jwt_identity()      # "1", "2", ...
    claims  = get_jwt()

    conn = get_sql()
    try:
        user = conn.execute(
            """SELECT id, email, nombre, rol, activo, creado_en
               FROM usuarios WHERE id = ?""",
            (user_id,),
        ).fetchone()
    finally:
        conn.close()

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({**dict(user), "claims_jwt": claims}), 200


@auth_api.post("/refresh")
@jwt_required()
def api_refresh():
    """Renueva el token si el actual aún es válido."""
    user_id = get_jwt_identity()
    claims  = get_jwt()

    conn = get_sql()
    try:
        user = conn.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,)).fetchone()
    finally:
        conn.close()

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    nuevo = _crear_token(user)
    return jsonify({"token": nuevo, "tipo": "Bearer", "expira_en": "2h"}), 200


# ═════════════════════════════════════════════════════════════
# RUTAS HTML — formularios + cookie
# ═════════════════════════════════════════════════════════════

@auth_web.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre   = request.form.get("nombre", "").strip()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm", "")

        if not all([nombre, email, password, confirm]):
            flash("Todos los campos son obligatorios.", "danger")
            return render_template("registro.html")
        if not email_valido(email):
            flash("El email no es válido.", "danger")
            return render_template("registro.html")
        if len(password) < 6:
            flash("La contraseña debe tener al menos 6 caracteres.", "danger")
            return render_template("registro.html")
        if password != confirm:
            flash("Las contraseñas no coinciden.", "danger")
            return render_template("registro.html")

        conn = get_sql()
        try:
            if conn.execute("SELECT id FROM usuarios WHERE email = ?", (email,)).fetchone():
                flash("Ya existe una cuenta con ese correo.", "danger")
                return render_template("registro.html")
            conn.execute(
                """INSERT INTO usuarios (email, password_hash, nombre, rol, activo)
                   VALUES (?, ?, ?, 'cliente', 1)""",
                (email, generate_password_hash(password), nombre),
            )
            conn.commit()
        finally:
            conn.close()

        flash("Cuenta creada correctamente. Ya puedes iniciar sesión.", "success")
        return redirect(url_for("auth_web.login"))

    return render_template("registro.html")


@auth_web.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_sql()
        try:
            user = conn.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
        finally:
            conn.close()

        if not user or not check_password_hash(user["password_hash"], password):
            flash("Correo o contraseña incorrectos.", "danger")
            return render_template("login.html")

        if user["activo"] != 1:
            flash("Tu cuenta está inactiva.", "danger")
            return render_template("login.html")

        token = _crear_token(user)
        response = make_response(redirect(url_for("auth_web.perfil")))
        set_access_cookies(response, token)     # cookie HTTP-only
        return response

    return render_template("login.html")


@auth_web.route("/perfil")
@login_required_html
def perfil():
    user_id = get_jwt_identity()

    conn = get_sql()
    try:
        user = conn.execute(
            """SELECT id, email, nombre, rol, creado_en
               FROM usuarios WHERE id = ?""",
            (user_id,),
        ).fetchone()
    finally:
        conn.close()

    return render_template("perfil.html", usuario=dict(user) if user else {})


@auth_web.route("/logout")
def logout():
    response = make_response(redirect(url_for("index")))
    unset_jwt_cookies(response)
    flash("Sesión cerrada correctamente.", "info")
    return response