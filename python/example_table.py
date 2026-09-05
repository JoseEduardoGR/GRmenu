"""Ejemplo de uso de GRmenu: un menu estilo tabla con GRDataTable.

Ejecutalo con: python example_table.py
"""
import sys

from GRmenu import GRmenu, GRSubMenu, GRDataTable

# (codigo, nombre, precio, stock)
PRODUCTOS = [
    ("001", "Teclado mecanico", 45000, 12),
    ("002", "Mouse inalambrico", 18000, 30),
    ("003", "Monitor 24\"", 120000, 5),
    ("004", "Auriculares", 25000, 0),
    ("005", "Webcam HD", 30000, 8),
]


def ver_producto(codigo, nombre, precio, stock):
    # Closure: cada fila necesita SU PROPIA funcion (no una compartida),
    # asi que esto arma una nueva por producto, con sus datos ya adentro.
    def _ver():
        print(f"Codigo:  {codigo}")
        print(f"Nombre:  {nombre}")
        print(f"Precio:  ${precio}")
        print(f"Stock:   {stock} unidades" + (" (SIN STOCK)" if stock == 0 else ""))
        input("Presiona Enter para volver al menu...")
    return _ver


def mostrar_metrica(nombre, valor):
    def _ver():
        print(f"{nombre}: {valor}")
        input("Presiona Enter para volver al menu...")
    return _ver


def restaurar_colores():
    GRmenu.SetStyle.Border("cyan", 1)
    GRmenu.SetStyle.Options("white", 1)
    GRmenu.SetStyle.Focus("green", 2)
    GRmenu.SetStyle.Title("yellow", 2)
    print("Colores restaurados a los valores por defecto de este ejemplo.")
    input("Presiona Enter para volver al menu...")


def salir():
    print("Hasta luego!")
    sys.exit()


if __name__ == "__main__":
    # Cada fila de una GRDataTable es (celdas, funcion) o (celdas, funcion,
    # descripcion) -- una celda por columna declarada en `columns` de
    # GRDataTable, en vez del nombre unico de un GRmenu comun.
    filas_productos = [
        (
            [codigo, nombre, f"${precio}", str(stock)],
            ver_producto(codigo, nombre, precio, stock),
            "Sin stock" if stock == 0 else f"{stock} unidades disponibles",
        )
        for codigo, nombre, precio, stock in PRODUCTOS
    ]

    # GRDataTable.SubTable anida OTRA tabla (con sus propias columnas) en
    # vez de un GRSubMenu comun de una sola columna.
    resumen = GRDataTable.SubTable(
        [
            (["Total de productos", str(len(PRODUCTOS))], mostrar_metrica("Total de productos", len(PRODUCTOS))),
            (["Sin stock", str(sum(1 for _, _, _, s in PRODUCTOS if s == 0))],
             mostrar_metrica("Sin stock", sum(1 for _, _, _, s in PRODUCTOS if s == 0))),
        ],
        name="Resumen",
        columns=["Metrica", "Valor"],
        col_align=["l", "r"],
    )

    # Un GRSubMenu comun (sin columnas) tambien se puede colgar entre
    # las filas de la tabla: se dibuja como una fila normal de ancho
    # completo, sin romper el resto de las columnas.
    configuracion = GRSubMenu([
        ("Restaurar colores", restaurar_colores, "Vuelve SetStyle a los valores de este ejemplo"),
    ], name="Configuracion")

    tabla = GRDataTable(
        filas_productos + [resumen, configuracion, ("Salir", salir, "Cierra el ejemplo")],
        columns=["Codigo", "Producto", "Precio", "Stock"],
        col_align=["l", "l", "r", "r"],
        title="Inventario",
        subtitle="Ejemplo de GRDataTable: menu con columnas alineadas\nFlechas + Enter para elegir, \"/\" para buscar",
        banner="STOCK",
        banner_style=3,
        font=1,
        divider=True,
        center=True,
        style=7,
        searchable=True,
        max_show_options=10,
        animate="rgb",
    )
    tabla.draw()
