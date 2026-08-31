"""Ejemplo enfocado en las funcionalidades mas nuevas de GRmenu:
`animate` (borde/banner animado) y `ExportConfig`/`ImportConfig` (guardar y
cargar el tema de colores en un archivo `.gr` propio, no YAML/JSON).

Ejecutalo con: python example_config.py

Tambien sirve como archivo de prueba para la exportacion sin interactuar:
    python -m GRmenu -ex example_config.py
Eso carga este script (corre el tema de mas abajo, pero `menu.draw()` no
hace nada) y deja "example_config.gr" al lado de este archivo, con el
tema que se ve aca configurado.
"""
from GRmenu import GRmenu

CONFIG_PATH = "theme.gr"


def _aplicar_oceano():
    """Solo aplica el tema (sin print/input): la reusan tanto el callback
    interactivo `tema_oceano` como el `__main__` de mas abajo, que necesita
    aplicar un tema inicial SIN bloquear esperando una tecla (por ejemplo
    al cargar este archivo con `python -m GRmenu -ex`)."""
    GRmenu.SetStyle.Border("aqua", 2)
    GRmenu.SetStyle.Options("white", 1)
    GRmenu.SetStyle.Focus("cyan", 2)
    GRmenu.SetStyle.Title("blue", 2)
    GRmenu.SetStyle.Banner("aqua", 2)
    GRmenu.SetStyle.Subtitle("cyan", 1)
    GRmenu.SetStyle.Divider("blue", 1)
    GRmenu.SetStyle.Description("gray", 1)


def _aplicar_incendio():
    GRmenu.SetStyle.Border("orange", 2)
    GRmenu.SetStyle.Options("yellow", 1)
    GRmenu.SetStyle.Focus("red", 2)
    GRmenu.SetStyle.Title("orange", 2)
    GRmenu.SetStyle.Banner("red", 2)
    GRmenu.SetStyle.Subtitle("yellow", 1)
    GRmenu.SetStyle.Divider("orange", 1)
    GRmenu.SetStyle.Description("gray", 1)


def tema_oceano():
    """Un tema con paleta fria (aqua/azul/cyan)."""
    _aplicar_oceano()
    print("Tema 'Oceano' aplicado.")
    input("Presiona Enter para volver al menu...")


def tema_incendio():
    """Un tema con paleta calida (orange/red/yellow)."""
    _aplicar_incendio()
    print("Tema 'Incendio' aplicado.")
    input("Presiona Enter para volver al menu...")


def guardar_tema():
    """`ExportConfig` escribe el `GRmenu.SetStyle` ACTUAL (el tema que
    hayas dejado aplicado, sea el de este archivo o uno que hayas tocado a
    mano) a un archivo `.gr`. Sin argumentos guardaria al lado de ESTE
    script; aca le pasamos una ruta fija para reusarla en `cargar_tema`.
    """
    ruta = GRmenu.ExportConfig(CONFIG_PATH)
    print(f"Tema actual guardado en {ruta}")
    print("Abrilo con cualquier editor de texto: es un formato propio,")
    print("no YAML ni JSON (usa '::', '<<' y '>>').")
    input("Presiona Enter para volver al menu...")


def cargar_tema():
    """`ImportConfig` aplica un `.gr` ya guardado a `GRmenu.SetStyle`. Si
    el archivo solo define una parte de la configuracion, el resto queda
    como estaba (no resetea nada que el archivo no mencione)."""
    try:
        GRmenu.ImportConfig(CONFIG_PATH)
        print(f"Tema cargado desde {CONFIG_PATH}")
    except FileNotFoundError:
        print(f"Todavia no existe {CONFIG_PATH} -- probá 'Guardar tema actual' primero.")
    except ValueError as e:
        print(f"No se pudo cargar: {e}")
    input("Presiona Enter para volver al menu...")


if __name__ == "__main__":
    # Arranca con el tema "Oceano" (sin print/input: no tiene sentido
    # bloquear el arranque del script pidiendo una tecla). Las opciones
    # del menu, en cambio, usan `tema_oceano`/`tema_incendio` (que si
    # imprimen y esperan Enter, como cualquier otra opcion del menu).
    _aplicar_oceano()

    menu = GRmenu(
        [
            ("Tema 'Oceano'", tema_oceano, "Paleta fria: aqua/blue/cyan"),
            ("Tema 'Incendio'", tema_incendio, "Paleta calida: orange/red/yellow"),
            ("Guardar tema actual", guardar_tema, f"GRmenu.ExportConfig() -> {CONFIG_PATH}"),
            ("Cargar tema guardado", cargar_tema, f"GRmenu.ImportConfig({CONFIG_PATH!r})"),
        ],
        title="Temas",
        banner="THEME",
        subtitle="animate + ExportConfig/ImportConfig",
        style=7,
        banner_style=3,
        font=1,
        center=True,
        animate="diagonal",   # ver tambien "linear", "fade" y "rgb"
    )
    menu.draw()
