
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
import math
import runpy
import select
import struct
import subprocess
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

    def __init__(self,functions : list,title="",style=19,banner="",subtitle="",banner_style=3,divider=None,center=True,font=None,max_show_options=10,searchable=False,animate=False):
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
            animate: Anima el borde, el titulo y el banner del menu.
                `False` (por defecto) no cambia nada del comportamiento ni
                el rendimiento actual (sigue bloqueando esperando tecla,
                sin redibujar de mas). Valores validos:
                    - "rgb": arcoiris que recorre todo el espectro de color
                      (ignora el color configurado en `SetStyle`).
                    - "fade": el color YA configurado (`SetStyle.Border`,
                      `.Title`, `.Banner`) sube y baja de brillo (respira).
                    - "linear": el color configurado con una ola de brillo
                      que se mueve de lado a lado.
                    - "diagonal": igual que "linear", pero la ola tambien
                      varia con la fila, asi que barre en diagonal.
                Activarlo cambia el loop de lectura de teclas: en vez de
                bloquear indefinidamente, espera hasta ~35ms por una tecla
                y si no llega ninguna redibuja el frame (~28 FPS) en vez de
                seguir esperando.
        """
        if animate not in GRmenu.ANIMATIONS:
            raise ValueError(f"animate debe ser uno de {GRmenu.ANIMATIONS!r}, no {animate!r}")
        if sys.platform == "win32":
            _enable_windows_ansi()
            self.D = None
            self.DF = None
        else:
            self.D = sys.stdin.fileno()
            self.DF = termios.tcgetattr(self.D)
            tty.setraw(self.D)
            sys.stdout.write("\x1b[?1000h\x1b[?1003h")  # reporte de mouse: clicks/rueda + movimiento (hover)
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
        self.animate = animate
        self._anim_tick = 0.0
        # Click/hover del mouse: `_read_key` deja las coordenadas del
        # ultimo click/movimiento en `_last_click`/`_last_hover`;
        # `_draw_loop` guarda en `_click_regions`, cuadro a cuadro, que
        # opcion cae bajo cada celda clickeable de lo que ACABA de
        # dibujar, para poder resolver el click/hover del PROXIMO frame
        # (el que ya esta en pantalla cuando el usuario mueve el mouse).
        self._last_click = None
        self._last_hover = None
        self._click_regions = []
        if font is not None:
            GRmenu.SetStyle.Font(font)
        self._ensure_terminal_size()

    def _estimate_size(self) -> tuple:
        """Estima (columnas, filas) minimas para que ESTE menu (banner +
        subtitulo + recuadro de opciones) se dibuje sin cortarse, con el
        mismo criterio (aproximado) que usa el layout real de `draw()`.
        Usada por `_ensure_terminal_size` para saber si hace falta
        agrandar la terminal antes de la primera tecla."""
        names = [self._name(f) for f in self.functions]
        width = max([20] + [len(n) + 8 for n in names] + ([len(self.title) + 4] if self.title else []))
        n_visible = min(len(self.functions), self.max_show_options or len(self.functions))
        height = 2 + (1 if self.title else 0) + n_visible + 2  # borde + titulo + opciones + footer

        if self.banner:
            rows = GRmenu.build_ascii_lines(self.banner, 999, GRmenu.SetStyle.font)
            if rows:
                width = max(width, max(len(r) for r in rows) + 6)
                height += len(rows) + 3
            else:
                width = max(width, len(self.banner.strip()) + 6)
                height += 3

        if self.subtitle:
            sub_lines = self.subtitle.splitlines()
            width = max(width, max(len(ln) for ln in sub_lines) + 2)
            height += len(sub_lines) + (2 if self.divider else 0) + 1

        return width + 2, height + 2  # margen de seguridad

    def _ensure_terminal_size(self) -> None:
        """Si la terminal actual es mas chica que lo que este menu
        necesita (ver `_estimate_size`), intenta agrandarla. Nunca la
        achica: si ya es mas grande de lo necesario, no hace nada.

        Dos intentos, de mas a menos portable, ambos "best effort" (si
        ninguno funciona, sigue de largo sin avisar: no hay forma
        universal de saber de antemano si la terminal va a aceptar
        alguno de los dos):

        1. La secuencia XTWINOPS `CSI 8 ; filas ; columnas t` (la
           soporta xterm y varios otros, pero kitty la rechaza a
           proposito por diseño -- ver
           https://sw.kovidgoyal.net/kitty/desktop-integration/ y su
           postura sobre escape codes de control de ventana).
        2. Si seguimos cortos Y estamos corriendo dentro de kitty
           (`KITTY_WINDOW_ID` en el entorno), `kitty @ resize-os-window`
           (su protocolo de control remoto). Requiere que la terminal
           tenga `allow_remote_control` habilitado en `kitty.conf`; si
           no lo tiene, el comando falla solo y no hace nada (no
           modificamos esa config nosotros).
        """
        if sys.platform == "win32" or not sys.stdout.isatty():
            return
        try:
            cur_cols, cur_rows = os.get_terminal_size()
        except OSError:
            return

        need_cols, need_rows = self._estimate_size()
        need_cols = min(need_cols, 300)   # nunca pedir algo absurdo
        need_rows = min(need_rows, 80)
        if need_cols <= cur_cols and need_rows <= cur_rows:
            return

        rows = max(need_rows, cur_rows)
        cols = max(need_cols, cur_cols)

        sys.stdout.write(f"\x1b[8;{rows};{cols}t")
        sys.stdout.flush()
        if self._wait_for_size(need_cols, need_rows):
            return

        if os.environ.get("KITTY_WINDOW_ID"):
            try:
                subprocess.run(
                    ["kitty", "@", "resize-os-window", "--self", "--unit", "cells",
                     "--width", str(cols), "--height", str(rows)],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    timeout=1.0, check=False,
                )
            except (OSError, subprocess.SubprocessError):
                return
            self._wait_for_size(need_cols, need_rows)

    @staticmethod
    def _wait_for_size(need_cols, need_rows, tries=10, interval=0.02) -> bool:
        """Espera hasta `tries * interval` segundos a que la terminal
        llegue a (al menos) `need_cols` x `need_rows`, dandole tiempo a
        aplicar un resize recien pedido. Devuelve si lo logro."""
        for _ in range(tries):
            time.sleep(interval)
            try:
                size = os.get_terminal_size()
            except OSError:
                return False
            if size.columns >= need_cols and size.lines >= need_rows:
                return True
        return False

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
                por defecto de la terminal. La clave "rgb" (si esta en
                `colors.json`) NO se convierte a secuencia de escape: queda
                como tupla `(r, g, b)`, la usa `_anim_color` como base para
                animar ese color (ver `animate` en `GRmenu.__init__`).
        """
        if GRmenu._colors_cache is None:
            with open(GRmenu._data_path("colors.json"), encoding="utf-8") as fh:
                raw = json.load(fh)
            GRmenu._colors_cache = {
                name: (
                    {
                        **{level: f"\x1b[{code}" for level, code in codes.items() if level != "rgb"},
                        **({"rgb": tuple(codes["rgb"])} if "rgb" in codes else {}),
                    } if isinstance(codes, dict) else f"\x1b[{codes}"
                )
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

    # --- Config .gr: exportar/importar GRmenu.SetStyle ---------------------
    #
    # Formato propio de GRmenu (no YAML/JSON), pensado para leerse a ojo:
    #
    #   GRmenu::config::1
    #
    #   <<border
    #     color:: cyan
    #     level:: 1
    #   >>
    #   ...
    #   font:: 1
    #   <<welcome
    #     text:: (vacio)
    #     image:: (vacio)
    #     width:: (vacio)
    #     height:: (vacio)
    #   >>
    #
    # "::" separa clave y valor (tambien arma la cabecera "GRmenu::config::1").
    # "<<nombre" abre una seccion, ">>" la cierra. Solo hay un nivel de
    # anidado (una seccion no puede contener otra seccion adentro).

    _CONFIG_HEADER = "GRmenu::config::1"
    _CONFIG_COLOR_SECTIONS = ("border", "options", "focus", "title", "banner", "subtitle", "divider", "description")

    @staticmethod
    def ExportConfig(path=None) -> str:
        """Exporta la configuracion global actual (`GRmenu.SetStyle`) a un
        archivo `.gr` (formato propio de GRmenu, ver comentario arriba).

        Args:
            path: Donde guardar el archivo. Si se omite (`None`), se
                guarda al lado del script que llama a esta funcion, con su
                mismo nombre pero extension `.gr` (ej. si tu script es
                "app.py", genera "app.gr" en la misma carpeta).

        Returns:
            str: la ruta donde quedo guardado el archivo (la que se paso,
                o la resuelta automaticamente si `path` era `None`).
        """
        if path is None:
            caller = inspect.stack()[1].filename
            path = os.path.splitext(os.path.abspath(caller))[0] + ".gr"

        S = GRmenu.SetStyle
        lines = [GRmenu._CONFIG_HEADER, ""]
        for name in GRmenu._CONFIG_COLOR_SECTIONS:
            cfg = getattr(S, name)
            lines.append(f"<<{name}")
            lines.append(f"  color:: {cfg['color']}")
            lines.append(f"  level:: {cfg['level']}")
            lines.append(">>")
            lines.append("")
        lines.append(f"font:: {S.font}")
        lines.append("")
        lines.append("<<welcome")
        for key, value in S.welcome.items():
            if key == "text" and value:
                value = value.replace("\n", "\\n")
            lines.append(f"  {key}:: {'' if value is None else value}")
        lines.append(">>")

        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
        return path

    @staticmethod
    def _parse_config(path) -> dict:
        with open(path, encoding="utf-8") as fh:
            raw_lines = fh.read().splitlines()
        lines = [ln for ln in raw_lines if ln.strip() and not ln.strip().startswith("#")]
        if not lines or not lines[0].strip().startswith("GRmenu::config"):
            raise ValueError(f"{path!r} no es un archivo de configuracion GRmenu (.gr) valido: falta la cabecera 'GRmenu::config::1'")

        data = {}
        section = None
        section_data = {}
        for ln in lines[1:]:
            stripped = ln.strip()
            if stripped.startswith("<<"):
                if section is not None:
                    raise ValueError(f"{path!r}: seccion '{section}' sin cerrar antes de abrir '{stripped[2:]}'")
                section = stripped[2:].strip()
                section_data = {}
            elif stripped == ">>":
                if section is None:
                    raise ValueError(f"{path!r}: '>>' sin ninguna seccion abierta")
                data[section] = section_data
                section = None
            elif "::" in stripped:
                key, _, value = stripped.partition("::")
                key, value = key.strip(), value.strip()
                (section_data if section is not None else data)[key] = value
            else:
                raise ValueError(f"{path!r}: linea invalida: {ln!r}")
        if section is not None:
            raise ValueError(f"{path!r}: seccion '{section}' nunca se cerro con '>>'")
        return data

    @staticmethod
    def ImportConfig(path) -> None:
        """Carga un archivo `.gr` generado por `ExportConfig` (o escrito a
        mano con el mismo formato) y aplica su configuracion a
        `GRmenu.SetStyle`: afecta a cualquier menu creado despues de esta
        llamada, igual que llamar a `SetStyle.Border(...)`, etc. a mano.

        Una seccion/clave ausente en el archivo deja ese valor de
        `SetStyle` como estaba (no lo resetea): un `.gr` puede tocar solo
        una parte de la configuracion.

        Args:
            path: Ruta al archivo `.gr` a importar.

        Raises:
            ValueError: si el archivo no tiene el formato esperado (falta
                la cabecera, una seccion quedo sin cerrar, etc).
        """
        data = GRmenu._parse_config(path)
        S = GRmenu.SetStyle

        for name in GRmenu._CONFIG_COLOR_SECTIONS:
            if name not in data:
                continue
            current = getattr(S, name)
            sect = data[name]
            color = sect.get("color") or current["color"]
            level = int(sect["level"]) if sect.get("level") else current["level"]
            setattr(S, name, {"color": color, "level": level})

        if "font" in data and data["font"]:
            S.Font(int(data["font"]))

        if "welcome" in data:
            w = data["welcome"]
            current = S.welcome

            def resolve(key, cast=str):
                # ausente en el .gr -> deja el valor actual sin tocar.
                # presente pero vacio -> lo borra (None), a proposito.
                # presente con valor -> lo castea y lo usa.
                if key not in w:
                    return current[key]
                return cast(w[key]) if w[key] else None

            S.Welcome(
                text=resolve("text", lambda v: v.replace("\\n", "\n")),
                image=resolve("image"),
                width=resolve("width", int),
                height=resolve("height", int),
            )

    @staticmethod
    def _colorize(text, color_cfg):
        if not color_cfg:
            return text
        colors = GRmenu.COLORS()
        code = colors.get(color_cfg["color"], {}).get(str(color_cfg["level"]), "")
        if not code:
            return text
        return f"{code}{text}{colors['reset']}"

    ANIMATIONS = (False, "linear", "fade", "diagonal", "rgb")

    @staticmethod
    def _rgb_wave(t) -> tuple:
        """Color arcoiris en el instante `t`: 3 senoidales desfasadas 120°
        entre si (una por canal), igual formula que usa la version Ruby
        para su modo "rgb"/"rainbow"/"chroma"."""
        r = int(max(0, min(255, math.sin(t) * 127 + 128)))
        g = int(max(0, min(255, math.sin(t + 2.0943951) * 127 + 128)))
        b = int(max(0, min(255, math.sin(t + 4.1887902) * 127 + 128)))
        return r, g, b

    @staticmethod
    def _scale_rgb(base, factor) -> tuple:
        """Escala `base` (r, g, b) por `factor` (0.0 a 1.0), sin bajar de
        1/4 de su brillo (para que el "valle" de un fade/pulso se vea
        atenuado en vez de apagarse del todo a negro)."""
        low = 0.25
        f = low + (1 - low) * factor
        return tuple(int(max(0, min(255, c * f))) for c in base)

    def _anim_color(self, color_cfg, t) -> tuple:
        """Color (r, g, b) para el instante `t`, segun `self.animate`.

        "rgb" ignora `color_cfg` y cicla el espectro completo. El resto de
        los modos parte del RGB base ya cargado en `COLORS()[...]["rgb"]`
        para el color configurado (`color_cfg["color"]`) y le anima el
        brillo con la misma senoidal, en vez de cambiar de tono."""
        if self.animate == "rgb":
            return self._rgb_wave(t)
        base = self.COLORS().get(color_cfg.get("color"), {}).get("rgb", (255, 255, 255))
        factor = (math.sin(t) + 1) / 2
        return self._scale_rgb(base, factor)

    def _colorize_anim(self, text, color_cfg, row=0, col=0) -> str:
        """Como `_colorize`, pero si `self.animate` esta activo devuelve
        `text` animado en vez del color fijo de `color_cfg`.

        Sin animacion activa (`self.animate` en `False`, el default) se
        comporta identico a `_colorize`: cero cambio de comportamiento.

        - "fade": un solo color (truecolor) para todo `text`, cuyo brillo
          sube y baja con el reloj de la animacion (`self._anim_tick`).
        - "rgb"/"linear"/"diagonal": un color por caracter, con una fase
          que depende de la posicion horizontal (las 3) y ademas de `row`
          (la vertical, solo "diagonal") para que la ola se vea barrer el
          recuadro en diagonal en vez de solo de lado a lado.

        `col` es la columna (dentro de la fila que se esta dibujando) en
        la que arranca `text`: la fase horizontal se calcula con
        `col + i`, no solo `i`. Hace falta cuando `text` no es la fila
        completa -- por ejemplo el borde vertical derecho, que se
        colorea suelto (un solo caracter) para reusarlo en varias filas;
        sin `col` esa fase siempre daria la del caracter en la columna 0
        (la misma que el borde IZQUIERDO), en vez de la que le toca del
        lado derecho del recuadro.
        """
        if not self.animate or not color_cfg:
            return self._colorize(text, color_cfg)
        if self.animate == "fade":
            r, g, b = self._anim_color(color_cfg, self._anim_tick)
            return f"\x1b[38;2;{r};{g};{b}m{text}\x1b[0m"
        out = [""] * len(text)
        for i, ch in enumerate(text):
            if ch in (" ", "\n", "\t"):
                out[i] = ch
                continue
            pos = col + i
            if self.animate == "rgb":
                phase = pos * 0.12
            elif self.animate == "diagonal":
                phase = pos * 0.3 + row * 0.6
            else:  # "linear"
                phase = pos * 0.3
            r, g, b = self._anim_color(color_cfg, self._anim_tick + phase)
            out[i] = f"\x1b[38;2;{r};{g};{b}m{ch}"
        return "".join(out) + "\x1b[0m"

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

    # Ancho/alto aproximado de una celda de terminal, en pixels (una
    # celda tipica de fuente monoespaciada es mas alta que ancha). No hay
    # forma de pedirselo a la terminal sin una consulta que puede colgarse
    # si no la soporta, asi que se usa esta aproximacion estandar para
    # calcular cuantas FILAS le corresponden a una imagen dada su ancho
    # en COLUMNAS, sin que se vea estirada (ver `_sniff_image_size` y su
    # uso en `welcome`).
    _CELL_ASPECT = 0.5

    @staticmethod
    def _sniff_image_size(path) -> Optional[tuple]:
        """Ancho x alto (en pixels) de un PNG/GIF/JPEG/BMP, leyendo solo
        su cabecera -- sin decodificar la imagen ni depender de Pillow ni
        ninguna libreria externa.

        Returns:
            Optional[tuple]: `(ancho, alto)` en pixels, o `None` si no se
                pudo determinar (formato no reconocido, archivo
                corrupto/truncado, etc). Quien lo llama debe tratar
                `None` como "no se sabe el tamano", no como un error.
        """
        try:
            with open(path, "rb") as fh:
                head = fh.read(32)
                if head[:8] == b"\x89PNG\r\n\x1a\n":
                    w, h = struct.unpack(">II", head[16:24])
                    return w, h
                if head[:6] in (b"GIF87a", b"GIF89a"):
                    w, h = struct.unpack("<HH", head[6:10])
                    return w, h
                if head[:2] == b"BM":
                    w, h = struct.unpack("<ii", head[18:26])
                    return abs(w), abs(h)
                if head[:2] == b"\xff\xd8":
                    fh.seek(2)
                    while True:
                        marker = fh.read(2)
                        if len(marker) < 2 or marker[0] != 0xff:
                            return None
                        kind = marker[1]
                        if kind in (0xd8, 0xd9):  # SOI/EOI, sin tamaño
                            continue
                        seg_len = struct.unpack(">H", fh.read(2))[0]
                        if 0xc0 <= kind <= 0xcf and kind not in (0xc4, 0xc8, 0xcc):
                            fh.read(1)  # precision
                            h, w = struct.unpack(">HH", fh.read(4))
                            return w, h
                        fh.seek(seg_len - 2, 1)
        except (OSError, struct.error):
            return None
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

    def _banner_cols(self) -> Optional[int]:
        """Ancho (en columnas) que va a ocupar `self.banner` cuando se
        dibuje, con el mismo criterio que usa `_draw_loop`. `None` si
        este menu no tiene banner configurado."""
        if not self.banner:
            return None
        cols = GRmenu._term_width()
        rows = self.build_ascii_lines(self.banner, cols, self.SetStyle.font)
        if rows:
            return max(len(r) for r in rows) + 6
        return min(len(self.banner.strip()) + 6, cols - 2)

    def welcome(self) -> None:
        """Pantalla de bienvenida mostrada antes de dibujar el menu por primera vez.

        Se llama una unica vez al comienzo de `draw()`, antes de leer la
        primera tecla. Su contenido se configura con `SetStyle.Welcome`:

            - Si se configuro `image` y la terminal soporta imagenes
              embebidas (ver `_image_protocol`), se muestra esa imagen.
              Si no se paso `width`/`height` explicito, el ancho por
              defecto es el del banner de este menu (o 40 columnas si no
              tiene banner), y el alto se calcula a partir del tamaño
              real del archivo (ver `_sniff_image_size`) para que
              mantenga su proporcion en vez de verse estirada.
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
                    width = self._banner_cols() or 40
                    size = GRmenu._sniff_image_size(image)
                    if size and size[0] > 0:
                        img_w, img_h = size
                        height = max(1, round(img_h / img_w * width * GRmenu._CELL_ASPECT))
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

    def _read_key(self, fd):
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
            code = cb - 32
            if code == 64: return b'\x1b[A'   # rueda arriba = flecha arriba
            if code == 65: return b'\x1b[B'   # rueda abajo = flecha abajo
            if code & 0x20:                   # movimiento (?1003h): hover, con o sin boton
                self._last_hover = (cx - 32, cy - 32)  # (columna, fila), 1-based
                return b'\x1b[HOVER'
            if code == 0:                     # click izquierdo (sin modificadores), press
                self._last_click = (cx - 32, cy - 32)  # (columna, fila), 1-based
                return b'\x1b[CLICK'
            return b''
        return data

    _ANIM_FRAME_SECONDS = 0.035  # ~28 FPS, mismo intervalo que usa Ruby
    _ANIM_TICK_STEP = 0.08

    def _read_key_or_tick(self):
        """Como `_read_key(self.D)`, pero si `self.animate` esta activo no
        bloquea indefinidamente: espera como mucho `_ANIM_FRAME_SECONDS`
        por una tecla y, si no llega ninguna en ese tiempo, avanza el
        reloj de la animacion (`self._anim_tick`) y devuelve `b''` (una
        tecla "vacia" que _draw_loop ya ignora sin cambiar nada de
        estado, asi que solo hace que se vuelva a dibujar el frame con el
        color animado actualizado).

        Sin `self.animate` (el default) es identico a `_read_key`: sigue
        bloqueado esperando la proxima tecla, sin overhead nuevo.
        """
        if not self.animate:
            return self._read_key(self.D)
        if sys.platform == "win32":
            if msvcrt.kbhit():
                return self._read_key(self.D)
            time.sleep(self._ANIM_FRAME_SECONDS)
            self._anim_tick += self._ANIM_TICK_STEP
            return b''
        ready, _, _ = select.select([self.D], [], [], self._ANIM_FRAME_SECONDS)
        if ready:
            return self._read_key(self.D)
        self._anim_tick += self._ANIM_TICK_STEP
        return b''


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
                sys.stdout.write("\x1b[?1003l\x1b[?1000l")  # desactiva reporte de mouse
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
        """Devuelve (ancho, lineas ya coloreadas, targets) del panel de
        opciones de `node` (self o un GRSubMenu). Cada linea ya incluye
        sus dos bordes verticales; no incluye el padding horizontal
        externo (eso lo pone quien componga varios paneles uno al lado
        del otro en _draw_loop).

        `targets` es una lista paralela a `lines`: `targets[i]` es el
        indice (en `node.functions`) de la opcion que dibuja `lines[i]`,
        o `None` si esa linea no es clickeable (borde, titulo, buscador,
        etc). La usa `_draw_loop` para saber que opcion cae bajo un click
        del mouse.

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
        targets = []
        if box_border:
            b = box_border
            line = self._hline(b["h"], width - 2)
            # v_right lleva `col=width - 1` para que su fase de animacion
            # corresponda a su columna REAL (la ultima de la fila) y no a
            # la 0 -- sin esto, el borde derecho quedaba siempre pintado
            # igual que el izquierdo (ver _colorize_anim).
            v_left = self._colorize_anim(b["v"], bc)
            v_right = self._colorize_anim(b["v"], bc, col=width - 1)
            lines.append(self._colorize_anim(b["tl"] + line + b["tr"], bc, row=len(lines)))
            targets.append(None)
            if title:
                lines.append(f"{v_left} {self._colorize_anim(title.center(width - 4), tc, row=len(lines))} {v_right}")
                targets.append(None)
                lines.append(self._colorize_anim(b["v"] + line + b["v"], bc, row=len(lines)))
                targets.append(None)
            if searching:
                lines.append(f"{v_left} {self._colorize(search_row.ljust(width - 4), dc)} {v_right}")
                targets.append(None)
                lines.append(self._colorize_anim(b["v"] + line + b["v"], bc, row=len(lines)))
                targets.append(None)
            if not visible:
                lines.append(f"{v_left} {self._colorize('(sin coincidencias)'.ljust(width - 4), oc)} {v_right}")
                targets.append(None)
            for i, name in visible:
                if i in marked:
                    color = (fc if focused else oc) if node.index == i else oc
                    option = self._colorize(f"[x] {name.ljust(width - 8)}", color)
                    lines.append(f"{v_left} {option} {v_right}")
                elif node.index == i:
                    option = self._colorize(f">{name.ljust(width - 6)}", fc if focused else oc)
                    lines.append(f"{v_left}  {option} {v_right}")
                else:
                    option = self._colorize(f"> {name.ljust(width - 6)}", oc)
                    lines.append(f"{v_left} {option} {v_right}")
                targets.append(i)
            lines.append(self._colorize_anim(b["bl"] + line + b["br"], bc, row=len(lines)))
            targets.append(None)
        else:
            symbol = "#"
            border = self._colorize(symbol, bc)
            lines.append(self._colorize(symbol * width, bc))
            targets.append(None)
            if title:
                lines.append(f"{border} {self._colorize(title.center(width - 4), tc)} {border}")
                targets.append(None)
                lines.append(self._colorize(symbol * width, bc))
                targets.append(None)
            if searching:
                lines.append(f"{border} {self._colorize(search_row.ljust(width - 4), dc)} {border}")
                targets.append(None)
                lines.append(self._colorize(symbol * width, bc))
                targets.append(None)
            if not visible:
                lines.append(f"{border} {self._colorize('(sin coincidencias)'.ljust(width - 4), oc)} {border}")
                targets.append(None)
            for i, name in visible:
                color = (fc if focused else oc) if node.index == i else oc
                content = f"[x] {name}" if i in marked else name
                lines.append(f"{border} {self._colorize(content.ljust(width - 4), color)} {border}")
                targets.append(i)
            lines.append(self._colorize(symbol * width, bc))
            targets.append(None)

        if truncated:
            pos = filtered.index(node.index) + 1 if node.index in filtered else 0
            lines.append(self._colorize(f"{pos} de {total}".rjust(width), dc))
            targets.append(None)

        if marked:
            plural = "s" if len(marked) != 1 else ""
            lines.append(self._colorize(f"{len(marked)} marcada{plural}".rjust(width), dc))
            targets.append(None)

        desc = self._description(node.functions[node.index])
        if desc:
            lines.append(self._colorize(desc.rjust(width), dc))
            targets.append(None)
        return width, lines, targets

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
            v_left = self._colorize_anim(b["v"], bc)
            v_right = self._colorize_anim(b["v"], bc, col=width - 1)
            lines.append(self._colorize_anim(b["tl"] + line + b["tr"], bc, row=len(lines)))
            lines.append(f"{v_left} {self._colorize_anim(title.center(width - 4), tc, row=len(lines))} {v_right}")
            lines.append(self._colorize_anim(b["v"] + line + b["v"], bc, row=len(lines)))
            for ln in src:
                lines.append(f"{v_left} {self._colorize(ln[:width - 4].ljust(width - 4), oc)} {v_right}")
            lines.append(self._colorize_anim(b["bl"] + line + b["br"], bc, row=len(lines)))
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
        return width, lines, [None] * len(lines)

    def _draw_loop(self, size_max):
        # tty.setraw() apaga ISIG, asi que Ctrl+C no llega como SIGINT sino
        # como el byte \x03 leido normalmente: hay que salir a mano igual
        # que con "q", si no el modo raw queda pegado hasta romper con kill.
        first_key = True
        while True:
            # La primera tecla es la que saca la pantalla de bienvenida
            # (`welcome()`, incluida la imagen si hay): tiene que esperar
            # una tecla/click/rueda DE VERDAD, sin importar `animate` --
            # si no, con animate activo el primer "tick" ocioso (a los
            # ~35ms, sin que el usuario toque nada) ya dispara el limpiar
            # pantalla + dibujar de mas abajo, y la bienvenida desaparece
            # casi al instante (no llega a verse). De la segunda vuelta
            # en adelante (ya con el menu real dibujado) si queremos que
            # los ticks ociosos redibujen, para que la animacion se vea
            # avanzar aunque no se toque nada.
            key = self._read_key(self.D) if first_key else self._read_key_or_tick()
            first_key = False

            if key == b'\x1b[CLICK' and self._last_click and not self._preview:
                # Resuelve el click contra lo que se dibujo en el frame
                # ANTERIOR (que es lo que el usuario tenia en pantalla al
                # clickear). Si cae sobre una opcion de un panel que sigue
                # siendo parte de self._chain, la selecciona y lo trata
                # como si hubiera apretado Enter con foco ahi (misma
                # ejecucion/entrada a submenu, mismas reglas de marcado).
                col, row = self._last_click
                for r0, r1, c0, c1, node_c, idx_c in self._click_regions:
                    if r0 <= row < r1 and c0 <= col < c1 and node_c in self._chain:
                        node_c.index = idx_c
                        self._focus = self._chain.index(node_c)
                        key = b'\r'
                        break
            elif key == b'\x1b[HOVER' and self._last_hover and not self._preview:
                # Mismo hit-test que el click, pero solo mueve la
                # seleccion (resalta la opcion bajo el cursor), sin
                # ejecutar nada -- como pasar el mouse por arriba en un
                # menu de escritorio. Si el hover no cambia nada (ya
                # estaba resaltada esa opcion, o cayo fuera de cualquier
                # panel), `continue` se salta el resto de esta vuelta
                # entera para no limpiar/redibujar la pantalla por gusto
                # (el mouse manda MUCHOS eventos de movimiento seguidos).
                col, row = self._last_hover
                changed = False
                for r0, r1, c0, c1, node_c, idx_c in self._click_regions:
                    if r0 <= row < r1 and c0 <= col < c1 and node_c in self._chain:
                        if node_c.index != idx_c or self._chain[self._focus] is not node_c:
                            node_c.index = idx_c
                            self._focus = self._chain.index(node_c)
                            changed = True
                        break
                if not changed:
                    continue

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
                    panels.append((node,) + self._render_source_panel(node, size_max, style, cols))
                else:
                    panels.append((node,) + self._render_option_panel(node, size_max, style, depth == self._focus))
            if not self._preview and len(self._chain) < GRSubMenu.MAX_DEPTH:
                last = self._chain[-1]
                lookahead = last.functions[last.index]
                if isinstance(lookahead, GRSubMenu):
                    lookahead_style = getattr(lookahead, "style", None) or style
                    panels.append((lookahead,) + self._render_option_panel(lookahead, size_max, lookahead_style, focused=False))

            # Ancho de solo los paneles "entrados" (self._chain), sin el
            # preview automatico de la fila resaltada (si la hay). Es lo
            # que se usa para centrar: si se centrara contra el ancho
            # TOTAL (incluido el preview), el panel principal se correria
            # unos caracteres cada vez que el preview aparece/desaparece
            # (por ejemplo al pasar el mouse o las flechas sobre una fila
            # que es un GRSubMenu), lo que hace que el mouse "se sienta
            # raro" -- el click/hover del frame siguiente cae calculado
            # contra una posicion que ya no es la que el usuario ve. Con
            # chain_w el panel principal queda fijo; el preview solo se
            # agrega a la derecha, sin empujar nada mas.
            chain_w = sum(w for node_p, w, _, _ in panels if node_p in self._chain) + 2 * (len(self._chain) - 1)

            # Cuenta las filas que van imprimiendo banner/subtitulo, para
            # saber en que fila ABSOLUTA de la terminal arrancan los
            # paneles (lo necesita el hit-test de click, mas abajo).
            printed_rows = 0

            banner_w = 0
            if self.banner:
                bb = self.BORDERS().get(str(self.banner_style), self.BORDERS()["3"])
                rows = self.build_ascii_lines(self.banner, cols, self.SetStyle.font)
                if rows:
                    banner_w = max(len(r) for r in rows) + 6
                    bline = self._hline(bb["h"], banner_w - 2)
                    print(self._colorize_anim(bb["tl"] + bline + bb["tr"], self.SetStyle.banner, row=0))
                    for b_row, r in enumerate(rows, start=1):
                        print(self._colorize_anim(f"{bb['v']}  {r}  {bb['v']}", self.SetStyle.banner, row=b_row))
                    print(self._colorize_anim(bb["bl"] + bline + bb["br"], self.SetStyle.banner, row=len(rows) + 1))
                    printed_rows += len(rows) + 2
                else:
                    btext = self.banner.strip()
                    banner_w = min(len(btext) + 6, cols - 2)
                    bline = self._hline(bb["h"], banner_w - 2)
                    print(self._colorize_anim(bb["tl"] + bline + bb["tr"], self.SetStyle.banner, row=0))
                    print(self._colorize_anim(f"{bb['v']} {btext.center(banner_w - 4)} {bb['v']}", self.SetStyle.banner, row=1))
                    print(self._colorize_anim(bb["bl"] + bline + bb["br"], self.SetStyle.banner, row=2))
                    printed_rows += 3
                print()
                printed_rows += 1

            ref = banner_w or chain_w

            if self.subtitle:
                div_w = min(ref, cols - 2)
                if self.divider:
                    print(self._colorize("─" * div_w, self.SetStyle.divider))
                    printed_rows += 1
                sub_lines = self.subtitle.splitlines()
                for sub_line in sub_lines:
                    print(self._colorize(sub_line.center(div_w) if self.center else sub_line, self.SetStyle.subtitle))
                printed_rows += len(sub_lines)
                if self.divider:
                    print(self._colorize("─" * div_w, self.SetStyle.divider))
                    printed_rows += 1
                print()
                printed_rows += 1

            outer_pad = " " * ((ref - chain_w) // 2) if self.center and ref > chain_w else ""
            height = max(len(lines) for _, _, lines, _ in panels)

            # Columna (1-based, terminal) donde arranca cada panel.
            panel_cols = []
            col_cursor = len(outer_pad) + 1
            for _, w, _, _ in panels:
                panel_cols.append(col_cursor)
                col_cursor += w + 2  # +2 = separador "  " entre paneles

            click_regions = []
            for row_i in range(height):
                row_texts = []
                for (node_p, w, lines, targets), col_start in zip(panels, panel_cols):
                    row_texts.append(lines[row_i] if row_i < len(lines) else " " * w)
                    target = targets[row_i] if row_i < len(targets) else None
                    if target is not None:
                        abs_row = printed_rows + row_i + 1
                        click_regions.append((abs_row, abs_row + 1, col_start, col_start + w, node_p, target))
                print(outer_pad + "  ".join(row_texts))
            self._click_regions = click_regions

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
                        sys.stdout.write("\x1b[?1003l\x1b[?1000l")
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
    def _export_config_from_file(target) -> None:
        """Carga `target` (un script .py) y exporta a `.gr` la configuracion
        global (`GRmenu.SetStyle`) que haya quedado seteada, SIN arrancar
        ningun menu interactivo: corre el script completo tal cual (asi se
        ejecutan sus `SetStyle.Border(...)`, etc.), pero con `GRmenu.draw`
        reemplazado por un no-op mientras dura la carga, para que no se
        quede esperando teclas.

        Restaura la terminal (modo raw, cursor, reporte de mouse) al
        terminar, incluso si `target` construyo un `GRmenu(...)` (eso ya
        pone la terminal en modo crudo en `__init__`, antes de llegar a
        `draw`).

        Nota tecnica: cuando esto corre via `python -m GRmenu`, ESTE
        archivo se ejecuta como `sys.modules["__main__"]`, no como
        `sys.modules["GRmenu"]` -- asi que un `from GRmenu import GRmenu`
        dentro de `target` reimportaria el archivo de cero y definiria
        una clase `GRmenu` SEPARADA (con su propio `SetStyle`, sin el
        `draw` parcheado). Para que `target` use esta MISMA clase, se
        alias `sys.modules["GRmenu"]` a este modulo antes de cargarlo.
        """
        if not os.path.exists(target):
            print(GRmenu._colorize(f"No existe {target!r}.", {"color": "red", "level": 2}))
            return

        original_draw = GRmenu.draw
        GRmenu.draw = lambda self, *a, **kw: None
        this_module = sys.modules[__name__]
        had_grmenu_module = "GRmenu" in sys.modules
        original_grmenu_module = sys.modules.get("GRmenu")
        sys.modules["GRmenu"] = this_module
        saved_term = None
        if sys.platform != "win32" and sys.stdin.isatty():
            saved_term = termios.tcgetattr(sys.stdin.fileno())
        original_argv = sys.argv
        try:
            sys.argv = [target]
            runpy.run_path(target, run_name="__main__")
        finally:
            sys.argv = original_argv
            GRmenu.draw = original_draw
            if had_grmenu_module:
                sys.modules["GRmenu"] = original_grmenu_module
            else:
                del sys.modules["GRmenu"]
            if saved_term is not None:
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSAFLUSH, saved_term)
            sys.stdout.write("\x1b[?25h\x1b[?1003l\x1b[?1000l")
            sys.stdout.flush()

        out = os.path.splitext(os.path.abspath(target))[0] + ".gr"
        GRmenu.ExportConfig(out)
        print(GRmenu._colorize(f"Configuracion de {target} exportada a {out}", {"color": "green", "level": 2}))

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
        parser.add_argument("-ex", "--Export", metavar="archivo.py", help="Carga <archivo.py> sin arrancar su menu interactivo (menu.draw() no hace nada) y exporta la configuracion global (GRmenu.SetStyle) que haya quedado seteada a un .gr al lado de <archivo.py>.")
        args = parser.parse_args()

        if args.Export:
            GRmenu._export_config_from_file(args.Export)
        elif args.Example:
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


