"""Ejemplo completo de uso de GRmenu: una calculadora.

Generado por `python -m GRmenu -e` / `python -m GRmenu --Example`.
Ejecutalo con: python example.py
"""

import sys

from GRmenu import GRmenu


def _pedir_numero(mensaje):
    while True:
        texto = input(mensaje)
        try:
            return float(texto)
        except ValueError:
            print("Numero invalido, intenta de nuevo.")


def sumar():
    a = _pedir_numero("Primer numero: ")
    b = _pedir_numero("Segundo numero: ")
    print(f"{a} + {b} = {a + b}")
    input("Presiona Enter para volver al menu...")


def restar():
    a = _pedir_numero("Primer numero: ")
    b = _pedir_numero("Segundo numero: ")
    print(f"{a} - {b} = {a - b}")
    input("Presiona Enter para volver al menu...")


def multiplicar():
    a = _pedir_numero("Primer numero: ")
    b = _pedir_numero("Segundo numero: ")
    print(f"{a} * {b} = {a * b}")
    input("Presiona Enter para volver al menu...")


def dividir():
    a = _pedir_numero("Primer numero: ")
    b = _pedir_numero("Segundo numero: ")
    if b == 0:
        print("No se puede dividir por cero.")
    else:
        print(f"{a} / {b} = {a / b}")
    input("Presiona Enter para volver al menu...")


def salir():
    print("Hasta luego!")
    sys.exit()


if __name__ == "__main__":
    # GRmenu.banner() es un helper estatico: imprime un banner suelto,
    # sin crear ningun menu (util para encabezados de script, splash, etc).
    GRmenu.banner("Calc", color="cyan", style=3, font=1)

    # Los colores globales (SetStyle) se pueden ajustar antes de crear
    # el menu; quedan vigentes para cualquier instancia que se cree despues.
    GRmenu.SetStyle.Border("cyan", 1)
    GRmenu.SetStyle.Options("white", 1)
    GRmenu.SetStyle.Focus("green", 2)
    GRmenu.SetStyle.Title("yellow", 2)
    GRmenu.SetStyle.Banner("magenta", 2)
    GRmenu.SetStyle.Subtitle("cyan", 2)
    GRmenu.SetStyle.Divider("blue", 1)

    while True:
        # Se crea un menu nuevo en cada vuelta: GRmenu.__init__ pone la
        # terminal en modo TTY crudo, que draw() restaura al elegir una
        # opcion, asi que hay que volver a crearlo para la siguiente vuelta.
        menu = GRmenu(
            # Cada opcion puede ser una funcion (se usa su nombre) o una
            # tupla (nombre a mostrar, funcion a ejecutar).
            [
                ("Sumar (+)", sumar),
                ("Restar (-)", restar),
                ("Multiplicar (x)", multiplicar),
                ("Dividir (/)", dividir),
                ("Salir", salir),
            ],
            title="Calculadora",                   # Titulo en el marco de opciones
            style=7,                                # Estilo de marco de opciones (1 al 20)
            banner="CALC",                          # Texto gigante en arte ASCII 3D
            subtitle="Menu principal\nUsa las flechas y Enter",  # soporta \n
            banner_style=3,                         # Estilo de marco del banner (1 al 20)
            font=1,                                 # Fuente ASCII del banner (1 al 10)
            divider=True,                           # Lineas divisorias junto al banner
            center=True,                            # Centrado simetrico
        )
        menu.draw(size_max=30)
