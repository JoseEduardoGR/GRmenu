"""Ejemplo de uso de GRmenu: una grilla de opciones con GRtable.

Ejecutalo con: python example_grid.py
"""
from GRmenu import GRmenu, GRtable

USUARIOS = ["admin", "ana", "luz", "bob"]


def ver_usuario(nombre):
    # Closure: cada celda necesita SU PROPIA funcion (no una
    # compartida), asi que esto arma una nueva por usuario.
    def _ver():
        print(f"Usuario: {nombre}")
        print("Rol: administrador" if nombre == "admin" else "Rol: usuario comun")
        input("Presiona Enter para volver a la grilla...")
    return _ver


def editar_usuario(nombre):
    def _editar():
        print(f"Editando a {nombre}...")
        input("Presiona Enter para volver a la grilla...")
    return _editar


def borrar_usuario(nombre):
    def _borrar():
        print(f"{nombre} eliminado.")
        input("Presiona Enter para volver a la grilla...")
    return _borrar


if __name__ == "__main__":
    # Cada celda de una GRtable es su PROPIA opcion, con su propia
    # funcion -- a diferencia de GRDataTable (una sola funcion por
    # FILA), aca cada combinacion (fila, columna) hace algo distinto.
    # `None` deja un hueco: no se puede seleccionar (por ejemplo, no se
    # puede borrar al admin).
    grilla = [
        [
            (nombre, ver_usuario(nombre), f"Ver ficha de {nombre}"),
            ("Editar", editar_usuario(nombre)),
            None if nombre == "admin" else ("Borrar", borrar_usuario(nombre), f"Elimina a {nombre}"),
        ]
        for nombre in USUARIOS
    ]

    tabla = GRtable(
        grilla,
        columns=["Usuario", "Editar", "Borrar"],
        title="Usuarios",
        subtitle="Ejemplo de GRtable: grilla de opciones\nFlechas en las 4 direcciones + Enter para elegir",
        banner="GRID",
        banner_style=3,
        font=1,
        divider=True,
        center=True,
        style=7,
        max_show_rows=10,
        animate="rgb",
    )
    tabla.draw()
