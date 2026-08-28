import math
import os
import sys
import termios
import tty

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

    @staticmethod
    def COLORS():
        return {
            "black":  {1: "\x1b[30m", 2: "\x1b[90m"},
            "red":    {1: "\x1b[31m", 2: "\x1b[91m"},
            "green":  {1: "\x1b[32m", 2: "\x1b[92m"},
            "yellow": {1: "\x1b[33m", 2: "\x1b[93m"},
            "blue":   {1: "\x1b[34m", 2: "\x1b[94m"},
            "magenta":{1: "\x1b[35m", 2: "\x1b[95m"},
            "cyan":   {1: "\x1b[36m", 2: "\x1b[96m"},
            "white":  {1: "\x1b[37m", 2: "\x1b[97m"},
            "reset": "\x1b[0m",
        }

    @staticmethod
    def BORDERS():
        return {
            1: dict(h="=-", v="|", tl="#", tr="#", bl="#", br="#"),
            2: dict(h="─", v="│", tl="┌", tr="┐", bl="└", br="┘"),
            3: dict(h="═", v="║", tl="╔", tr="╗", bl="╚", br="╝"),
            4: dict(h="━", v="┃", tl="┏", tr="┓", bl="┗", br="┛"),
            5: dict(h="═", v="│", tl="╒", tr="╕", bl="╘", br="╛"),
            6: dict(h="─", v="║", tl="╓", tr="╖", bl="╙", br="╜"),
            7: dict(h="─", v="│", tl="╭", tr="╮", bl="╰", br="╯"),
            8: dict(h="▀", v="▌", tl="▛", tr="▜", bl="▙", br="▟"),
            19: dict(h="●○", v="●", tl="●", tr="●", bl="●", br="●"),
            20: dict(h="★☆", v="★", tl="★", tr="★", bl="★", br="★"),
        }
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
        code = colors.get(color_cfg["color"], {}).get(color_cfg["level"], "")
        if not code:
            return text
        return f"{code}{text}{colors['reset']}"

    @staticmethod
    def _hline(h, width):
        return (h * (width // len(h) + 1))[:width]


    def menu(self):
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
            bc, oc, fc = self.SetStyle.border, self.SetStyle.options, self.SetStyle.focus
            box_border = self.BORDERS().get(self.style)
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


