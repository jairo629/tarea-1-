"""
main.py - Biblioteca personal (menú de consola)
------------------------------------------------
Interfaz de usuario. Usa las funciones de database.py para guardar
y consultar los libros en SQLite.

Uso:  python main.py
"""

import database as db

ESTADOS = {1: "Leído", 0: "No leído"}


# --------------------------- Utilidades de entrada ---------------------------


def pedir_texto(mensaje: str) -> str:
    """Pide un texto y repite la pregunta hasta que no esté vacío."""
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("  Este campo no puede estar vacío.")


def pedir_estado(mensaje: str = "Estado de lectura (1 = Leído, 2 = No leído): ") -> int:
    """Pide el estado de lectura. Devuelve 1 (leído) o 0 (no leído)."""
    while True:
        opcion = input(mensaje).strip()
        if opcion == "1":
            return 1
        if opcion == "2":
            return 0
        print("  Elige 1 o 2.")


def pedir_libro_existente(con):
    """Pide un id y devuelve el libro, o None si no es válido o no existe."""
    texto = input("ID del libro: ").strip()
    if not texto.isdigit():
        print("  El ID debe ser un número.\n")
        return None
    libro = db.obtener_libro(con, int(texto))
    if libro is None:
        print("  No existe un libro con ese ID.\n")
    return libro


# ------------------------------- Presentación -------------------------------


def mostrar_libros(libros: list) -> None:
    """Imprime los libros en forma de tabla."""
    if not libros:
        print("  No hay libros para mostrar.\n")
        return

    encabezados = ("ID", "Título", "Autor", "Género", "Estado")
    filas = [
        (str(l["id"]), l["titulo"], l["autor"], l["genero"], ESTADOS[l["leido"]])
        for l in libros
    ]
    # Ancho de cada columna = el texto más largo de esa columna.
    anchos = [max(len(fila[i]) for fila in [encabezados] + filas) for i in range(5)]

    def linea(fila):
        return "  " + " | ".join(texto.ljust(ancho) for texto, ancho in zip(fila, anchos))

    print(linea(encabezados))
    print("  " + "-+-".join("-" * ancho for ancho in anchos))
    for fila in filas:
        print(linea(fila))
    print(f"\n  Total: {len(filas)} libro(s)\n")


# --------------------------------- Opciones ---------------------------------


def opcion_agregar(con) -> None:
    print("\n--- Agregar libro ---")
    titulo = pedir_texto("Título: ")
    autor = pedir_texto("Autor: ")
    genero = pedir_texto("Género: ")
    leido = pedir_estado()
    nuevo_id = db.agregar_libro(con, titulo, autor, genero, leido)
    print(f"  Libro agregado con ID {nuevo_id}.\n")


def opcion_actualizar(con) -> None:
    print("\n--- Actualizar libro ---")
    libro = pedir_libro_existente(con)
    if libro is None:
        return

    print("  Presiona Enter para dejar un campo sin cambios.")
    cambios = {}

    titulo = input(f"Título [{libro['titulo']}]: ").strip()
    if titulo:
        cambios["titulo"] = titulo
    autor = input(f"Autor [{libro['autor']}]: ").strip()
    if autor:
        cambios["autor"] = autor
    genero = input(f"Género [{libro['genero']}]: ").strip()
    if genero:
        cambios["genero"] = genero

    estado_actual = ESTADOS[libro["leido"]]
    while True:
        estado = input(f"Estado [{estado_actual}] (1 = Leído, 2 = No leído): ").strip()
        if estado == "":
            break
        if estado in ("1", "2"):
            cambios["leido"] = 1 if estado == "1" else 0
            break
        print("  Elige 1, 2 o Enter para no cambiar.")

    if not cambios:
        print("  No se hicieron cambios.\n")
    elif db.actualizar_libro(con, libro["id"], cambios):
        print("  Libro actualizado.\n")


def opcion_eliminar(con) -> None:
    print("\n--- Eliminar libro ---")
    libro = pedir_libro_existente(con)
    if libro is None:
        return

    print(f"  {libro['titulo']} - {libro['autor']}")
    confirmar = input("¿Seguro que quieres eliminarlo? (s/n): ").strip().lower()
    if confirmar == "s":
        db.eliminar_libro(con, libro["id"])
        print("  Libro eliminado.\n")
    else:
        print("  Operación cancelada.\n")


def opcion_listar(con) -> None:
    print("\n--- Listado de libros ---")
    mostrar_libros(db.listar_libros(con))


def opcion_buscar(con) -> None:
    print("\n--- Buscar libros ---")
    print("  1. Por título\n  2. Por autor\n  3. Por género")
    campos = {"1": "titulo", "2": "autor", "3": "genero"}
    campo = campos.get(input("Buscar por: ").strip())
    if campo is None:
        print("  Opción no válida.\n")
        return

    texto = pedir_texto("Texto a buscar: ")
    mostrar_libros(db.buscar_libros(con, campo, texto))


# ------------------------------------ Menú ----------------------------------


def mostrar_menu() -> None:
    print("=" * 36)
    print("     BIBLIOTECA PERSONAL")
    print("=" * 36)
    print("  1. Agregar nuevo libro")
    print("  2. Actualizar un libro")
    print("  3. Eliminar un libro")
    print("  4. Ver listado de libros")
    print("  5. Buscar libros")
    print("  6. Salir")


def main() -> None:
    con = db.conectar()
    acciones = {
        "1": opcion_agregar,
        "2": opcion_actualizar,
        "3": opcion_eliminar,
        "4": opcion_listar,
        "5": opcion_buscar,
    }
    try:
        while True:
            mostrar_menu()
            opcion = input("Elige una opción: ").strip()
            if opcion == "6":
                break
            accion = acciones.get(opcion)
            if accion:
                accion(con)
            else:
                print("\n  Opción no válida. Elige un número del 1 al 6.\n")
    finally:
        con.close()
        print("\nBase de datos cerrada. ¡Hasta pronto!")


if __name__ == "__main__":
    main()
