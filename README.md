# 🛍️ Novha - Catálogo con Persistencia Políglota

**Catálogo web interactivo para un negocio de ropa y personalización en
Corabastos, Bogotá.**

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=flat-square&logo=sqlite&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=flat-square&logo=mongodb&logoColor=white)

------------------------------------------------------------------------

## 📖 Descripción del Proyecto

**Novha** es un negocio de confección y personalización de prendas de
trabajo. Esta aplicación implementa una arquitectura de **Persistencia
Políglota**, combinando lo mejor de dos mundos para gestionar el
catálogo:

-   🗄️ **SQLite:** Datos estructurados del catálogo (productos).
-   🍃 **MongoDB Atlas:** Características variables por producto
    (tallas, colores, materiales, forros).
-   ⚡ **Flask:** API REST que combina ambas bases de datos en tiempo
    real.

------------------------------------------------------------------------

## 🏗️ Arquitectura

``` text
+-----------------------------+
|    Frontend (Vue/Bootstrap) |
+--------------+--------------+
               | HTTP/JSON
               v
+-----------------------------+
|         Flask API           |
|           /api/*            |
+--------------+--------------+
               |
        +------+-------+
        |              |
        v              v
+-------------+   +-------------------+
|   SQLite    |   |      MongoDB      |
|  productos  |   |  configuraciones |
|  usuarios   |   | (caract. variables)|
+-------------+   +-------------------+
```

### ¿Por qué dos bases de datos?

-   Los **productos** tienen campos comunes (nombre, categoría, precio)
    que se adaptan perfectamente a SQL.
-   Sus **características son variables**: una chaqueta tiene talla,
    color y tipo de cremallera; un cojín tiene tamaño y tipo de bordado;
    un overol tiene forro y tipo. En SQL esto requeriría columnas que
    quedarían nulas (`NULL`) para la mayoría de productos. En MongoDB
    cada documento guarda **solo lo que aplica**.

------------------------------------------------------------------------

## 🚀 Instalación y Ejecución

### Requisitos previos

-   Python 3.10+
-   Cuenta en MongoDB Atlas (gratuita)

### Pasos

1.  Clonar el repositorio:

    ``` bash
    git clone https://github.com/Johami/Novha.git
    cd Novha
    ```

2.  Crear y activar entorno virtual:

    ``` bash
    python -m venv .venv
    ```

    **Windows (PowerShell):**

    ``` powershell
    .venv\Scripts\Activate.ps1
    ```

    **Linux/macOS:**

    ``` bash
    source .venv/bin/activate
    ```

3.  Instalar dependencias:

    ``` bash
    pip install -r requirements.txt
    ```

4.  Configurar variables de entorno. Crea un archivo `.env` en la raíz
    del proyecto con:

    ``` env
    MONGO_URI=mongodb+srv://usuario:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
    MONGO_DB=novha_db
    ```

    Reemplaza los valores de ejemplo por las credenciales de tu propio
    clúster de MongoDB Atlas.

5.  Crear la base de datos SQLite con los datos iniciales:

    ``` bash
    python init_db.py
    ```

6.  Iniciar el servidor:

    ``` bash
    python app.py
    ```

    El servidor estará disponible en `http://localhost:5000`.

> **Opcional:** Para poblar MongoDB con configuraciones de ejemplo,
> ejecuta `python seed_mongo.py` desde otra terminal, con el entorno
> virtual activado.

------------------------------------------------------------------------

## 📡 Endpoints de la API

  --------------------------------------------------------------------------------------------------
  Método                Endpoint                                  Base de datos     Descripción
  --------------------- -------------------------------------- -------------------- ----------------
  `GET`                 `/api/`                                        ---          Índice de la API
                                                                                    con lista de
                                                                                    endpoints

  **Productos**                                                                     

  `GET`                 `/api/productos`                              SQLite        Listar productos
                                                                                    activos

  `GET`                 `/api/productos?categoria=Chaquetas`          SQLite        Filtrar por
                                                                                    categoría

  `GET`                 `/api/productos/<id>`                         SQLite        Ver un producto

  `POST`                `/api/productos`                              SQLite        Crear producto

  `PUT`                 `/api/productos/<id>`                         SQLite        Actualizar
                                                                                    producto

  `DELETE`              `/api/productos/<id>`                         SQLite        Desactivar
                                                                                    producto (soft
                                                                                    delete)

  **Configuraciones**                                                               

  `GET`                 `/api/configuraciones/<producto_id>`         MongoDB        Ver
                                                                                    configuración

  `POST`                `/api/configuraciones`                       MongoDB        Crear
                                                                                    configuración
                                                                                    (valida producto
                                                                                    en SQL)

  `PUT`                 `/api/configuraciones/<producto_id>`         MongoDB        Actualizar
                                                                                    configuración

  `DELETE`              `/api/configuraciones/<producto_id>`         MongoDB        Eliminar
                                                                                    configuración

  **Combinado**                                                                     

  `GET`                 `/api/productos/<id>/detalle`            **SQL + NoSQL**    Producto y
                                                                                    configuración en
                                                                                    una sola
                                                                                    respuesta
  --------------------------------------------------------------------------------------------------

