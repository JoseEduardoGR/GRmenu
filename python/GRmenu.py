import math
import os
import sys
import termios
import tty
import json

class GRmenu():
    class GRprint:
        real_print = print

        @staticmethod
        def p(text,end='\r\n',**extra):
            GRmenu.GRprint.real_print(text, end=end,**extra)

        def setFixPrint():
            globals()['print'] = GRmenu.GRprint.p

    def __init__(self,functions : list,title="",style=19):
        self.D = sys.stdin.fileno() 
        self.DF = termios.tcgetattr(self.D)
        tty.setraw(self.D) 
        self.functions = functions
        self.style = style
        self.GRprint.setFixPrint()
        self.title = title
        self.index = 0
        self._clear_seq = "\x1b[H\x1b[2J\x1b[3J"

    def _up(self):
        self.index = (self.index - 1) % len(self.functions)
    def _down(self):
        self.index =  (self.index + 1) % len(self.functions)


    @staticmethod
    def STYLES():
        return {
            1:"#",2:"┌",3:"╔",4:"┏",5:"╒",6:"╓",7:"╭",8:"▛",
            9:"▓",10:"▒",11:"░",12:"█",13:"*",14:"+",15:"=",
            16:"~",17:"-",18:"◆",19:"●",20:"★"
        }

    _colors_cache = None

    @staticmethod
    def COLORS() -> dict:
        if GRmenu._colors_cache is None:
            path = os.path.join(os.path.dirname(__file__), "../data/colors.json")
            with open(path, encoding="utf-8") as fh:
                raw = json.load(fh)
            GRmenu._colors_cache = {
                name: ({level: f"\x1b[{code}" for level, code in codes.items()} if isinstance(codes, dict) else f"\x1b[{codes}")
                for name, codes in raw.items()
            }
        return GRmenu._colors_cache

    _borders_cache = None

    @staticmethod
    def BORDERS() -> dict:
        if GRmenu._borders_cache is None:
            path = os.path.join(os.path.dirname(__file__), "../data/borders.json")
            with open(path, encoding="utf-8") as fh:
                GRmenu._borders_cache = json.load(fh)
        return GRmenu._borders_cache
    
    class SetStyle:
        border = {"color": "cyan", "level": 1}
        options = {"color": "white", "level": 1}
        focus = {"color": "green", "level": 2}

        @staticmethod
        def Border(color, level=1):
            GRmenu.SetStyle.border = {"color": color, "level": level}

        @staticmethod
        def Options(color, level=1):
            GRmenu.SetStyle.options = {"color": color, "level": level}

        @staticmethod
        def Focus(color, level=2):
            GRmenu.SetStyle.focus = {"color": color, "level": level}

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
    def _fonts() -> dict:
        if GRmenu._fonts_cache is None:
            path = os.path.join(os.path.dirname(__file__), "../data/fonts.json")
            with open(path, encoding="utf-8") as fh:
                GRmenu._fonts_cache = json.load(fh)
        return GRmenu._fonts_cache

    @staticmethod
    def build_ascii_lines(text, max_cols, font_id=1) -> Optional[list]:
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
        print("Press any key to start ...")

    def draw(self,size_max=20):
        self.menu()
        while (key := os.read(self.D,3)) != b'q':
            print(self._clear_seq, end="")

            self._up() if key==b'\x1b[A' else None # up
            self._down() if key==b'\x1b[B' else None # down

            #print("right",end="\r\f") if key==b'\x1b[C' else None # right
            #print("left",end="\r\f") if key==b'\x1b[D' else None # left

            names = [getattr(f, "__name__", str(f)) for f in self.functions]
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
                    print(f"{v} {self.title.center(width - 4)} {v}")
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
                    print(f"{border} {self.title.center(width - 4)} {border}")
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
                self.functions[self.index]()
                break


