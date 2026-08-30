
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

    def __init__(self,functions : list,title="",style=19,banner="",subtitle="",banner_style=3,divider=None,center=True,font=None):
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
            title: Titulo que se muestra dentro del recuadro de opciones. Si
                queda vacio ("") no se dibuja la fila de titulo.
            style: Numero de estilo de marco de opciones a usar (1 al 20, ver
                `GRmenu.STYLES()` y `GRmenu.BORDERS()`; ej: 7 = redondeado,
                3 = doble linea). Por defecto 19 ("●").
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
        """
        if sys.platform == "win32":
            _enable_windows_ansi()
            self.D = None
            self.DF = None
        else:
            self.D = sys.stdin.fileno()
            self.DF = termios.tcgetattr(self.D)
            tty.setraw(self.D)

        self.functions = functions
        self.style = style
        self.GRprint.setFixPrint()
        self.title = title
        self.index = 0
        self._clear_seq = "\x1b[H\x1b[2J\x1b[3J"
        self.banner = banner
        self.subtitle = subtitle
        self.banner_style = banner_style
        self.divider = divider if divider is not None else bool(banner or subtitle)
        self.center = center
        if font is not None:
            GRmenu.SetStyle.Font(font)

    def _up(self):
        self.index = (self.index - 1) % len(self.functions)
    def _down(self):
        self.index =  (self.index + 1) % len(self.functions)


    @staticmethod
    def STYLES():
        """Devuelve los simbolos usados para dibujar un borde "simple".

        Se usan como respaldo cuando el estilo elegido (`self.style`) no
        tiene una definicion detallada (esquinas + lineas) en `BORDERS()`:
        en ese caso `draw()` repite este mismo caracter para todo el
        recuadro en vez de usar esquinas distintas.

        Returns:
            dict: mapea el numero de estilo (int, 1 a 20) al caracter que le
                corresponde. Por ejemplo `STYLES()[19]` es "●".
        """
        return {
            1:"#",2:"┌",3:"╔",4:"┏",5:"╒",6:"╓",7:"╭",8:"▛",
            9:"▓",10:"▒",11:"░",12:"█",13:"*",14:"+",15:"=",
            16:"~",17:"-",18:"◆",19:"●",20:"★"
        }

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
        """
        if GRmenu._borders_cache is None:
            with open(GRmenu._data_path("borders.json"), encoding="utf-8") as fh:
                GRmenu._borders_cache = json.load(fh)
        return GRmenu._borders_cache
    
    class SetStyle:
        border = {"color": "cyan", "level": 1}
        options = {"color": "white", "level": 1}
        focus = {"color": "green", "level": 2}
        title = {"color": "yellow", "level": 2}
        banner = {"color": "magenta", "level": 2}
        subtitle = {"color": "cyan", "level": 2}
        divider = {"color": "blue", "level": 1}
        font = 1

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
        if isinstance(f, (list, tuple)):
            return str(f[0])
        name = getattr(f, "__name__", "opcion")
        return "Lambda" if name == "<lambda>" else name.replace("_", " ").title()

    @staticmethod
    def _call(f) -> Any:
        return f[1]() if isinstance(f, (list, tuple)) else f()

    def menu(self) -> None:
        """Pantalla mostrada antes de dibujar el menu por primera vez.

        Se llama una unica vez al comienzo de `draw()`, antes de leer la
        primera tecla. Por defecto solo imprime "Press any key to start ...".
        Pensado para ser sobreescrito (override) en una subclase si se
        quiere mostrar una pantalla de bienvenida distinta.
        """
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
        return os.read(fd, 3)

    def draw(self,size_max=20):
        """Dibuja el menu y arranca el loop de lectura de teclado.

        Muestra las opciones (`self.functions`) dentro de un recuadro,
        resalta la opcion actualmente seleccionada, y queda esperando
        teclas:
            - Flecha arriba / abajo: mueve la seleccion.
            - Enter: restaura la configuracion original de la terminal,
              ejecuta la opcion seleccionada y termina el loop.
            - "q": sale del menu sin ejecutar ninguna opcion.

        Args:
            size_max: Ancho minimo (en caracteres) del recuadro del menu,
                usado aunque el texto de las opciones sea mas corto. Por
                defecto 20.
        """
        self.menu()
        while (key := self._read_key(self.D)) != b'q':
            print(self._clear_seq, end="")

            self._up() if key==b'\x1b[A' else None # up
            self._down() if key==b'\x1b[B' else None # down

            #print("right",end="\r\f") if key==b'\x1b[C' else None # right
            #print("left",end="\r\f") if key==b'\x1b[D' else None # left

            names = [self._name(f) for f in self.functions]
            width = max([size_max] + [len(n) + 4 for n in names])
            if self.title:
                width = max(width, len(self.title) + 4)

            cols = GRmenu._term_width()
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

            ref = banner_w or width
            pad = " " * ((ref - width) // 2) if self.center and ref > width else ""

            if self.subtitle:
                div_w = min(ref, cols - 2)
                if self.divider:
                    print(self._colorize("─" * div_w, self.SetStyle.divider))
                for sub_line in self.subtitle.splitlines():
                    print(self._colorize(sub_line.center(div_w) if self.center else sub_line, self.SetStyle.subtitle))
                if self.divider:
                    print(self._colorize("─" * div_w, self.SetStyle.divider))
                print()

            bc, oc, fc, tc = self.SetStyle.border, self.SetStyle.options, self.SetStyle.focus, self.SetStyle.title
            box_border = self.BORDERS().get(str(self.style))
            if box_border:
                b = box_border
                line = self._hline(b["h"], width - 2)
                v = self._colorize(b["v"], bc)
                print(self._colorize(b["tl"] + line + b["tr"], bc))
                if self.title:
                    print(f"{v} {self._colorize(self.title.center(width - 4), tc)} {v}")
                    print(self._colorize(b["v"] + line + b["v"], bc))
                for name in names:
                    if self.index == names.index(name):
                        option = self._colorize(f">{name.ljust(width - 6)}", fc)
                        print(f"{v}  {option} {v}")
                    else:
                        option = self._colorize(f"> {name.ljust(width - 6)}", oc)
                        print(f"{v} {option} {v}")

                print(self._colorize(b["bl"] + line + b["br"], bc))
            else:
                symbol = self.STYLES().get(self.style, "#")
                border = self._colorize(symbol, bc)
                print(self._colorize(symbol * width, bc))
                if self.title:
                    print(f"{border} {self._colorize(self.title.center(width - 4), tc)} {border}")
                    print(self._colorize(symbol * width, bc))
                for name in names:
                    if self.index == names.index(name):
                        print(f"{border} {self._colorize(name.ljust(width - 4), fc)} {border}")
                    else:
                        print(f"{border} {self._colorize(name.ljust(width - 4), oc)} {border}")
                print(self._colorize(symbol * width, bc))

            if key == b'\r':
                if not sys.platform == "win32":
                    termios.tcsetattr(self.D, termios.TCSAFLUSH, self.DF)
                print(self._clear_seq)
                self._call(self.functions[self.index])
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
        sym = GRmenu.STYLES().get(n, "#")
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


