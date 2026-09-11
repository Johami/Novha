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


if __name__ == "__main__":
    app.run(debug=True)