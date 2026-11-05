import requests

BASE = "http://localhost:5000/api/configuraciones"

configuraciones = [
    {
        "producto_id": 1,
        "caracteristicas": {
            "talla": ["S", "M", "L", "XL"],
            "color_tela": ["Negro", "Azul", "Beige"],
            "material": ["Nautica"],
            "tipo_cremallera": ["Metalica", "Plastica"]
        },
        "especificaciones": "Consulta colores disponibles"
    },
    {
        "producto_id": 4,
        "caracteristicas": {
            "talla": ["S", "M", "L", "XL"],
            "material": ["Dril", "Nautica"],
            "color_tela": ["Azul", "Negro", "Verde"],
            "forro": ["Fleece", "Tafeta"],
            "tipo": ["Chaleco", "Pantalon", "Conjunto completo"]
        },
        "especificaciones": "Personalizacion segun solicitud"
    },
    {
        "producto_id": 6,
        "caracteristicas": {
            "tamano_bordado": ["Pequeno", "Mediano", "Grande"],
            "tipo_bordado": ["Nombre", "Logo", "Imagen"],
            "material": ["Tela suave", "Lino"]
        },
        "especificaciones": "Se puede personalizar con nombres, imagenes y disenos"
    }
]

for c in configuraciones:
    print(f"\n→ Creando config para producto {c['producto_id']}...")
    r = requests.post(BASE, json=c)
    print(f"  Status: {r.status_code}")
    print(f"  Response: {r.text[:200]}")