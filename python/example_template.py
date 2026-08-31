"""Ejemplo completo de uso de GRmenu: referencia interactiva de la libreria.

Generado por `python -m GRmenu -e` || `python -m GRmenu --Example`.
Ejecutalo con: python example.py
"""
import sys
import webbrowser

from GRmenu import GRmenu, GRSubMenu

REPO_URL = "https://github.com/JoseEduardoGR/GRmenu"

def salir():
    print("Hasta luego!")
    sys.exit()


def acerca_de():
    print("GRmenu - libreria de menus interactivos para terminal.")
    input("Presiona Enter para volver al menu...")


def restaurar_colores():
    GRmenu.SetStyle.Border("cyan", 1)
    GRmenu.SetStyle.Options("white", 1)
    GRmenu.SetStyle.Focus("green", 2)
    GRmenu.SetStyle.Title("yellow", 2)
    print("Colores restaurados a los valores por defecto de este ejemplo.")
    input("Presiona Enter para volver al menu...")


# Opciones que usan `webbrowser` (modulo estandar, no hace falta instalar
# nada) para abrir el repositorio del lado del navegador del usuario.

def abrir_repositorio():
    webbrowser.open(REPO_URL)
    print(f"Abriendo {REPO_URL} en el navegador...")
    input("Presiona Enter para volver al menu...")


def reportar_issue():
    webbrowser.open(f"{REPO_URL}/issues/new")
    print("Abriendo el formulario para reportar un issue...")
    input("Presiona Enter para volver al menu...")


def ver_issues():
    webbrowser.open(f"{REPO_URL}/issues")
    print("Abriendo los issues del repositorio...")
    input("Presiona Enter para volver al menu...")


# Las siguientes opciones reutilizan los mismos helpers "privados" (_print_*)
# que ya usa la CLI (`python -m GRmenu -s/-b/-d/-a`), asi que no duplican
# nada; sirven ademas para tener mas de 10 opciones y ver el scroll de
# `max_show_options` en accion (ver GRmenu(..., max_show_options=...) abajo).

def ver_estilos_marco():
    GRmenu._print_style_help()
    input("Presiona Enter para volver al menu...")


def ver_fuentes_banner():
    GRmenu._print_banner_help()
    input("Presiona Enter para volver al menu...")


def ver_colores():
    print(GRmenu._colorize("Colores disponibles (GRmenu.COLORS()):", {"color": "magenta", "level": 2}))
    color_names = [c for c in GRmenu.COLORS() if c != "reset"]
    print("  " + ", ".join(GRmenu._colorize(c, {"color": c, "level": 2}) for c in color_names))
    print("  Brillo: 1 = normal, 2 = brillante (SetStyle.*(color, level)).")
    input("Presiona Enter para volver al menu...")


def explicar_divider():
    GRmenu._print_divider_help()
    input("Presiona Enter para volver al menu...")


def ver_guia_completa():
    GRmenu._print_all_help()
    input("Presiona Enter para volver al menu...")


def ver_metodos_setstyle():
    print(GRmenu._colorize("Metodos de SetStyle (colores/estilo global):", {"color": "magenta", "level": 2}))
    metodos = [
        ("SetStyle.Border(color, level)", "color del marco de opciones."),
        ("SetStyle.Options(color, level)", "color de las opciones no activas."),
        ("SetStyle.Focus(color, level)", "color de la opcion con foco."),
        ("SetStyle.Description(color, level)", "color de la descripcion/hints."),
        ("SetStyle.Welcome(text, image)", "pantalla de bienvenida (ver 'Ver bienvenida')."),
    ]
    for sig, desc in metodos:
        print(f"  {GRmenu._colorize(sig.ljust(34), {'color': 'cyan', 'level': 1})} -> {desc}")
    input("Presiona Enter para volver al menu...")


def ver_bienvenida():
    print("SetStyle.Welcome(text=None, image=None, width=None, height=None)")
    print("configura lo que se ve una sola vez, antes de la primera tecla,")
    print("al llamar a menu.draw(). Sin argumentos usa el logo por defecto")
    print("(imagen real si la terminal la soporta; si no, esta version ASCII):")
    print()
    for line in GRmenu._DEFAULT_LOGO_ASCII.splitlines():
        print(line)
    print()
    print('Con text="..." se usa ese texto en vez del logo (anda en cualquier')
    print('terminal). Con image="ruta.png" se intenta esa imagen, con text')
    print("como respaldo si la terminal no soporta imagenes embebidas.")
    input("Presiona Enter para volver al menu...")


def probar_banner():
    GRmenu.banner("DEMO", color="orange", style=7, font=3)
    input("Presiona Enter para volver al menu...")


