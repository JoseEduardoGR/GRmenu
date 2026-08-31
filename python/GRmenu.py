
# ============================================================================
#                    ⚠️  ADVERTENCIA NO TOCAR ESTE BLOQUE  ⚠️
# ============================================================================
#
#   Este codigo fue escrito un martes a las 3:47 AM, con 4 cafes de por
#   medio y sin recordar exactamente que hace `tty.setraw()`.
#
#   Se intento arreglar 6 veces. Las 6 veces empeoro.
#   Se le agrego un try/except "por las dudas". Nadie sabe de que dudas.
#   Se elimino ese try/except en un commit posterior porque "ya no hacia
#   falta". Segun el historial de git, seguia haciendo falta.
#
#   Un colaborador anonimo (coautor sin foto, cuenta fantasma, nadie la
#   vio nunca, nadie la va a ver nunca) lo toco una vez. Andaba peor.
#   Se revirtio ese commit. Sigue sin explicacion por que andaba peor.
#
#   Se probo en Linux: anda.
#   Se probo en macOS: anda, pero nadie sabe por que si es "casi lo mismo
#   pero no realmente" segun el POSIX que le canta a termios en la ducha.
#
#   Windows es, aparte, un horror propio: una API de consola de otro
#   planeta, un `msvcrt.getch()` que devuelve las flechas partidas en dos
#   pedazos como acertijo, y un modo ANSI al que hay que pedirle permiso
#   a `ctypes.windll` para que se digne a existir. Se escribio la rama
#   entera citando la documentacion como quien cita las escrituras.
#   No se probo en una maquina con Windows de verdad. Ni una sola vez.
#   Nadie tiene una a mano. Nadie la quiere tener a mano.
#   Hay fe de que funcione. Es la misma fe de siempre, aplicada a un
#   sistema operativo nuevo.
#
#   Se le pidio a un modelo de lenguaje que lo explique.
#   El modelo de lenguaje tambien reza antes de tocarlo.
#
#   No hay tests unitarios para esto. Hay fe.
#   No hay documentacion tecnica para esto. Hay un README que dice
#   "requiere una terminal real" como quien dice "requiere un milagro".
#
#   Si esto deja de funcionar algun dia, no va a ser por un bug.
#   Va a ser porque alguien, en algun lugar, dejo de creer.
#
#
#   Este codigo funciona gracias a obra divina.
#
# ============================================================================
import argparse
import base64
import inspect
import time
import os
import sys
import json
from typing import Optional, Any

# maldito windows especialito!
if sys.platform == "win32":
    import msvcrt
    import ctypes
else:
    import termios
    import tty

