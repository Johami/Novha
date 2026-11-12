import os
from datetime import timedelta

from flask import Flask, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt
from dotenv import load_dotenv

from api import api
from auth import auth_api, auth_web

load_dotenv()

app = Flask(__name__)

# ── Configuración Flask + JWT ────────────────────────────────
app.config["SECRET_KEY"]               = os.environ.get("SECRET_KEY", "dev-flash-key")
app.config["JWT_SECRET_KEY"]           = os.environ.get("JWT_SECRET_KEY", "dev-jwt-key-cambiar")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)
app.config["JWT_TOKEN_LOCATION"]       = ["headers", "cookies"]
app.config["JWT_COOKIE_CSRF_PROTECT"]  = False   # simplificado (ver nota en el PDF)
app.config["JWT_COOKIE_SECURE"]        = False   # True cuando uses HTTPS en prod

CORS(app, supports_credentials=True)
jwt = JWTManager(app)

# ── Blueprints ───────────────────────────────────────────────
app.register_blueprint(api)         # /api/productos, /api/configuraciones, etc.
app.register_blueprint(auth_api)    # /api/registro, /api/login, /api/perfil, /api/refresh
app.register_blueprint(auth_web)    # /login, /registro, /perfil, /logout

# ── Context processor: expone `current_user` en plantillas ───
@app.context_processor
def inject_user():
    try:
        verify_jwt_in_request(locations=["cookies"], optional=True)
        claims = get_jwt()
        return {"current_user": claims if claims else None}
    except Exception:
        return {"current_user": None}

# ── Rutas existentes del catálogo ────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/catalogo")
def catalogo():
    return render_template("catalogo.html")

@app.route("/chaquetas")
def chaquetas():
    return render_template("chaquetas.html")

@app.route("/overoles")
def overoles():
    return render_template("overoles.html")

@app.route("/ruanas")
def ruanas():
    return render_template("ruanas.html")

@app.route("/bordados")
def bordados():
    return render_template("bordados.html")

@app.route("/cojines")
def cojines():
    return render_template("cojines.html")

@app.route("/polos")
def polos():
    return render_template("polos.html")

@app.route("/producto/<int:id>")
def producto(id):
    return render_template("producto.html")

@app.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)