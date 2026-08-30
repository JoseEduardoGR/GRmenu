import time
import os
import sys
import termios
import tty
import json
from typing import Optional, Any

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
            GRmenu.SetStyle.Font(font);
        import argparse
        if argparse._sys.argv and "-h" in argparse._sys.argv:
            print("fack")
            exit()

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
        cols = os.get_terminal_size().columns
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
        while (key := os.read(self.D,3)) != b'q':
            print(self._clear_seq, end="")

            self._up() if key==b'\x1b[A' else None # up
            self._down() if key==b'\x1b[B' else None # down

            #print("right",end="\r\f") if key==b'\x1b[C' else None # right
            #print("left",end="\r\f") if key==b'\x1b[D' else None # left

            names = [self._name(f) for f in self.functions]
            width = max([size_max] + [len(n) + 4 for n in names])
            if self.title:
                width = max(width, len(self.title) + 4)

            cols = os.get_terminal_size().columns
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
                termios.tcsetattr(self.D, termios.TCSAFLUSH, self.DF)
                print(self._clear_seq)
                self._call(self.functions[self.index])
                break