def _enable_windows_ansi():
    if not sys.platform == "win32":
        return
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
    mode = ctypes.c_uint32()
    kernel32.GetConsoleMode(handle, ctypes.byref(mode))
    kernel32.SetConsoleMode(handle, mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING


class GRSubMenu:
    """Lista de opciones anidada, para pasar directo (sin tupla) dentro
    de la lista de `GRmenu`/`GRSubMenu` que la contiene.

    En cuanto la fila que contiene un `GRSubMenu` queda resaltada, su
    panel se dibuja automaticamente a la derecha; flecha derecha (o
    Enter) mueve el foco de flechas/Enter adentro, flecha izquierda lo
    devuelve al panel anterior. No tiene titulo, banner ni subtitulo
    propios, y sus colores se heredan de `GRmenu.SetStyle` (son globales
    a la clase). Su borde tambien se hereda: si no se pasa `style`, usa
    el del panel que lo contiene (en cascada, nivel por nivel).
    """
    MAX_DEPTH = 4  # el menu principal cuenta como nivel 1: menu<sub<sub<sub

    def __init__(self, functions, name, style=None, max_show_options=10, searchable=False):
        self.functions = functions
        self.name = name
        self.style = style  # None = hereda el style resuelto del panel padre
        self.max_show_options = max_show_options  # None = sin limite (muestra todas)
        self.searchable = searchable  # habilita entrar en modo busqueda con "/"
        self.index = 0
        self.scroll = 0  # primera opcion visible, para cuando hay mas de max_show_options
        self.search_active = False
        self.search_query = ""
        # Las marcas de espacio NO se guardan aca: viven en una sola lista
        # global en la raiz (GRmenu._marked), para poder marcar opciones en
        # distintos paneles/niveles y ejecutarlas todas juntas con un Enter.


class GRmenu():
    class GRprint:
        real_print = print

        @staticmethod
        def p(text="",end='\r\n',**extra):
            """Reemplazo interno de `print()` usado por GRmenu.

            Se instala como la funcion global `print` (ver `setFixPrint`) para
            que el salto de linea por defecto sea compatible con la terminal
            en modo TTY crudo, donde `\\n` no vuelve el cursor al inicio de
            la linea.

            Args:
                text: Texto a imprimir (mismo primer argumento que `print`).
                    Por defecto "" (cadena vacia), para poder llamar
                    `print()` sin argumentos igual que la funcion original,
                    por ejemplo para imprimir solo una linea en blanco.
                end: Terminador de linea. Por defecto "\\r\\n" (retorno de
                    carro + salto de linea) en vez del "\\n" habitual, que es
                    lo que necesita el modo raw para verse bien.
                **extra: Cualquier otro argumento que acepte el `print` real
                    de Python (por ejemplo `sep`, `flush`, `file`).
            """
            GRmenu.GRprint.real_print(text, end=end,**extra)

        def setFixPrint():
            """Reemplaza la funcion global `print` por `GRprint.p`.

            Se llama automaticamente desde `GRmenu.__init__`, asi que
            normalmente no hace falta invocarla a mano. Una vez llamada,
            todo `print()` del programa (no solo el de GRmenu) usara
            "\\r\\n" como terminador, algo necesario para que el texto se
            vea correctamente en modo TTY crudo (raw).
            """
            globals()['print'] = GRmenu.GRprint.p

    def __init__(self,functions : list,title="",style=19,banner="",subtitle="",banner_style=3,divider=None,center=True,font=None,max_show_options=10,searchable=False):
        """Crea un nuevo menu interactivo de terminal.

        Pone la terminal en modo TTY crudo (raw) para poder leer las flechas
        y el Enter tecla a tecla, sin esperar un salto de linea, y guarda la
        configuracion original de la terminal (`self.DF`) para poder
        restaurarla al terminar (ver `draw`).

        Args:
            functions: Lista de opciones del menu. Cada elemento puede ser:
                - una funcion/callable: se usa su `__name__` como texto de la
                  opcion.
                - una tupla/lista `(nombre, funcion)`: `nombre` se muestra
                  tal cual y `funcion` es la que se ejecuta al presionar
                  Enter.
                - una tupla/lista `(nombre, funcion, descripcion)`:
                  ademas de lo anterior, `descripcion` se muestra abajo a
                  la derecha del recuadro de opciones mientras esa opcion
                  este seleccionada.
            title: Titulo que se muestra dentro del recuadro de opciones. Si
                queda vacio ("") no se dibuja la fila de titulo.
            style: Numero de estilo de marco de opciones a usar (1 al 20, ver
                `GRmenu.BORDERS()`; ej: 7 = redondeado, 3 = doble linea).
                Por defecto 19 ("●").
            banner: Texto gigante en arte ASCII 3D que se muestra arriba del
                menu (ver `build_ascii_lines`/`draw`). Si queda vacio ("") no
                se dibuja ningun banner.
            subtitle: Subtitulo mostrado debajo del banner y arriba del
                recuadro de opciones. Soporta saltos de linea ("\\n") para
                mostrar varias lineas centradas.
            banner_style: Numero de estilo de marco del banner (1 al 20, ver
                `GRmenu.BORDERS()`; ej: 3 = doble linea). Por defecto 3.
            divider: Si se dibujan lineas divisorias arriba/abajo del
                subtitulo. `None` (por defecto) las activa automaticamente
                solo si hay `banner` o `subtitle`; pasar `True`/`False`
                fuerza el comportamiento.
            center: Si el banner, el subtitulo y el recuadro de opciones se
                centran horizontalmente entre si. Por defecto `True`.
            font: Numero de tipografia ASCII a usar para el `banner` (1 al
                10, ver `build_ascii_lines`; por defecto 1 = "ANSI Shadow
                3D"). Si se pasa, actualiza el estilo global
                (`GRmenu.SetStyle.font`, ver `SetStyle.Font`); si se omite
                (`None`) se respeta el valor ya configurado ahi.
            max_show_options: Maximo de opciones visibles a la vez dentro
                del recuadro. Si hay mas, el recuadro no crece: se ve una
                "ventana" de `max_show_options` filas, y bajar/subir con
                las flechas mas alla del borde de esa ventana la hace
                scrollear para revelar el resto (se muestra un indicador
                tipo "7 de 30", la posicion de la opcion resaltada). `None`
                = sin limite (muestra todas). Por defecto 10.
            searchable: Si `True`, la tecla "/" entra en modo busqueda:
                escribir filtra las opciones por nombre (sin importar
                mayusculas), y mientras se esta escribiendo el resto de
                las teclas (incluidas "t" y "q") se toman como texto de
                busqueda en vez de su funcion normal. "/" o Escape de
                nuevo sale del modo busqueda y vuelve a la lista completa.
                Por defecto `False` (no cambia el comportamiento actual).
        """
        if sys.platform == "win32":
            _enable_windows_ansi()
            self.D = None
            self.DF = None
        else:
            self.D = sys.stdin.fileno()
            self.DF = termios.tcgetattr(self.D)
            tty.setraw(self.D)
            sys.stdout.write("\x1b[?1000h")  # activa reporte de mouse (clicks/rueda)
        sys.stdout.write("\x1b[?25l")  # oculta el cursor mientras el menu esta activo
        sys.stdout.flush()

        self.functions = functions
        self.style = style
        self.GRprint.setFixPrint()
        self.title = title
        self.max_show_options = max_show_options
        self.searchable = searchable
        self.index = 0
        self.scroll = 0
        self.search_active = False
        self.search_query = ""
        # Lista GLOBAL de opciones marcadas con espacio, como pares
        # (node, indice), en el orden en que se marcaron. Es global (vive
        # aca, en la raiz) y no por panel, para poder marcar opciones en
        # distintos GRSubMenu/niveles y que Enter las ejecute todas juntas
        # sin importar en que panel este el foco en ese momento.
        self._marked = []
        self._preview = False
        # Cadena de paneles actualmente "entrados" (via flecha derecha o
        # Enter sobre una fila con un GRSubMenu): self siempre es el nivel
        # 0. self._focus indica cual de estos paneles recibe flechas/Enter.
        self._chain = [self]
        self._focus = 0
        self._clear_seq = "\x1b[H\x1b[2J\x1b[3J"
        self._image_shown = False
        self.banner = banner
        self.subtitle = subtitle
        self.banner_style = banner_style
        self.divider = divider if divider is not None else bool(banner or subtitle)
        self.center = center
        if font is not None:
            GRmenu.SetStyle.Font(font)

    def _up(self):
        node = self._chain[self._focus]
        filtered = self._filtered_indices(node)
        if not filtered:
            return
        pos = filtered.index(node.index) if node.index in filtered else 0
        node.index = filtered[(pos - 1) % len(filtered)]
        self._clamp_scroll(node, filtered)

    def _down(self):
        node = self._chain[self._focus]
        filtered = self._filtered_indices(node)
        if not filtered:
            return
        pos = filtered.index(node.index) if node.index in filtered else 0
        node.index = filtered[(pos + 1) % len(filtered)]
        self._clamp_scroll(node, filtered)

    @staticmethod
    def _filtered_indices(node):
        """Indices (en node.functions) que pasan el filtro de busqueda de
        node, en orden. Sin busqueda activa (o sin query) devuelve todos:
        la navegacion/scroll/render usan esto siempre, asi que cuando no
        hay busqueda se comportan exactamente igual que antes."""
        if not getattr(node, "search_active", False):
            return list(range(len(node.functions)))
        query = getattr(node, "search_query", "").strip().lower()
        if not query:
            return list(range(len(node.functions)))
        return [i for i, f in enumerate(node.functions) if query in GRmenu._name(f).lower()]

    @staticmethod
    def _clamp_scroll(node, filtered):
        """Mueve node.scroll (primera opcion visible, como posicion DENTRO
        de `filtered`) lo justo para que node.index quede dentro de la
        ventana de node.max_show_options, tanto si el indice avanzo,
        retrocedio, dio la vuelta (wrap), o `filtered` cambio de tamaño
        (por busqueda)."""
        limit = getattr(node, "max_show_options", None)
        total = len(filtered)
        if not limit or limit >= total:
            node.scroll = 0
            return
        pos = filtered.index(node.index) if node.index in filtered else 0
        if pos < node.scroll:
            node.scroll = pos
        elif pos >= node.scroll + limit:
            node.scroll = pos - limit + 1
        node.scroll = max(0, min(node.scroll, total - limit))


    _colors_cache = None

    @staticmethod
    def COLORS() -> dict:
        """Carga (y cachea) la paleta de colores ANSI disponible.

        Los colores se leen una sola vez desde `data/colors.json` (misma
        fuente que usan las versiones de Ruby y C++) y se guardan en
        `GRmenu._colors_cache` para no volver a leer el archivo en llamadas
        posteriores.

        Returns:
            dict: cada clave es el nombre de un color ("red", "green",
                "cyan", etc.) y su valor es otro dict que mapea el nivel de
                intensidad (1 = normal, 2 = brillante) a la secuencia de
                escape ANSI ya armada (con el prefijo "\\x1b["). La clave
                especial "reset" contiene la secuencia para volver al color
                por defecto de la terminal.
        """
        if GRmenu._colors_cache is None:
            with open(GRmenu._data_path("colors.json"), encoding="utf-8") as fh:
                raw = json.load(fh)
            GRmenu._colors_cache = {
                name: ({level: f"\x1b[{code}" for level, code in codes.items()} if isinstance(codes, dict) else f"\x1b[{codes}")
                for name, codes in raw.items()
            }
        return GRmenu._colors_cache

    _borders_cache = None

    @staticmethod
    def BORDERS() -> dict:
        """Carga (y cachea) las definiciones de borde disponibles.

        Se leen una sola vez desde `data/borders.json` y se guardan en
        `GRmenu._borders_cache` para no volver a leer el archivo en llamadas
        posteriores.

        Returns:
            dict: cada clave es el numero de estilo como string (por ejemplo
                "3") y su valor es un dict con las piezas para dibujar el
                recuadro:
                    h  -> caracter(es) para las lineas horizontales
                    v  -> caracter para las lineas verticales
                    tl -> esquina superior izquierda
                    tr -> esquina superior derecha
                    bl -> esquina inferior izquierda
                    br -> esquina inferior derecha
                Un estilo "simple" (mismo caracter en todo el recuadro, sin
                esquinas distintas) se puede escribir en `borders.json` como
                un string suelto en vez del dict completo (ej. `"9": "▓"`);
                aca se expande a las 6 claves de arriba, todas con ese mismo
                caracter.
        """
        if GRmenu._borders_cache is None:
            with open(GRmenu._data_path("borders.json"), encoding="utf-8") as fh:
                raw = json.load(fh)
            GRmenu._borders_cache = {
                style: (value if isinstance(value, dict) else dict.fromkeys(("h", "v", "tl", "tr", "bl", "br"), value))
                for style, value in raw.items()
            }
        return GRmenu._borders_cache
    
    class SetStyle:
        border = {"color": "cyan", "level": 1}
        options = {"color": "white", "level": 1}
        focus = {"color": "green", "level": 2}
        title = {"color": "yellow", "level": 2}
        banner = {"color": "magenta", "level": 2}
        subtitle = {"color": "cyan", "level": 2}
        divider = {"color": "blue", "level": 1}
        description = {"color": "gray", "level": 1}
        font = 1
        welcome = {"text": None, "image": None, "width": None, "height": None}

        @staticmethod
        def Border(color, level=1):
            """Define el color usado para dibujar el recuadro del menu.

            Args:
                color: Nombre del color a usar. Debe existir como clave en
                    `GRmenu.COLORS()` (por ejemplo "cyan", "red", "green",
                    "magenta", "white", "gray", "purple", "pink", "aqua",
                    "orange"). Un nombre invalido hace que `_colorize` no
                    aplique color y el texto se imprima sin formato.
                level: Intensidad del color: 1 para el tono normal, 2 para
                    el tono brillante. Por defecto 1.
            """
            GRmenu.SetStyle.border = {"color": color, "level": level}

        @staticmethod
        def Options(color, level=1):
            """Define el color de las opciones del menu que NO estan seleccionadas.

            Args:
                color: Nombre del color a usar (debe existir en
                    `GRmenu.COLORS()`, ver `Border` para la lista completa).
                level: Intensidad del color: 1 para el tono normal, 2 para
                    el tono brillante. Por defecto 1.
            """
            GRmenu.SetStyle.options = {"color": color, "level": level}

        @staticmethod
        def Focus(color, level=2):
            """Define el color de la opcion actualmente seleccionada (resaltada).

            Args:
                color: Nombre del color a usar (debe existir en
                    `GRmenu.COLORS()`, ver `Border` para la lista completa).
                level: Intensidad del color: 1 para el tono normal, 2 para
                    el tono brillante. Por defecto 2 (brillante).
            """
            GRmenu.SetStyle.focus = {"color": color, "level": level}

        @staticmethod
        def Title(color, level=2):
            """Define el color del titulo mostrado dentro del recuadro de opciones.

            Args:
                color: Nombre del color a usar (debe existir en
                    `GRmenu.COLORS()`, ver `Border` para la lista completa).
                level: Intensidad del color: 1 para el tono normal, 2 para
                    el tono brillante. Por defecto 2 (brillante).
            """
            GRmenu.SetStyle.title = {"color": color, "level": level}

        @staticmethod
        def Banner(color, level=2):
            """Define el color del texto y el marco del banner ASCII 3D.

            Args:
                color: Nombre del color a usar (debe existir en
                    `GRmenu.COLORS()`, ver `Border` para la lista completa).
                level: Intensidad del color: 1 para el tono normal, 2 para
                    el tono brillante. Por defecto 2 (brillante).
            """
            GRmenu.SetStyle.banner = {"color": color, "level": level}

        @staticmethod
        def Subtitle(color, level=2):
            """Define el color del subtitulo mostrado debajo del banner.

            Args:
                color: Nombre del color a usar (debe existir en
                    `GRmenu.COLORS()`, ver `Border` para la lista completa).
                level: Intensidad del color: 1 para el tono normal, 2 para
                    el tono brillante. Por defecto 2 (brillante).
            """
            GRmenu.SetStyle.subtitle = {"color": color, "level": level}

        @staticmethod
        def Divider(color, level=1):
            """Define el color de las lineas divisorias que rodean al subtitulo.

            Args:
                color: Nombre del color a usar (debe existir en
                    `GRmenu.COLORS()`, ver `Border` para la lista completa).
                level: Intensidad del color: 1 para el tono normal, 2 para
                    el tono brillante. Por defecto 1.
            """
            GRmenu.SetStyle.divider = {"color": color, "level": level}

        @staticmethod
        def Description(color, level=1):
            """Define el color de la descripcion de la opcion seleccionada.

            Args:
                color: Nombre del color a usar (debe existir en
                    `GRmenu.COLORS()`, ver `Border` para la lista completa).
                level: Intensidad del color: 1 para el tono normal, 2 para
                    el tono brillante. Por defecto 1.
            """
            GRmenu.SetStyle.description = {"color": color, "level": level}

        @staticmethod
        def Font(font_id):
            """Define la tipografia ASCII 3D global usada para dibujar el banner.

            Args:
                font_id: Numero de tipografia a usar (1 al 10, ver
                    `build_ascii_lines` y `data/fonts.json`; por defecto 1 =
                    "ANSI Shadow 3D"). Se convierte a `int` antes de
                    guardarlo.
            """
            GRmenu.SetStyle.font = int(font_id)

        @staticmethod
        def Welcome(text=None, image=None, width=None, height=None):
            """Define el contenido de la pantalla de bienvenida (`GRmenu.welcome`).

            Si no se llama a este metodo (o se llama sin argumentos), la
            bienvenida por defecto es el logo de GRmenu: la imagen real
            (`assets/logo.png`) si la terminal la soporta, o su version en
            ASCII (generada con `build_ascii_lines`) si no.

            Args:
                text: Texto o logo ASCII a imprimir en la pantalla de
                    bienvenida. Si tambien se paso `image`, funciona como
                    respaldo: se usa cuando la terminal NO soporta imagenes
                    embebidas, en vez de `image`.
                image: Ruta a un archivo de imagen (PNG/JPEG/GIF) para
                    mostrar en la pantalla de bienvenida. Se muestra
                    embebida en la terminal si esta soporta el protocolo
                    de imagenes de iTerm2 o Kitty (ver `GRmenu._image_protocol`);
                    si no lo soporta, se usa `text` como respaldo si se
                    paso, o se imprime un aviso si no.
                width: Ancho de la imagen en columnas de terminal. Si se
                    omite (`None`), se usa 40 columnas por defecto para
                    evitar que la imagen se vea gigante. Sin efecto si no
                    se paso `image`.
                height: Alto de la imagen en filas de terminal. Si se
                    omite (`None`) junto con `width`, la terminal calcula
                    el alto sola para mantener la proporcion de la imagen.
            """
            GRmenu.SetStyle.welcome = {
                "text": text, "image": image, "width": width, "height": height,
            }

    @staticmethod
    def _colorize(text, color_cfg):
        if not color_cfg:
            return text
        colors = GRmenu.COLORS()
        code = colors.get(color_cfg["color"], {}).get(str(color_cfg["level"]), "")
        if not code:
            return text
        return f"{code}{text}{colors['reset']}"

    @staticmethod
    def _hline(h, width):
        return (h * (width // len(h) + 1))[:width]

    @staticmethod
    def _data_path(filename) -> str:
        here = os.path.dirname(__file__)
        local = os.path.join(here, "data", filename)
        if os.path.exists(local):
            return local
        return os.path.join(here, "..", "data", filename)

    @staticmethod
    def _asset_path(filename) -> str:
        return os.path.join(os.path.dirname(__file__), "assets", filename)

    # Version en ASCII, hardcodeada a mano, del logo por defecto de GRmenu
    # (icono hexagonal + wordmark "GR code"), usada como pantalla de
    # bienvenida cuando la terminal no soporta imagenes embebidas. Colores
    # fijos (blanco/azul) en vez de pasar por SetStyle, para que se vea
    # igual que el logo real sin depender de la paleta configurada.
    _DEFAULT_LOGO_ASCII = (
        "                             \x1b[94m     _____________\x1b[0m\n"
        "                             \x1b[94m    /             \\\x1b[0m\n"
        "                             \x1b[94m   /      ___      \\\x1b[0m\n"
        "                             \x1b[94m  /      /   \\      \\\x1b[0m\n"
        "                             \x1b[94m /      /     \\      \\\x1b[0m\n"
        "                             \x1b[94m \\      \\     /      /\x1b[0m\n"
        "                             \x1b[94m  \\      \\   /      /\x1b[0m\n"
        "                             \x1b[94m   \\               /\x1b[0m\n"
        "                             \x1b[94m    \\             /\x1b[0m\n"
        "                             \x1b[94m     _____________\x1b[0m\n"
        "\n"
        "\x1b[97m  ██████╗     ██████╗   \x1b[94m    ██████╗      ██████╗     ██████╗      ███████╗  \x1b[0m\n"
        "\x1b[97m ██╔════╝     ██╔══██╗  \x1b[94m   ██╔════╝     ██╔═══██╗    ██╔══██╗     ██╔════╝  \x1b[0m\n"
        "\x1b[97m ██║  ███╗    ██████╔╝  \x1b[94m   ██║          ██║   ██║    ██║  ██║     █████╗    \x1b[0m\n"
        "\x1b[97m ██║   ██║    ██╔══██╗  \x1b[94m   ██║          ██║   ██║    ██║  ██║     ██╔══╝    \x1b[0m\n"
        "\x1b[97m ╚██████╔╝    ██║  ██║  \x1b[94m   ╚██████╗     ╚██████╔╝    ██████╔╝     ███████╗  \x1b[0m\n"
        "\x1b[97m  ╚═════╝     ╚═╝  ╚═╝  \x1b[94m    ╚═════╝      ╚═════╝     ╚═════╝      ╚══════╝  \x1b[0m"
    )

    _fonts_cache = None

    @staticmethod
    def _fonts() -> dict:
        if GRmenu._fonts_cache is None:
            with open(GRmenu._data_path("fonts.json"), encoding="utf-8") as fh:
                GRmenu._fonts_cache = json.load(fh)
        return GRmenu._fonts_cache

    @staticmethod
    def build_ascii_lines(text, max_cols, font_id=1) -> Optional[list]:
        """Convierte un texto en lineas de arte ASCII usando una tipografia de `data/fonts.json`.

        Prueba distintos espaciados entre caracteres (2, luego 1, luego 0
        espacios) y se queda con el mas ancho que todavia entre en
        `max_cols` columnas, dejando 6 columnas de margen para el borde.

        Args:
            text: Texto a convertir. Se pasa a mayusculas y se descartan los
                caracteres que no existan en la tipografia elegida (por
                ejemplo, letras acentuadas o simbolos no definidos).
            max_cols: Ancho maximo disponible, en columnas de terminal, para
                el resultado (normalmente `os.get_terminal_size().columns`).
            font_id: Numero de tipografia a usar, tal como esta definida en
                `data/fonts.json`. Por defecto 1.

        Returns:
            Optional[list]: lista de strings, una por cada fila del arte
                ASCII (todas del mismo alto), o `None` si ningun caracter de
                `text` existe en la tipografia, o si ni siquiera con
                espaciado 0 el resultado entra en `max_cols`.
        """
        glyphs = GRmenu._fonts().get(str(font_id), GRmenu._fonts()["1"])
        chars = [c for c in str(text).upper() if c in glyphs]
        if not chars:
            return None
        height = len(next(iter(glyphs.values())))
        for spacing in [2, 1, 0]:
            lines = [""] * height
            for i, c in enumerate(chars):
                pad = "" if i == len(chars) - 1 else " " * spacing
                for row in range(height):
                    lines[row] += glyphs[c][row] + pad
            if max(len(l) for l in lines) + 6 <= max_cols:
                return lines
        return None

    @staticmethod
    def banner(text, delay=0, color="magenta", level=2, style=3, font=1) -> None:
        """Imprime un banner decorado directamente en la terminal.

        Si `text` se puede representar con la tipografia ASCII indicada en
        `font` (ver `build_ascii_lines`) y entra en el ancho de la terminal,
        se dibuja como letras grandes dentro de un recuadro. Si no entra (o
        ningun caracter tiene glifo), se dibuja como una sola linea de texto
        centrada dentro del recuadro.

        Args:
            text: Texto del banner.
            delay: Segundos de pausa entre cada fila del arte ASCII, para un
                efecto de "dibujado" progresivo. 0 = sin pausa (por
                defecto). No tiene efecto si el texto se imprime como linea
                simple.
            color: Nombre del color del recuadro y del texto (debe existir
                en `GRmenu.COLORS()`).
            level: Intensidad del color (1 normal, 2 brillante). Por
                defecto 2.
            style: Estilo de borde a usar (ver `GRmenu.BORDERS()`). Por
                defecto 3 ("╔").
            font: Tipografia ASCII a usar (ver `build_ascii_lines`). Por
                defecto 1.
        """
        cols = GRmenu._term_width()
        cfg = {"color": color, "level": level}
        b = GRmenu.BORDERS().get(str(style), GRmenu.BORDERS()["3"])
        rows = GRmenu.build_ascii_lines(text, cols, font)
        if rows:
            width = max(len(r) for r in rows) + 4
            hline = GRmenu._hline(b["h"], width)
            print(GRmenu._colorize(b["tl"] + hline + b["tr"], cfg))
            for r in rows:
                print(GRmenu._colorize(f"{b['v']}  {r}  {b['v']}", cfg))
                if delay > 0:
                    time.sleep(delay)
            print(GRmenu._colorize(b["bl"] + hline + b["br"], cfg))
        else:
            text = str(text).strip()
            width = min(len(text) + 4, cols - 4)
            hline = GRmenu._hline(b["h"], width)
            print(GRmenu._colorize(b["tl"] + hline + b["tr"], cfg))
            print(GRmenu._colorize(f"{b['v']} {text.center(width)} {b['v']}", cfg))
            print(GRmenu._colorize(b["bl"] + hline + b["br"], cfg))

    @staticmethod
    def _name(f) -> str:
        if isinstance(f, GRSubMenu):
            return str(f.name)
        if isinstance(f, (list, tuple)):
            return str(f[0])
        name = getattr(f, "__name__", "opcion")
        return "Lambda" if name == "<lambda>" else name.replace("_", " ").title()

    @staticmethod
    def _call(f) -> Any:
        return f[1]() if isinstance(f, (list, tuple)) else f()

    @staticmethod
    def _description(f) -> str:
        return str(f[2]) if isinstance(f, (list, tuple)) and len(f) > 2 else ""

    @staticmethod
    def _source(f, max_lines=20) -> list:
        if isinstance(f, GRSubMenu):
            return ["(esto es un submenu, no tiene codigo fuente)"]
        func = f[1] if isinstance(f, (list, tuple)) else f
        try:
            lines = [ln.rstrip("\n") for ln in inspect.getsource(func).splitlines()]
        except (OSError, TypeError):
            return ["(no se pudo obtener el codigo fuente)"]
        if len(lines) > max_lines:
            lines = lines[:max_lines] + [f"... (+{len(lines) - max_lines} lineas)"]
        return lines or ["(sin contenido)"]

    @staticmethod
    def _image_protocol() -> Optional[str]:
        """Detecta si la terminal soporta mostrar imagenes embebidas.

        Se basa unicamente en variables de entorno (no hay forma portable
        de consultarle al terminal si soporta un protocolo sin bloquear
        esperando una respuesta), asi que es una deteccion best-effort:
        cubre iTerm2, WezTerm (protocolo de iTerm2) y Kitty (o cualquier
        terminal que herede su `TERM`/`KITTY_WINDOW_ID`, como Konsole).

        Returns:
            Optional[str]: "kitty", "iterm2", o `None` si no se detecto
                soporte.
        """
        if "KITTY_WINDOW_ID" in os.environ or os.environ.get("TERM") == "xterm-kitty":
            return "kitty"
        if os.environ.get("TERM_PROGRAM") in ("iTerm.app", "WezTerm"):
            return "iterm2"
        return None

    @staticmethod
    def _show_image(path, width=None, height=None) -> None:
        """Imprime un archivo de imagen embebido en la terminal.

        Envia los bytes crudos del archivo (sin decodificar ni redimensionar,
        para no depender de librerias externas como Pillow) codificados en
        base64 dentro de la secuencia de escape del protocolo detectado por
        `_image_protocol`. La terminal es la que decodifica, redimensiona y
        dibuja la imagen.

        Args:
            path: Ruta al archivo de imagen (PNG/JPEG/GIF) a mostrar.
            width: Ancho de la imagen en columnas de terminal. `None` deja
                que la terminal calcule un ancho por defecto (que suele ser
                el tamano nativo de la imagen, potencialmente enorme).
            height: Alto de la imagen en filas de terminal. Si se omite
                junto con `width`, la terminal preserva la proporcion.
        """
        protocol = GRmenu._image_protocol()
        with open(path, "rb") as fh:
            data = fh.read()
        b64 = base64.b64encode(data).decode("ascii")
        if protocol == "kitty":
            size = ""
            if width is not None:
                size += f",c={int(width)}"
            if height is not None:
                size += f",r={int(height)}"
            chunk_size = 4096
            chunks = [b64[i:i + chunk_size] for i in range(0, len(b64), chunk_size)] or [""]
            for i, chunk in enumerate(chunks):
                more = 1 if i < len(chunks) - 1 else 0
                header = f"a=T,f=100{size},m={more}" if i == 0 else f"m={more}"
                sys.stdout.write(f"\x1b_G{header};{chunk}\x1b\\")
            sys.stdout.write("\n")
        else:
            size = ""
            if width is not None:
                size += f";width={int(width)}"
            if height is not None:
                size += f";height={int(height)}"
            sys.stdout.write(f"\x1b]1337;File=inline=1;size={len(data)}{size}:{b64}\a\n")
        sys.stdout.flush()

    def welcome(self) -> None:
        """Pantalla de bienvenida mostrada antes de dibujar el menu por primera vez.

        Se llama una unica vez al comienzo de `draw()`, antes de leer la
        primera tecla. Su contenido se configura con `SetStyle.Welcome`:

            - Si se configuro `image` y la terminal soporta imagenes
              embebidas (ver `_image_protocol`), se muestra esa imagen.
            - Si se configuro `image` pero la terminal NO las soporta, se
              usa `text` como respaldo si se paso; si no, se imprime un
              aviso.
            - Si no se configuro `image` (pero si `text`), se imprime
              `text` directamente (por ejemplo, un logo en ASCII).
            - Si no se configuro ni `image` ni `text`, se usa el logo por
              defecto de GRmenu (imagen real o su version ASCII, ver
              `SetStyle.Welcome`).

        Pensado para ser sobreescrito (override) en una subclase si se
        quiere una pantalla de bienvenida totalmente distinta.

        Limpia la pantalla antes de dibujar, para que cualquier cosa
        impresa antes de crear el menu (por ejemplo un `GRmenu.banner()`
        suelto) no quede pegada arriba del logo o del texto.
        """
        print(self._clear_seq, end="")
        w = GRmenu.SetStyle.welcome
        image, text = w["image"], w["text"]
        if image is None and text is None:
            image = GRmenu._asset_path("logo.png")
            text = GRmenu._DEFAULT_LOGO_ASCII
        if image:
            if GRmenu._image_protocol():
                width = w["width"]
                height = w["height"]
                if width is None and height is None:
                    width = 40
                GRmenu._show_image(image, width, height)
                self._image_shown = True
            elif text:
                for line in text.splitlines():
                    print(line)
            else:
                print("Esta terminal no soporta imagenes")
        elif text:
            for line in text.splitlines():
                print(line)
        else:
            print("Press any key to start ...")

    @staticmethod
    def _read_key(fd):
        if sys.platform ==  "win32":
            ch = msvcrt.getch()
            if ch in (b'\x00', b'\xe0'):          # prefijo de tecla especial
                ch2 = msvcrt.getch()
                return {b'H': b'\x1b[A', b'P': b'\x1b[B',
                        b'K': b'\x1b[D', b'M': b'\x1b[C'}.get(ch2, ch2)
            return ch
        data = os.read(fd, 3)
        if data == b'\x1b[M':
            cb, cx, cy = os.read(fd, 3)
            if cb == 96: return b'\x1b[A'   # rueda arriba = flecha arriba
            if cb == 97: return b'\x1b[B'   # rueda abajo = flecha abajo
            return b''                       
        return data


    def draw(self,size_max=20):
        """Dibuja el menu y arranca el loop de lectura de teclado.

        Muestra las opciones (`self.functions`) dentro de un recuadro,
        resalta la opcion actualmente seleccionada, y queda esperando
        teclas:
            - Flecha arriba / abajo: mueve la seleccion dentro del panel
              que tiene el foco.
            - Flecha derecha o Enter sobre una fila que contiene un
              `GRSubMenu`: entra a su panel, que se dibuja a la derecha (le
              pasa el foco de flechas/Enter); flecha izquierda vuelve al
              panel anterior. Hasta `GRSubMenu.MAX_DEPTH` niveles anidados.
            - Enter sobre una opcion normal: restaura la configuracion
              original de la terminal, ejecuta la opcion y termina el loop
              (sea cual sea el panel/nivel donde este el foco).
            - "t": muestra el codigo fuente de la funcion de la opcion
              resaltada en el panel con foco (via `inspect.getsource`);
              flechas y Enter quedan deshabilitados mientras se ve el
              preview. Presionar "t" de nuevo vuelve al menu de opciones.
            - "/" (si el panel con foco tiene `searchable=True`): entra en
              modo busqueda, filtra las opciones por nombre a medida que
              se escribe (mientras tanto "t"/"q" son solo letras, no su
              funcion normal). "/" o Escape de nuevo sale y vuelve a la
              lista completa.
            - Espacio (fuera del modo busqueda): marca/desmarca la opcion
              resaltada con "[x]" (no funciona sobre un `GRSubMenu`). Las
              marcas son globales a todo el menu, no solo al panel actual:
              se puede marcar algo en un `GRSubMenu`, volver con flecha
              izquierda y marcar mas en otro panel/nivel. Con una o mas
              opciones marcadas (de cualquier panel), Enter las ejecuta
              TODAS en el orden en que se marcaron (en vez de solo la
              resaltada) y termina el loop igual que con una sola opcion.
            - "q" o Ctrl+C: sale del menu sin ejecutar ninguna opcion (con
              busqueda activa, "q" es parte del texto: usar Ctrl+C o
              salir de la busqueda primero).

        Args:
            size_max: Ancho minimo (en caracteres) del recuadro del menu,
                usado aunque el texto de las opciones sea mas corto. Por
                defecto 20.
        """
        self.welcome()
        try:
            self._draw_loop(size_max)
        finally:
            if not sys.platform == "win32":
                termios.tcsetattr(self.D, termios.TCSAFLUSH, self.DF)
                sys.stdout.write("\x1b[?1000l")  # desactiva reporte de mouse
            sys.stdout.write("\x1b[?25h")  # muestra de nuevo el cursor
            sys.stdout.flush()

    @staticmethod
    def _delete_shown_images() -> None:
        """Borra las imagenes que sigan dibujadas via el protocolo de Kitty.

        El clear de pantalla normal (`_clear_seq`, secuencias ANSI de
        limpiar texto) no afecta a las imagenes dibujadas con el protocolo
        grafico de Kitty: quedan como una capa aparte hasta que se borran
        explicitamente con esta secuencia (`a=d,d=A` = borrar todas). Sin
        esto, el logo mostrado en `welcome()` seguiria visible por debajo
        del primer menu que se dibuja despues.
        """
        sys.stdout.write("\x1b_Ga=d,d=A\x1b\\")
        sys.stdout.flush()

    def _render_option_panel(self, node, size_max, style, focused):
        """Devuelve (ancho, lineas ya coloreadas) del panel de opciones de
        `node` (self o un GRSubMenu). Cada linea ya incluye sus dos bordes
        verticales; no incluye el padding horizontal externo (eso lo pone
        quien componga varios paneles uno al lado del otro en _draw_loop).

        `focused` indica si ESTE panel es el que recibe flechas/Enter en
        este momento: solo puede haber un foco a la vez en toda la
        pantalla, asi que solo su fila resaltada se pinta con el color de
        foco (indicando que funcion ejecutaria Enter). Los demas paneles
        (los que llevaron hasta el panel con foco, o el preview de lo que
        hay un nivel mas adentro) muestran la misma flechita de cursor,
        pero sin colorear, para no sugerir que ahi tambien hay foco.
        """
        names = [self._name(f) for f in node.functions]
        title = getattr(node, "title", "")
        box_border = self.BORDERS().get(str(style))
        bc, oc, fc, tc, dc = self.SetStyle.border, self.SetStyle.options, self.SetStyle.focus, self.SetStyle.title, self.SetStyle.description
        searching = getattr(node, "search_active", False)
        query = getattr(node, "search_query", "") if searching else ""
        search_row = f"Buscar: {query}_" if searching else ""
        marked = [i for n, i in self._marked if n is node]  # solo las de ESTE panel

        # +8 = margen que consume la fila de opcion mas ancha posible
        # ("│ [x] " + nombre + " │", el formato de una fila marcada con
        # foco): con +6 (solo el "│ > " normal) una fila que se marca con
        # espacio se podia pasar del ancho del recuadro.
        width = max(
            [size_max] + [len(n) + 8 for n in names]
            + ([len(title) + 4] if title else [])
            + ([len(search_row) + 4] if search_row else [])
        )

        filtered = self._filtered_indices(node)
        limit = getattr(node, "max_show_options", None)
        total = len(filtered)
        truncated = bool(limit) and limit < total
        window = filtered[node.scroll:node.scroll + limit] if truncated else filtered
        visible = [(i, names[i]) for i in window]

        lines = []
        if box_border:
            b = box_border
            line = self._hline(b["h"], width - 2)
            v = self._colorize(b["v"], bc)
            lines.append(self._colorize(b["tl"] + line + b["tr"], bc))
            if title:
                lines.append(f"{v} {self._colorize(title.center(width - 4), tc)} {v}")
                lines.append(self._colorize(b["v"] + line + b["v"], bc))
            if searching:
                lines.append(f"{v} {self._colorize(search_row.ljust(width - 4), dc)} {v}")
                lines.append(self._colorize(b["v"] + line + b["v"], bc))
            if not visible:
                lines.append(f"{v} {self._colorize('(sin coincidencias)'.ljust(width - 4), oc)} {v}")
            for i, name in visible:
                if i in marked:
                    color = (fc if focused else oc) if node.index == i else oc
                    option = self._colorize(f"[x] {name.ljust(width - 8)}", color)
                    lines.append(f"{v} {option} {v}")
                elif node.index == i:
                    option = self._colorize(f">{name.ljust(width - 6)}", fc if focused else oc)
                    lines.append(f"{v}  {option} {v}")
                else:
                    option = self._colorize(f"> {name.ljust(width - 6)}", oc)
                    lines.append(f"{v} {option} {v}")
            lines.append(self._colorize(b["bl"] + line + b["br"], bc))
        else:
            symbol = "#"
            border = self._colorize(symbol, bc)
            lines.append(self._colorize(symbol * width, bc))
            if title:
                lines.append(f"{border} {self._colorize(title.center(width - 4), tc)} {border}")
                lines.append(self._colorize(symbol * width, bc))
            if searching:
                lines.append(f"{border} {self._colorize(search_row.ljust(width - 4), dc)} {border}")
                lines.append(self._colorize(symbol * width, bc))
            if not visible:
                lines.append(f"{border} {self._colorize('(sin coincidencias)'.ljust(width - 4), oc)} {border}")
            for i, name in visible:
                color = (fc if focused else oc) if node.index == i else oc
                content = f"[x] {name}" if i in marked else name
                lines.append(f"{border} {self._colorize(content.ljust(width - 4), color)} {border}")
            lines.append(self._colorize(symbol * width, bc))

        if truncated:
            pos = filtered.index(node.index) + 1 if node.index in filtered else 0
            lines.append(self._colorize(f"{pos} de {total}".rjust(width), dc))

        if marked:
            plural = "s" if len(marked) != 1 else ""
            lines.append(self._colorize(f"{len(marked)} marcada{plural}".rjust(width), dc))

        desc = self._description(node.functions[node.index])
        if desc:
            lines.append(self._colorize(desc.rjust(width), dc))
        return width, lines

    def _render_source_panel(self, node, size_max, style, cols):
        """Igual que `_render_option_panel`, pero en vez de la lista de
        opciones muestra el codigo fuente de la opcion resaltada de `node`
        (activado con "t", ver `_draw_loop`)."""
        names = [self._name(f) for f in node.functions]
        box_border = self.BORDERS().get(str(style))
        bc, oc, tc = self.SetStyle.border, self.SetStyle.options, self.SetStyle.title
        src = self._source(node.functions[node.index])
        title = f"Preview: {names[node.index]}"
        width = min(max([size_max] + [len(l) + 4 for l in src] + [len(title) + 4]), cols - 4)

        lines = []
        if box_border:
            b = box_border
            line = self._hline(b["h"], width - 2)
            v = self._colorize(b["v"], bc)
            lines.append(self._colorize(b["tl"] + line + b["tr"], bc))
            lines.append(f"{v} {self._colorize(title.center(width - 4), tc)} {v}")
            lines.append(self._colorize(b["v"] + line + b["v"], bc))
            for ln in src:
                lines.append(f"{v} {self._colorize(ln[:width - 4].ljust(width - 4), oc)} {v}")
            lines.append(self._colorize(b["bl"] + line + b["br"], bc))
        else:
            symbol = "#"
            border = self._colorize(symbol, bc)
            lines.append(self._colorize(symbol * width, bc))
            lines.append(f"{border} {self._colorize(title.center(width - 4), tc)} {border}")
            lines.append(self._colorize(symbol * width, bc))
            for ln in src:
                lines.append(f"{border} {self._colorize(ln[:width - 4].ljust(width - 4), oc)} {border}")
            lines.append(self._colorize(symbol * width, bc))
        lines.append(self._colorize("'t' para volver al menu".rjust(width), self.SetStyle.description))
        return width, lines

    def _draw_loop(self, size_max):
        # tty.setraw() apaga ISIG, asi que Ctrl+C no llega como SIGINT sino
        # como el byte \x03 leido normalmente: hay que salir a mano igual
        # que con "q", si no el modo raw queda pegado hasta romper con kill.
        while True:
            key = self._read_key(self.D)
            focus_node = self._chain[self._focus]
            searching = focus_node.search_active

            # "q" quita el menu, salvo mientras se esta escribiendo una
            # busqueda (ahi "q" es una letra mas del texto). Ctrl+C
            # siempre sale, sea cual sea el modo.
            if key == b'\x03' or (key == b'q' and not searching):
                break

            if self._image_shown:
                if GRmenu._image_protocol() == "kitty":
                    self._delete_shown_images()
                self._image_shown = False
            print(self._clear_seq, end="")

            if searching:
                # En modo busqueda cualquier tecla imprimible (incluidas
                # "t"/"q") se toma como texto, no como su funcion normal.
                if key in (b'/', b'\x1b'):
                    focus_node.search_active = False
                    focus_node.search_query = ""
                    searching = False
                elif key in (b'\x7f', b'\x08'):
                    focus_node.search_query = focus_node.search_query[:-1]
                elif len(key) == 1 and 32 <= key[0] <= 126:
                    focus_node.search_query += key.decode("ascii", "ignore")
                if searching:
                    filtered = self._filtered_indices(focus_node)
                    if filtered and focus_node.index not in filtered:
                        focus_node.index = filtered[0]
                    self._clamp_scroll(focus_node, filtered)
            else:
                if key == b'/' and focus_node.searchable and not self._preview:
                    focus_node.search_active = True
                    focus_node.search_query = ""
                elif key == b't':
                    self._preview = not self._preview
                elif key == b' ' and not self._preview:
                    row = focus_node.functions[focus_node.index]
                    if not isinstance(row, GRSubMenu):
                        pair = (focus_node, focus_node.index)
                        if pair in self._marked:
                            self._marked.remove(pair)
                        else:
                            self._marked.append(pair)

            if not self._preview:
                self._up() if key==b'\x1b[A' else None # up
                self._down() if key==b'\x1b[B' else None # down

            # fila resaltada en el panel con foco ANTES de procesar flecha
            # derecha/izquierda/Enter (que pueden cambiar self._chain).
            focus_node = self._chain[self._focus]
            focus_row = focus_node.functions[focus_node.index]

            if not self._preview:
                if key in (b'\x1b[C', b'\r') and isinstance(focus_row, GRSubMenu) \
                        and len(self._chain) < GRSubMenu.MAX_DEPTH:
                    # Derecha o Enter sobre un GRSubMenu SIEMPRE entra a su
                    # panel, sin importar si hay opciones marcadas en otra
                    # fila de este mismo nivel (una fila de GRSubMenu nunca
                    # se puede marcar, asi que no hay ambiguedad real: solo
                    # Enter sobre una opcion normal puede "competir" con las
                    # marcadas, y eso se resuelve mas abajo).
                    self._chain.append(focus_row)
                    self._focus += 1
                elif key == b'\x1b[D' and self._focus > 0:
                    self._focus -= 1                # izquierda: vuelve un nivel
                    del self._chain[self._focus + 1:]

            cols = GRmenu._term_width()

            # Un panel por cada nivel ya "entrado" (self._chain), mas un
            # preview automatico de un nivel mas si la fila resaltada en
            # el ultimo panel es a su vez un GRSubMenu (sin necesidad de
            # apretar flecha derecha todavia). El estilo de borde se
            # hereda en cascada: cada nivel usa el suyo propio si lo
            # define, si no el ya resuelto del panel que lo contiene.
            # Solo el panel con self._focus se pinta como "el foco"
            # (unico en toda la pantalla, ver _render_option_panel).
            panels = []
            style = self.style
            for depth, node in enumerate(self._chain):
                style = getattr(node, "style", None) or style
                is_deepest = depth == len(self._chain) - 1
                if is_deepest and self._preview:
                    panels.append(self._render_source_panel(node, size_max, style, cols))
                else:
                    panels.append(self._render_option_panel(node, size_max, style, depth == self._focus))
            if not self._preview and len(self._chain) < GRSubMenu.MAX_DEPTH:
                last = self._chain[-1]
                lookahead = last.functions[last.index]
                if isinstance(lookahead, GRSubMenu):
                    lookahead_style = getattr(lookahead, "style", None) or style
                    panels.append(self._render_option_panel(lookahead, size_max, lookahead_style, focused=False))

            total_w = sum(w for w, _ in panels) + 2 * (len(panels) - 1)

            banner_w = 0
            if self.banner:
                bb = self.BORDERS().get(str(self.banner_style), self.BORDERS()["3"])
                rows = self.build_ascii_lines(self.banner, cols, self.SetStyle.font)
                if rows:
                    banner_w = max(len(r) for r in rows) + 6
                    bline = self._hline(bb["h"], banner_w - 2)
                    print(self._colorize(bb["tl"] + bline + bb["tr"], self.SetStyle.banner))
                    for r in rows:
                        print(self._colorize(f"{bb['v']}  {r}  {bb['v']}", self.SetStyle.banner))
                    print(self._colorize(bb["bl"] + bline + bb["br"], self.SetStyle.banner))
                else:
                    btext = self.banner.strip()
                    banner_w = min(len(btext) + 6, cols - 2)
                    bline = self._hline(bb["h"], banner_w - 2)
                    print(self._colorize(bb["tl"] + bline + bb["tr"], self.SetStyle.banner))
                    print(self._colorize(f"{bb['v']} {btext.center(banner_w - 4)} {bb['v']}", self.SetStyle.banner))
                    print(self._colorize(bb["bl"] + bline + bb["br"], self.SetStyle.banner))
                print()

            ref = banner_w or total_w

            if self.subtitle:
                div_w = min(ref, cols - 2)
                if self.divider:
                    print(self._colorize("─" * div_w, self.SetStyle.divider))
                for sub_line in self.subtitle.splitlines():
                    print(self._colorize(sub_line.center(div_w) if self.center else sub_line, self.SetStyle.subtitle))
                if self.divider:
                    print(self._colorize("─" * div_w, self.SetStyle.divider))
                print()

            outer_pad = " " * ((ref - total_w) // 2) if self.center and ref > total_w else ""
            height = max(len(lines) for _, lines in panels)
            for row_i in range(height):
                row = [lines[row_i] if row_i < len(lines) else " " * w for w, lines in panels]
                print(outer_pad + "  ".join(row))

            if key == b'\r' and not self._preview and not isinstance(focus_row, GRSubMenu):
                # Si la fila resaltada es un GRSubMenu, Enter ya la entro
                # arriba y no hay nada que ejecutar en esta vuelta. Si no,
                # y hay opciones marcadas con espacio (self._marked es
                # global: pueden ser de cualquier panel/nivel, no solo el
                # que tiene el foco ahora), Enter las ejecuta TODAS en el
                # orden en que se marcaron; si no hay ninguna marcada,
                # ejecuta solo la resaltada.
                to_run = [n.functions[i] for n, i in self._marked] if self._marked else [focus_row]
                if to_run:
                    if not sys.platform == "win32":
                        termios.tcsetattr(self.D, termios.TCSAFLUSH, self.DF)
                        sys.stdout.write("\x1b[?1000l")
                    sys.stdout.write("\x1b[?25h")  # muestra el cursor antes de ejecutar
                    sys.stdout.flush()
                    print(self._clear_seq)
                    for func in to_run:
                        self._call(func)
                    break

    # --- CLI: `python -m GRmenu -h/-a/-s/-b/-d/-e` -------------------------

    @staticmethod
    def _term_width(default=80) -> int:
        try:
            return os.get_terminal_size().columns
        except OSError:
            return default

    @staticmethod
    def _print_header(title, subtitle) -> None:
        GRmenu.banner(title, color="magenta", level=2, style=3, font=1)
        cols = min(GRmenu._term_width(), 66)
        print(GRmenu._colorize("─" * cols, {"color": "blue", "level": 1}))
        for line in subtitle.splitlines():
            print(GRmenu._colorize(line.center(cols), {"color": "cyan", "level": 2}))
        print(GRmenu._colorize("─" * cols, {"color": "blue", "level": 1}))
        print()

    @staticmethod
    def _style_preview(n) -> str:
        b = GRmenu.BORDERS().get(str(n))
        if b:
            h5 = GRmenu._hline(b["h"], 5)
            return f"{b['tl']}{h5}{b['tr']}  {b['v']}     {b['v']}  {b['bl']}{h5}{b['br']}"
        sym = "#"
        return f"{sym * 7}  {sym}     {sym}  {sym * 7}"

    @staticmethod
    def _print_style_help() -> None:
        print(GRmenu._colorize("Estilos de marco disponibles (style / banner_style, 1 al 20):", {"color": "magenta", "level": 2}))
        print(GRmenu._colorize("─" * 66, {"color": "blue", "level": 1}))
        for n in range(1, 21):
            label = GRmenu._colorize(f"{n:>2}", {"color": "yellow", "level": 2})
            print(f"  {label} -> {GRmenu._style_preview(n)}")
        print()
        print("Se usan en: GRmenu(..., style=N, banner_style=N), o en runtime con")
        print("  menu.style = N / menu.banner_style = N antes de menu.draw().")

    @staticmethod
    def _font_preview(font_id, sample="GR") -> str:
        rows = GRmenu.build_ascii_lines(sample, 200, font_id)
        return rows[0] if rows else "(sin glifos para la muestra)"

    @staticmethod
    def _print_banner_help() -> None:
        print(GRmenu._colorize("Fuentes ASCII 3D del banner (font, 1 al 10):", {"color": "magenta", "level": 2}))
        print(GRmenu._colorize("─" * 66, {"color": "blue", "level": 1}))
        for n in range(1, 11):
            label = GRmenu._colorize(f"{n:>2}", {"color": "yellow", "level": 2})
            print(f"  {label} -> {GRmenu._font_preview(n)}")
        print()
        print("Parametros relacionados con el banner:")
        rows = [
            ("banner", "texto a renderizar en arte ASCII 3D."),
            ("banner_style", "estilo de marco del banner (ver --Style)."),
            ("font", "fuente ASCII de arriba (1 al 10)."),
        ]
        for name, desc in rows:
            print(f"  {GRmenu._colorize(name.ljust(14), {'color': 'green', 'level': 2})} -> {desc}")
        print(f"  {GRmenu._colorize('SetStyle.Banner(color, level)'.ljust(30), {'color': 'cyan', 'level': 1})} -> color del banner.")
        print(f"  {GRmenu._colorize('SetStyle.Font(font_id)'.ljust(30), {'color': 'cyan', 'level': 1})} -> fuente global por defecto.")
        print(f"  {GRmenu._colorize('GRmenu.banner(texto, ...)'.ljust(30), {'color': 'cyan', 'level': 1})} -> helper suelto, sin crear un menu.")

    @staticmethod
    def _print_divider_help() -> None:
        print(GRmenu._colorize("Parametro divider:", {"color": "magenta", "level": 2}))
        print(GRmenu._colorize("─" * 66, {"color": "blue", "level": 1}))
        print("Dibuja una linea divisoria arriba y abajo del subtitulo, junto al banner.")
        print()
        rows = [
            ("divider=None", "(default) se activa solo si hay banner o subtitle."),
            ("divider=True", "siempre se dibuja."),
            ("divider=False", "nunca se dibuja."),
        ]
        for name, desc in rows:
            print(f"  {GRmenu._colorize(name.ljust(15), {'color': 'green', 'level': 2})} -> {desc}")
        print()
        print(f"  {GRmenu._colorize('SetStyle.Divider(color, level)'.ljust(30), {'color': 'cyan', 'level': 1})} -> color de las lineas (default: blue, 1).")

    @staticmethod
    def _print_all_help() -> None:
        print(GRmenu._colorize("Parametros de GRmenu(functions, ...):", {"color": "magenta", "level": 2}))
        print(GRmenu._colorize("─" * 66, {"color": "blue", "level": 1}))
        params = [
            ("functions", "opciones: funciones o tuplas (nombre, funcion)."),
            ("title", "titulo del recuadro de opciones."),
            ("style", "estilo de marco de opciones (1 al 20, default 19)."),
            ("banner", "texto grande en arte ASCII 3D."),
            ("subtitle", "subtitulo, soporta '\\n' para varias lineas."),
            ("banner_style", "estilo de marco del banner (1 al 20, default 3)."),
            ("font", "fuente ASCII del banner (1 al 10, default 1)."),
            ("divider", "lineas divisorias junto al banner/subtitle."),
            ("center", "centrado simetrico (default True)."),
        ]
        for name, desc in params:
            print(f"  {GRmenu._colorize(name.ljust(14), {'color': 'green', 'level': 2})} -> {desc}")
        print()

        GRmenu._print_style_help()
        print()
        GRmenu._print_banner_help()
        print()
        GRmenu._print_divider_help()
        print()

        print(GRmenu._colorize("Colores disponibles (GRmenu.COLORS()):", {"color": "magenta", "level": 2}))
        print(GRmenu._colorize("─" * 66, {"color": "blue", "level": 1}))
        color_names = [c for c in GRmenu.COLORS() if c != "reset"]
        print("  " + ", ".join(GRmenu._colorize(c, {"color": c, "level": 2}) for c in color_names))
        print("  Brillo: 1 = normal, 2 = brillante.")
        print()

        print(GRmenu._colorize("Metodos de SetStyle:", {"color": "magenta", "level": 2}))
        print(GRmenu._colorize("─" * 66, {"color": "blue", "level": 1}))
        methods = [
            ("SetStyle.Border(color, level)", "color y brillo del marco de opciones."),
            ("SetStyle.Options(color, level)", "color y brillo de opciones no activas."),
            ("SetStyle.Focus(color, level)", "color y brillo de la opcion resaltada."),
            ("SetStyle.Title(color, level)", "color y brillo del titulo."),
            ("SetStyle.Banner(color, level)", "color y brillo del banner."),
            ("SetStyle.Subtitle(color, level)", "color y brillo del subtitulo."),
            ("SetStyle.Divider(color, level)", "color y brillo de las lineas divisorias."),
            ("SetStyle.Font(font_id)", "fuente ASCII global del banner (1 al 10)."),
            ("SetStyle.Welcome(text, image)", "contenido de la pantalla de bienvenida (GRmenu.welcome)."),
        ]
        for sig, desc in methods:
            print(f"  {GRmenu._colorize(sig.ljust(32), {'color': 'cyan', 'level': 1})} -> {desc}")
        print()

        print(GRmenu._colorize("Ejecucion:", {"color": "magenta", "level": 2}))
        print(GRmenu._colorize("─" * 66, {"color": "blue", "level": 1}))
        print(f"  {GRmenu._colorize('menu.draw(size_max=20)'.ljust(24), {'color': 'white', 'level': 2})} -> arranca el menu (flechas, Enter, q).")
        print()
        print("Genera un ejemplo completo con: python -m GRmenu -e")
        print()

    @staticmethod
    def _generate_example(dest="example.py") -> None:
        template_path = os.path.join(os.path.dirname(__file__), "example_template.py")
        with open(template_path, encoding="utf-8") as fh:
            content = fh.read()
        if os.path.exists(dest):
            print(GRmenu._colorize(f"Ya existe {dest}, no se sobreescribe.", {"color": "red", "level": 2}))
            return
        with open(dest, "w", encoding="utf-8") as fh:
            fh.write(content)
        print(GRmenu._colorize(f"Se genero {dest} con un ejemplo completo de uso de la libreria.", {"color": "green", "level": 2}))
        print(f"Ejecutalo con: python {dest}")

    @staticmethod
    def _cli() -> None:
        parser = argparse.ArgumentParser(
            prog="GRmenu",
            description="GRmenu - libreria de menus interactivos para terminal en modo TTY crudo.",
            add_help=False,
        )
        parser.add_argument("-h", "--help", action="store_true", help="Muestra esta ayuda.")
        parser.add_argument("-a", "--All", action="store_true", help="Muestra la guia completa (estilos, fuentes, colores, parametros, metodos).")
        parser.add_argument("-s", "--Style", action="store_true", help="Muestra los estilos de marco disponibles (style / banner_style, 1 al 20).")
        parser.add_argument("-b", "--Banner", action="store_true", help="Muestra las fuentes del banner (font, 1 al 10) y sus parametros.")
        parser.add_argument("-d", "--Divider", action="store_true", help="Explica el parametro divider (lineas divisorias del banner/subtitulo).")
        parser.add_argument("-e", "--Example", action="store_true", help="Genera example.py en el directorio actual con un ejemplo completo de la libreria.")
        args = parser.parse_args()

        if args.Example:
            GRmenu._generate_example()
        elif args.All:
            GRmenu._print_header("GRMENU", "Guia y Referencia Rapida\nNavegacion interactiva en terminal TTY")
            GRmenu._print_all_help()
        elif args.Style:
            GRmenu._print_header("STYLE", "Estilos de marco disponibles\n(style / banner_style, 1 al 20)")
            GRmenu._print_style_help()
        elif args.Banner:
            GRmenu._print_header("BANNER", "Fuentes ASCII 3D del banner\n(font, 1 al 10)")
            GRmenu._print_banner_help()
        elif args.Divider:
            GRmenu._print_header("DIVIDER", "Lineas divisorias junto al banner y subtitulo")
            GRmenu._print_divider_help()
        else:
            GRmenu._print_header("GRMENU", "Ayuda de linea de comandos")
            parser.print_help()


if __name__ == "__main__":
    GRmenu._cli()


