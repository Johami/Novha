from db import get_sql

PRODUCTOS = [
    ("Chaqueta clásica", "Chaquetas", "Diseño cómodo y funcional para el día a día.", 95000, "img/chaqueta-1.jpg"),
    ("Chaqueta personalizada", "Chaquetas", "Personalízala con diseños y bordados a tu gusto.", 105000, "img/chaqueta-2.jpg"),
    ("Chaqueta de trabajo", "Chaquetas", "Pensada para acompañarte durante tus jornadas laborales.", 100000, "img/chaqueta-3.jpg"),
    ("Overol de trabajo", "Overoles", "Overol industrial de dos piezas (chaleco + pantalón).", 120000, "img/categorias/overoles.jpg"),
    ("Ruana disponible", "Ruanas", "Ruana según diseños y existencias actuales.", None, "img/ruanas/ruana-1.jpg"),
    ("Cojín personalizado", "Cojines", "Cojín con bordado personalizado.", 25000, "img/cojines/cojin-1.jpg"),
    ("Polo básico", "Polos", "Polo cómodo y versátil para trabajo o uso diario.", 45000, "img/categorias/polos.jpg"),
]

def init():
    conn = get_sql()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            descripcion TEXT,
            precio_referencia REAL,
            imagen_principal TEXT,
            activo INTEGER NOT NULL DEFAULT 1,
            creado_en TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nombre TEXT,
            rol TEXT NOT NULL DEFAULT 'cliente',
            activo INTEGER NOT NULL DEFAULT 1,
            creado_en TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("SELECT COUNT(*) FROM productos")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO productos (nombre, categoria, descripcion, precio_referencia, imagen_principal) VALUES (?, ?, ?, ?, ?)",
            PRODUCTOS,
        )
        print(f"✅ {len(PRODUCTOS)} productos insertados")

    conn.commit()
    conn.close()
    print("✅ Base de datos lista: novha.db")
    print("✅ Tabla usuarios creada (vacía, para Entrega JWT)")

if __name__ == "__main__":
    init()