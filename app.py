from flask import Flask, render_template
from flask_cors import CORS
from api import api

app = Flask(__name__)
CORS(app)
app.register_blueprint(api)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/catalogo")
def catalogo():
    return render_template("catalogo.html")


# ⚠️ Ruta eliminada temporalmente: producto.html no existe todavía
# @app.route("/producto/<slug>")
# def producto(slug):
#     return render_template("producto.html", slug=slug)


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


if __name__ == "__main__":
    app.run(debug=True)