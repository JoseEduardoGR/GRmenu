"""Ejemplo completo de uso de GRmenu.

Generado por `python -m GRmenu -e` / `python -m GRmenu --Example`.
Ejecutalo con: python example.py
"""

from GRmenu import GRmenu


def opcion_reiniciar():
    print("Reiniciando el servicio...")


def opcion_logs():
    print("Mostrando los ultimos logs...")


def opcion_salir():
    print("Hasta luego!")


if __name__ == "__main__":
    # GRmenu.banner() es un helper estatico: imprime un banner suelto,
    # sin crear ningun menu (util para encabezados de script, splash, etc).
    GRmenu.banner("GRmenu", color="cyan", style=3, font=1)

    # Los colores globales (SetStyle) se pueden ajustar antes de crear
    # el menu; quedan vigentes para cualquier instancia que se cree despues.
    GRmenu.SetStyle.Border("cyan", 1)
    GRmenu.SetStyle.Options("white", 1)
    GRmenu.SetStyle.Focus("green", 2)
    GRmenu.SetStyle.Title("yellow", 2)
    GRmenu.SetStyle.Banner("magenta", 2)
    GRmenu.SetStyle.Subtitle("cyan", 2)
    GRmenu.SetStyle.Divider("blue", 1)

    menu = GRmenu(
        # Cada opcion puede ser una funcion (se usa su nombre) o una tupla
        # (nombre a mostrar, funcion a ejecutar).
        [
            opcion_reiniciar,
            ("Ver logs", opcion_logs),
            ("Salir", opcion_salir),
        ],
        title="Panel de Control",              # Titulo en el marco de opciones
        style=7,                                # Estilo de marco de opciones (1 al 20)
        banner="DEV OPS",                       # Texto gigante en arte ASCII 3D
        subtitle="Consola de Administracion\nUsa las flechas y Enter",  # soporta \n
        banner_style=3,                         # Estilo de marco del banner (1 al 20)
        font=1,                                 # Fuente ASCII del banner (1 al 10)
        divider=True,                           # Lineas divisorias junto al banner
        center=True,                            # Centrado simetrico
    )

    menu.draw(size_max=30)
