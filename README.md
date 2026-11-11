# 🛍️ Novha - Catálogo con Persistencia Políglota

**Catálogo web interactivo para un negocio de ropa y personalización en Corabastos, Bogotá.**

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=flat-square&logo=sqlite&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=flat-square&logo=mongodb&logoColor=white)

---

## 📖 Descripción del Proyecto

**Novha** es un negocio de confección y personalización de prendas de trabajo. Esta aplicación implementa una arquitectura de **Persistencia Políglota**, combinando lo mejor de dos mundos para gestionar el catálogo:

- 🗄️ **SQLite:** Datos estructurados del catálogo (productos).
- 🍃 **MongoDB Atlas:** Características variables por producto (tallas, colores, materiales, forros).
- ⚡ **Flask:** API REST que combina ambas bases de datos en tiempo real.

---

## 🏗️ Arquitectura

```text
+----------------------------------------+
|    Frontend (Vue.js 3 (CND)/Bootstrap) |
+--------------+-------------------------+
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
|  productos  |   |  configuraciones  |
|  usuarios   |   | (caract. variables)|
+-------------+   +-------------------+

## 🎨 Frontend con Vue.js
El frontend ha sido migrado a Vue.js (usando la versión CDN para mantener la simplicidad del proyecto). 
- **Reactividad:** Todas las páginas de categorías (`chaquetas.html`, `overoles.html`, etc.) y el catálogo cargan los productos dinámicamente usando `fetch()` hacia la API.
- **Detalle del Producto:** La vista `/producto/<id>` consume el endpoint combinado (`/api/productos/<id>/detalle`) para mostrar en una sola pantalla los datos de SQLite y las características de MongoDB.
- **Sin recargas:** La navegación es fluida y los datos se actualizan sin necesidad de recargar la página.