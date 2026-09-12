from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/catalogo")
def catalogo():
    # TODO: en el futuro recibirá los productos desde la BD
    return render_template("catalogo.html")


@app.route("/producto/<slug>")
def producto(slug):
    # TODO: en el futuro buscará el producto por slug en la BD
    return render_template("producto.html", slug=slug)

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

@app.route("/prendas")
def prendas():
    return render_template("prendas.html")
    
if __name__ == "__main__":
    app.run(debug=True)