# \# Novha - Catálogo con Persistencia Políglota

# 

# Catálogo web interactivo para un negocio de ropa y personalización en Corabastos, Bogotá.

# 

# \## Descripción

# 

# Novha es un negocio de confección y personalización de prendas de trabajo. Esta aplicación implementa una arquitectura de persistencia políglota usando:

# 

# \- SQLite: datos estructurados del catálogo (productos).

# \- MongoDB Atlas: características variables por producto (tallas, colores, materiales, forros).

# \- Flask: API REST que combina ambas bases de datos.

# 

# \## Tecnologías

# 

# | Componente | Tecnología |

# |---|---|

# | Backend | Python 3.12 + Flask 3.1 |

# | Base de datos SQL | SQLite (vía `sqlite3` estándar) |

# | Base de datos NoSQL | MongoDB Atlas (vía `pymongo`) |

# | Frontend | HTML5 + CSS3 + Bootstrap 5 + Jinja2 |

# | CORS | Flask-CORS |

# | Variables de entorno | python-dotenv |

# 

# \## Arquitectura

# 

# ```text

# +-----------------------------+

# |    Frontend (Vue/Bootstrap) |

# +--------------+--------------+

# &#x20;              | HTTP/JSON

# &#x20;              v

# +-----------------------------+

# |         Flask API           |

# |           /api/\*            |

# +--------------+--------------+

# &#x20;              |

# &#x20;       +------+-------+

# &#x20;       |              |

# &#x20;       v              v

# +-------------+   +-------------------+

# |   SQLite    |   |      MongoDB      |

# |  productos  |   |  configuraciones  |

# |  usuarios   |   | (caract. variables)|

# +-------------+   +-------------------+

# ```

# 

# Por qué dos bases de datos:

# \- Los productos tienen campos comunes (nombre, categoría, precio) que se adaptan perfectamente a SQL.

# \- Sus características son variables: una chaqueta tiene talla, color y tipo de cremallera; un cojín tiene tamaño y tipo de bordado; un overol tiene forro y tipo. En SQL esto requeriría columnas que quedarían nulas para la mayoría de productos. En MongoDB cada documento guarda solo lo que aplica.

# 

# \## Instalación y ejecución

# 

# \### Requisitos previos

# \- Python 3.10+

# \- Cuenta en MongoDB Atlas (gratuita)

# 

# \### Pasos

# 

# ```bash

# \# 1. Clonar el repositorio

# git clone https://github.com/Johami/Novha.git

# cd Novha

# 

# \# 2. Crear y activar entorno virtual

# python -m venv .venv

# \# Windows:

# .venv\\Scripts\\Activate.ps1

# \# Linux/Mac:

# source .venv/bin/activate

# 

# \# 3. Instalar dependencias

# pip install -r requirements.txt

# 

# \# 4. Configurar variables de entorno

# \# Crear un archivo .env en la raíz con:

# MONGO\_URI=mongodb+srv://usuario:password@cluster0.xxxxx.mongodb.net/?retryWrites=true\&w=majority

# MONGO\_DB=novha\_db

# 

# \# 5. Crear base de datos SQLite con datos iniciales

# python init\_db.py

# 

# \# 6. Arrancar el servidor

# python app.py

# ```

# 

# El servidor estará disponible en `http://localhost:5000`.

# 

# Para poblar MongoDB con configuraciones de ejemplo (opcional, en otra terminal):

# ```bash

# python seed\_mongo.py

# ```

# 

# \## Endpoints de la API

# 

# | Método | Endpoint | Base de datos | Descripción |

# |---|---|---|---|

# | GET | `/api/` | - | Índice de la API con lista de endpoints |

# | \*\*PRODUCTOS (SQLite)\*\* | | | |

# | GET | `/api/productos` | SQLite | Listar productos activos |

# | GET | `/api/productos?categoria=Chaquetas` | SQLite | Filtrar por categoría |

# | GET | `/api/productos/<id>` | SQLite | Ver un producto |

# | POST | `/api/productos` | SQLite | Crear producto |

# | PUT | `/api/productos/<id>` | SQLite | Actualizar producto |

# | DELETE | `/api/productos/<id>` | SQLite | Desactivar producto (soft delete) |

# | \*\*CONFIGURACIONES (MongoDB)\*\* | | | |

# | GET | `/api/configuraciones/<producto\_id>` | MongoDB | Ver configuración |

# | POST | `/api/configuraciones` | MongoDB | Crear configuración (valida producto en SQL) |

# | PUT | `/api/configuraciones/<producto\_id>` | MongoDB | Actualizar configuración |