------------------------------------------------------------------------

## 📊 Estructura de Datos

### SQLite: Tabla `productos`

  -----------------------------------------------------------------------
  Campo                   Tipo                    Descripción
  ----------------------- ----------------------- -----------------------
  `id`                    INTEGER PK              Identificador único

  `nombre`                TEXT                    Nombre del producto

  `categoria`             TEXT                    Categoría (Chaquetas,
                                                  Overoles, etc.)

  `descripcion`           TEXT                    Descripción general

  `precio_referencia`     REAL                    Precio orientativo
                                                  (`NULL` = "Consultar")

  `imagen_principal`      TEXT                    Ruta de la imagen

  `activo`                INTEGER                 `1` = activo, `0` =
                                                  desactivado

  `creado_en`             TEXT                    Fecha de creación
  -----------------------------------------------------------------------

### SQLite: Tabla `usuarios` (preparada para JWT futuro)

  Campo             Tipo          Descripción
  ----------------- ------------- -------------------------
  `id`              INTEGER PK    Identificador único
  `email`           TEXT UNIQUE   Correo del usuario
  `password_hash`   TEXT          Contraseña hasheada
  `rol`             TEXT          `"cliente"` o `"admin"`

### MongoDB: Colección `configuraciones`

Cada documento tiene `_id = producto_id` de SQLite y estructura
variable. Ejemplo para el producto 1 (Chaqueta clásica):

``` json
{
  "_id": 1,
  "caracteristicas": {
    "talla": ["S", "M", "L", "XL"],
    "color_tela": ["Negro", "Azul", "Beige"],
    "material": ["Nautica"],
    "tipo_cremallera": ["Metalica", "Plastica"]
  },
  "especificaciones": "Consulta colores disponibles"
}
```

> El overol (`id=4`) tiene `forro` y `tipo` que la chaqueta no tiene. El
> cojín (`id=6`) tiene `tamano_bordado`. Eso justifica MongoDB: **cada
> producto guarda solo sus características aplicables**.

------------------------------------------------------------------------

## 📸 Evidencias de Ejecución

Las capturas de pantalla del funcionamiento están ubicadas en la carpeta
`/docs`:

1.  `01-api-index.png` - Índice de la API
2.  `02-productos-sql.png` - 7 productos desde SQLite
3.  `03-detalle-sin-config.png` - Producto sin configuración
    (`configuracion: null`)
4.  `04-detalle-con-config.png` - Producto y configuración combinados
    (SQL + NoSQL)
5.  `05-atlas-coleccion.png` - Colección configuraciones en MongoDB
    Atlas
6.  `06-sqlite-tabla.png` - Tabla productos en SQLite (DB Browser)

------------------------------------------------------------------------

## 📂 Estructura del Proyecto

``` text
Novha/
├── app.py              # Punto de entrada Flask + rutas HTML y API
├── api.py              # Blueprint con los endpoints de la API REST
├── db.py               # Conexiones a SQLite y MongoDB
├── init_db.py          # Crea la base SQLite con 7 productos iniciales
├── seed_mongo.py       # Puebla MongoDB con configuraciones de ejemplo
├── auth.py             # (Reservado para autenticación JWT)
├── requirements.txt    # Dependencias
├── .env.example        # Plantilla de variables de entorno
├── static/             # CSS, JS e imágenes
├── templates/          # Plantillas HTML (Jinja2)
└── docs/               # Capturas de evidencias
```

------------------------------------------------------------------------

## 🔒 Seguridad

-   El archivo `.env` con credenciales reales **no se sube a GitHub**
    (debe estar incluido en `.gitignore`).
-   Solo se sube `.env.example` con valores ficticios.
-   La base SQLite `novha.db` tampoco se sube; se regenera con
    `init_db.py`.

------------------------------------------------------------------------

## 👥 Autores

-   **Johami Silva** 
-   **Julian Suarez** 

------------------------------------------------------------------------

## 📚 Referencias

-   [Flask Documentation](https://flask.palletsprojects.com/)
-   [PyMongo Documentation](https://pymongo.readthedocs.io/)
-   [MongoDB Atlas](https://www.mongodb.com/atlas/database)
-   [SQLite Documentation](https://www.sqlite.org/docs.html)