def ver_teclas():
    print(GRmenu._colorize("Teclas del menu:", {"color": "magenta", "level": 2}))
    teclas = [
        ("Arriba / Abajo", "mueve la seleccion (o scrollea si hay mas de max_show_options)."),
        ("Derecha / Enter (en un GRSubMenu)", "entra a su panel."),
        ("Izquierda", "vuelve al panel anterior."),
        ("Enter (en una opcion)", "la ejecuta y cierra el menu."),
        ("t", "preview del codigo fuente de la opcion resaltada."),
        ("/", "busqueda (si searchable=True); 't'/'q' se vuelven texto."),
        ("Espacio", "marca/desmarca con [x]; Enter ejecuta todas en orden."),
        ("q / Ctrl+C", "sale sin ejecutar nada."),
    ]
    for tecla, desc in teclas:
        print(f"  {GRmenu._colorize(tecla.ljust(34), {'color': 'green', 'level': 2})} -> {desc}")
    input("Presiona Enter para volver al menu...")


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
    # SetStyle.Welcome define la pantalla de bienvenida (antes de la primera
    # tecla). Dos formas de usarla:
    #
    # Caso 1: imagen. Solo se ve como imagen real en terminales que soportan
    # el protocolo de iTerm2 o Kitty (Kitty, WezTerm, iTerm2, Konsole...);
    # en las que no lo soportan, cae al `text` de respaldo si se lo pasas
    # (si no le pasas texto, se imprime un aviso).
    GRmenu.SetStyle.Welcome()

    # Caso 2: solo texto, sin imagen. Anda igual en cualquier terminal.
    # (Descomentar esta linea reemplaza al caso 1 de arriba.)
    # GRmenu.SetStyle.Welcome(text="=== GRMENU ===")

    # Si no llamas a SetStyle.Welcome() para nada, se usa el logo por
    # defecto de GRmenu (imagen real o su version ASCII segun la terminal).

    # Un GRSubMenu es una lista de opciones anidada: se pasa directo (sin
    # tupla) dentro de la lista de opciones del GRmenu/GRSubMenu que lo
    # contiene. No tiene titulo/banner/subtitle propios (hereda colores
    # de GRmenu.SetStyle); "Avanzado" muestra que un GRSubMenu puede tener
    # a su vez otro GRSubMenu adentro.
    avanzado = GRSubMenu([
        ("Restaurar colores", restaurar_colores, "Vuelve SetStyle a los valores de este ejemplo"),
    ], name="Avanzado")

    configuracion = GRSubMenu([
        ("Acerca de", acerca_de, "Info de la libreria"),
        avanzado,
    ], name="Configuracion")

    repositorio = GRSubMenu([
        ("Abrir repositorio", abrir_repositorio, "Abre GRmenu en GitHub"),
        ("Reportar un issue", reportar_issue, "Abre el formulario de nuevo issue"),
        ("Ver issues abiertos", ver_issues, "Lista de issues del repositorio"),
    ], name="Repositorio")

    # Se crea un menu nuevo en cada vuelta: GRmenu.__init__ pone la
    # terminal en modo TTY crudo, que draw() restaura al elegir una
    # opcion, asi que hay que volver a crearlo para la siguiente vuelta.
    menu = GRmenu(
        # Cada opcion puede ser una funcion (se usa su nombre), una tupla
        # (nombre a mostrar, funcion a ejecutar), una tupla con un tercer
        # elemento (nombre, funcion, descripcion) que se muestra abajo a
        # la derecha del recuadro mientras esa opcion este seleccionada,
        # o un GRSubMenu (ver arriba): su panel aparece automaticamente a
        # la derecha en cuanto esa fila esta resaltada; flecha derecha o
        # Enter mueve el foco adentro, flecha izquierda vuelve.
        [
            configuracion,
            ("Ver estilos de marco", ver_estilos_marco, "Recorre style 1 al 20"),
            ("Ver fuentes del banner", ver_fuentes_banner, "Recorre font 1 al 10"),
            ("Ver colores disponibles", ver_colores, "Paleta de GRmenu.COLORS()"),
            ("Explicar 'divider'", explicar_divider, "Lineas junto al banner/subtitle"),
            ("Ver bienvenida", ver_bienvenida, "Como configurar SetStyle.Welcome"),
            ("Probar un banner suelto", probar_banner, "GRmenu.banner() sin crear un menu"),
            ("Ver guia completa", ver_guia_completa, "Todo junto (como -a en la CLI)"),
            ("Ver metodos de SetStyle", ver_metodos_setstyle, "Border/Options/Focus/etc"),
            ("Ver teclas del menu", ver_teclas, "Flechas, Enter, t, q..."),
            repositorio,
            ("Salir", salir, "Cierra el ejemplo"),
        ],
        title="GRmenu",                         # Titulo en el marco de opciones
        style=7,                                # Estilo de marco de opciones (1 al 20)
        banner="GRMENU",                        # Texto gigante en arte ASCII 3D
        subtitle="Referencia interactiva\nUsa las flechas o rueda del raton y Enter",  # soporta \n
        banner_style=3,                         # Estilo de marco del banner (1 al 20)
        font=1,                                 # Fuente ASCII del banner (1 al 10)
        divider=True,                           # Lineas divisorias junto al banner
        center=True,                            # Centrado simetrico
        max_show_options=10,                    # Ventana de opciones visibles; con 11 opciones, scrollea
        searchable=True,                        # "/" filtra las opciones por nombre a medida que escribis
        animate="rgb"
    )
    menu.draw()