# | DELETE | `/api/configuraciones/<producto\_id>` | MongoDB | Eliminar configuración |

# | \*\*COMBINADO\*\* | | | |

# | GET | `/api/productos/<id>/detalle` | SQL + Mongo | Producto (SQLite) + configuración (MongoDB) en una sola respuesta |

# 

# \## Estructura de datos

# 

# \### SQLite: tabla `productos`

# 

# | Campo | Tipo | Descripción |

# |---|---|---|

# | id | INTEGER PK | Identificador único |

# | nombre | TEXT | Nombre del producto |

# | categoria | TEXT | Categoría (Chaquetas, Overoles, etc.) |

# | descripcion | TEXT | Descripción general |

# | precio\_referencia | REAL | Precio orientativo (NULL = "Consultar") |

# | imagen\_principal | TEXT | Ruta de la imagen |

# | activo | INTEGER | 1 = activo, 0 = desactivado |

# | creado\_en | TEXT | Fecha de creación |

# 

# \### SQLite: tabla `usuarios` (preparada para autenticación futura)

# 

# | Campo | Tipo | Descripción |

# |---|---|---|

# | id | INTEGER PK | Identificador único |

# | email | TEXT UNIQUE | Correo del usuario |

# | password\_hash | TEXT | Contraseña hasheada |

# | nombre | TEXT | Nombre del usuario |

# | rol | TEXT | "cliente" o "admin" |

# | activo | INTEGER | 1 = activo |

# | creado\_en | TEXT | Fecha de creación |

# 

# \### MongoDB: colección `configuraciones`

# 

# Cada documento tiene `\_id = producto\_id` de SQLite y estructura variable. Ejemplo para el producto 1 (Chaqueta clásica):

# 

# ```json

# {

# &#x20; "\_id": 1,

# &#x20; "caracteristicas": {

# &#x20;   "talla": \["S", "M", "L", "XL"],

# &#x20;   "color\_tela": \["Negro", "Azul", "Beige"],

# &#x20;   "material": \["Nautica"],

# &#x20;   "tipo\_cremallera": \["Metalica", "Plastica"]

# &#x20; },

# &#x20; "especificaciones": "Consulta colores disponibles"

# }

# ```

# 

# El overol (id=4) tiene forro y tipo que la chaqueta no tiene. El cojín (id=6) tiene tamano\_bordado que ninguno de los otros tiene. Eso es exactamente lo que justifica MongoDB: cada producto guarda solo sus características aplicables.

# 

# \## Evidencias de ejecución

# 

# Las capturas están en la carpeta `/docs`:

# 

# 1\. `01-api-index.png` - Índice de la API

# 2\. `02-productos-sql.png` - 7 productos desde SQLite

# 3\. `03-detalle-sin-config.png` - Producto sin configuración (configuracion: null)

# 4\. `04-detalle-con-config.png` - Producto + configuración combinados (SQL + NoSQL)

# 5\. `05-atlas-coleccion.png` - Colección configuraciones en MongoDB Atlas (3 documentos)

# 6\. `06-sqlite-tabla.png` - Tabla productos en SQLite (7 registros)

# 

# \## Estructura del proyecto

# 

# ```text

# Novha/

# ├── app.py              # Punto de entrada Flask + registro de rutas HTML y API

# ├── api.py              # Blueprint con los 12 endpoints de la API REST

# ├── db.py               # Conexiones a SQLite y MongoDB

# ├── init\_db.py          # Crea la base SQLite con 7 productos iniciales

# ├── seed\_mongo.py       # Puebla MongoDB con 3 configuraciones de ejemplo

# ├── auth.py             # (Reservado para autenticación JWT)

# ├── requirements.txt    # Dependencias

# ├── .env.example        # Plantilla de variables de entorno

# ├── static/             # CSS, JS e imágenes

# ├── templates/          # Plantillas HTML (Jinja2)

# ├── docs/               # Capturas de evidencias

# └── README.md

# ```

# 

# \## Seguridad

# 

# \- El archivo `.env` con credenciales reales no se sube a GitHub (está en `.gitignore`).

# \- Solo se sube `.env.example` con valores ficticios.

# \- La base SQLite `novha.db` tampoco se sube (se regenera con `init\_db.py`).

# 

# \## Autores

# 

# \- Johami Silva 

# \- Julian Suarez

# 

# \## Referencias

# 

# \- \[Flask Documentation](https://flask.palletsprojects.com/)

# \- \[PyMongo Documentation](https://pymongo.readthedocs.io/)

# \- \[MongoDB Atlas](https://www.mongodb.com/atlas/database)

# \- \[SQLite Documentation](https://www.sqlite.org/docs.html)

