"""
database.py - Capa de acceso a datos (SQLite)
----------------------------------------------
Contiene todas las operaciones con la base de datos de la biblioteca
personal. No imprime ni pide datos al usuario: eso lo hace main.py.

Tabla: libros
  id     INTEGER PRIMARY KEY AUTOINCREMENT
  titulo TEXT    NOT NULL
  autor  TEXT    NOT NULL
  genero TEXT    NOT NULL
  leido  INTEGER NOT NULL  (1 = leído, 0 = no leído)
"""

import sqlite3
from pathlib import Path

# La base de datos se guarda en la carpeta "datos", junto a este archivo.
CARPETA_DATOS = Path(__file__).resolve().parent / "datos"
DB_NAME = CARPETA_DATOS / "biblioteca_personal.db"

# Listas blancas: los nombres de columnas no se pueden pasar como
# parámetros "?", así que solo aceptamos los que están aquí.
CAMPOS_BUSQUEDA = ("titulo", "autor", "genero")
CAMPOS_EDITABLES = ("titulo", "autor", "genero", "leido")


def conectar() -> sqlite3.Connection:
    """Crea la carpeta 'datos' si hace falta, abre la base y crea la tabla."""
    CARPETA_DATOS.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_NAME)
    con.row_factory = sqlite3.Row  # permite acceder a columnas por nombre
    crear_tabla(con)
    return con


def crear_tabla(con: sqlite3.Connection) -> None:
    """Crea la tabla 'libros' si todavía no existe."""
    con.execute("""
        CREATE TABLE IF NOT EXISTS libros (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT    NOT NULL,
            autor  TEXT    NOT NULL,
            genero TEXT    NOT NULL,
            leido  INTEGER NOT NULL DEFAULT 0 CHECK (leido IN (0, 1))
        )
    """)
    con.commit()


def agregar_libro(con, titulo: str, autor: str, genero: str, leido: int) -> int:
    """Inserta un libro nuevo y devuelve el id que se le asignó."""
    cursor = con.execute(
        "INSERT INTO libros (titulo, autor, genero, leido) VALUES (?, ?, ?, ?)",
        (titulo, autor, genero, leido),
    )
    con.commit()
    return cursor.lastrowid


def obtener_libro(con, libro_id: int):
    """Devuelve el libro con ese id, o None si no existe."""
    return con.execute(
        "SELECT * FROM libros WHERE id = ?", (libro_id,)
    ).fetchone()


def listar_libros(con) -> list:
    """Devuelve todos los libros ordenados por id."""
    return con.execute("SELECT * FROM libros ORDER BY id").fetchall()


def buscar_libros(con, campo: str, texto: str) -> list:
    """Busca libros cuyo 'campo' (titulo, autor o genero) contenga el texto."""
    if campo not in CAMPOS_BUSQUEDA:
        raise ValueError(f"Campo de búsqueda no válido: {campo}")
    return con.execute(
        f"SELECT * FROM libros WHERE {campo} LIKE ? ORDER BY id",
        (f"%{texto}%",),
    ).fetchall()


def actualizar_libro(con, libro_id: int, cambios: dict) -> bool:
    """
    Modifica los campos indicados en 'cambios' (por ejemplo
    {"autor": "Nuevo autor", "leido": 1}).
    Devuelve True si el libro existía y se actualizó.
    """
    campos = [c for c in cambios if c in CAMPOS_EDITABLES]
    if not campos:
        return False
    asignaciones = ", ".join(f"{c} = ?" for c in campos)
    valores = [cambios[c] for c in campos] + [libro_id]
    cursor = con.execute(f"UPDATE libros SET {asignaciones} WHERE id = ?", valores)
    con.commit()
    return cursor.rowcount > 0


def eliminar_libro(con, libro_id: int) -> bool:
    """Elimina el libro. Devuelve True si existía."""
    cursor = con.execute("DELETE FROM libros WHERE id = ?", (libro_id,))
    con.commit()
    return cursor.rowcount > 0
