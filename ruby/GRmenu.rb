# frozen_string_literal: true

require 'io/console'
require 'json'

class GRmenu
  CLEAR_SCREEN_SEQUENCE = "\e[H\e[2J\e[3J"
  HIDE_CURSOR           = "\e[?25l"
  SHOW_CURSOR           = "\e[?25h"
  CURSOR_HOME           = "\e[H"
  CLEAR_TO_EOL          = "\e[K"
  CLEAR_TO_EOS          = "\e[J"

  module Color
    RESET = "\e[0m"
    BOLD  = "\e[1m"

    CODES = {
      black:          { 1 => "\e[30m", 2 => "\e[90m" },
      gray:           { 1 => "\e[90m", 2 => "\e[38;5;245m" },
      grey:           { 1 => "\e[90m", 2 => "\e[38;5;245m" },
      red:            { 1 => "\e[31m", 2 => "\e[91m" },
      green:          { 1 => "\e[32m", 2 => "\e[92m" },
      yellow:         { 1 => "\e[33m", 2 => "\e[93m" },
      blue:           { 1 => "\e[34m", 2 => "\e[94m" },
      magenta:        { 1 => "\e[35m", 2 => "\e[95m" },
      purple:         { 1 => "\e[38;5;129m", 2 => "\e[38;5;141m" },
      pink:           { 1 => "\e[38;5;205m", 2 => "\e[38;5;218m" },
      cyan:           { 1 => "\e[36m", 2 => "\e[96m" },
      aqua:           { 1 => "\e[38;5;45m",  2 => "\e[38;5;51m" },
      orange:         { 1 => "\e[38;5;208m", 2 => "\e[38;5;214m" },
      white:          { 1 => "\e[37m", 2 => "\e[97m" }
    }.freeze

    module_function

    def paint(text, color_name, level = 1)
      code = CODES.dig(color_name.to_sym, level) || "\e[37m"
      "#{code}#{text}#{RESET}"
    end

    def red(s)            = paint(s, :red, 1)
    def bright_red(s)     = paint(s, :red, 2)
    def dark_red(s)       = paint(s, :red, 1)

    def green(s)          = paint(s, :green, 1)
    def bright_green(s)   = paint(s, :green, 2)
    def dark_green(s)     = paint(s, :green, 1)

    def yellow(s)         = paint(s, :yellow, 1)
    def bright_yellow(s)  = paint(s, :yellow, 2)

    def blue(s)           = paint(s, :blue, 1)
    def bright_blue(s)    = paint(s, :blue, 2)

    def magenta(s)        = paint(s, :magenta, 1)
    def bright_magenta(s) = paint(s, :magenta, 2)

    def purple(s)         = paint(s, :purple, 1)
    def bright_purple(s)  = paint(s, :purple, 2)

    def pink(s)           = paint(s, :pink, 1)
    def bright_pink(s)    = paint(s, :pink, 2)

    def cyan(s)           = paint(s, :cyan, 1)
    def bright_cyan(s)    = paint(s, :cyan, 2)

    def aqua(s)           = paint(s, :aqua, 1)
    def bright_aqua(s)    = paint(s, :aqua, 2)

    def orange(s)         = paint(s, :orange, 1)
    def bright_orange(s)  = paint(s, :orange, 2)

    def white(s)          = paint(s, :white, 1)
    def bright_white(s)   = paint(s, :white, 2)

    def black(s)          = paint(s, :black, 1)
    def gray(s)           = paint(s, :gray, 1)
    def bright_gray(s)    = paint(s, :gray, 2)
    def grey(s)           = gray(s)

    def r(s)  = bright_red(s)
    def dr(s) = dark_red(s)
    def g(s)  = bright_green(s)
    def y(s)  = bright_yellow(s)
    def w(s)  = bright_white(s)
    def gr(s) = gray(s)
    def cy(s) = bright_cyan(s)
    def mg(s) = bright_magenta(s)
    def bl(s) = bright_blue(s)
  end
  C = Color

  STYLES = {
    1  => "#", 2  => "┌", 3  => "╔", 4  => "┏", 5  => "╒",
    6  => "╓", 7  => "╭", 8  => "▛", 9  => "▓", 10 => "▒",
    11 => "░", 12 => "█", 13 => "*", 14 => "+", 15 => "=",
    16 => "~", 17 => "-", 18 => "◆", 19 => "●", 20 => "★"
  }.freeze

  COLORS = {
    "black"          => { 1 => "\e[30m", 2 => "\e[90m" },
    "gray"           => { 1 => "\e[90m", 2 => "\e[38;5;245m" },
    "grey"           => { 1 => "\e[90m", 2 => "\e[38;5;245m" },
    "red"            => { 1 => "\e[31m", 2 => "\e[91m" },
    "green"          => { 1 => "\e[32m", 2 => "\e[92m" },
    "yellow"         => { 1 => "\e[33m", 2 => "\e[93m" },
    "blue"           => { 1 => "\e[34m", 2 => "\e[94m" },
    "magenta"        => { 1 => "\e[35m", 2 => "\e[95m" },
    "purple"         => { 1 => "\e[38;5;129m", 2 => "\e[38;5;141m" },
    "pink"           => { 1 => "\e[38;5;205m", 2 => "\e[38;5;218m" },
    "cyan"           => { 1 => "\e[36m", 2 => "\e[96m" },
    "aqua"           => { 1 => "\e[38;5;45m",  2 => "\e[38;5;51m" },
    "orange"         => { 1 => "\e[38;5;208m", 2 => "\e[38;5;214m" },
    "white"          => { 1 => "\e[37m", 2 => "\e[97m" },
    "reset"          => "\e[0m"
  }.freeze

  BORDERS = {
    1  => { h: "=-", v: "|", tl: "#", tr: "#", bl: "#", br: "#" },
    2  => { h: "─",  v: "│", tl: "┌", tr: "┐", bl: "└", br: "┘" },
    3  => { h: "═",  v: "║", tl: "╔", tr: "╗", bl: "╚", br: "╝" },
    4  => { h: "━",  v: "┃", tl: "┏", tr: "┓", bl: "┗", br: "┛" },
    5  => { h: "═",  v: "│", tl: "╒", tr: "╕", bl: "╘", br: "╛" },
    6  => { h: "─",  v: "║", tl: "╓", tr: "╖", bl: "╙", br: "╜" },
    7  => { h: "─",  v: "│", tl: "╭", tr: "╮", bl: "╰", br: "╯" },
    8  => { h: "▀", hb: "▄", v: "▌", vl: "▌", vr: "▐", tl: "▛", tr: "▜", bl: "▙", br: "▟" },
    19 => { h: "●○", v: "●", tl: "●", tr: "●", bl: "●", br: "●" },
    20 => { h: "★☆", v: "★", tl: "★", tr: "★", bl: "★", br: "★" }
  }.freeze

  def self._normalize_font(f)
    normalized = {}
    f.each do |key, lines|
      max_w = lines.map(&:length).max
      normalized[key] = lines.map { |line| line.ljust(max_w) }.freeze
    end
    normalized.freeze
  end

  def self._load_fonts
    possible_paths = [
      File.expand_path("data/fonts.json", __dir__),
      File.expand_path("../data/fonts.json", __dir__),
      File.expand_path("fonts.json", __dir__)
    ]
    path = possible_paths.find { |p| File.file?(p) }
    return {}.freeze unless path

    raw_fonts = JSON.parse(File.read(path))
    loaded = {}
    raw_fonts.each do |font_key, chars|
      font_id = font_key.to_i
      loaded[font_id] = _normalize_font(chars)
    end
    loaded.freeze
  rescue StandardError
    {}.freeze
  end

  FONTS = _load_fonts
  FONTS.each { |id, data| const_set("FONT_#{id}", data) }
  FONT = FONTS[1] || {}.freeze

  class SetStyle
    def initialize(
      border:   { color: "cyan",    level: 1 },
      options:  { color: "white",   level: 1 },
      focus:    { color: "green",   level: 2 },
      title:    { color: "yellow",  level: 2 },
      banner:   { color: "magenta", level: 2 },
      subtitle: { color: "cyan",    level: 2 },
      divider:  { color: "blue",    level: 1 },
      font:     1
    )
      @border   = border.dup
      @options  = options.dup
      @focus    = focus.dup
      @title    = title.dup
      @banner   = banner.dup
      @subtitle = subtitle.dup
      @divider  = divider.dup
      @font     = font.to_i
    end

    def border(color_name = nil, brightness_level = 1)
      return @border if color_name.nil?
      @border = parse_color(color_name, brightness_level)
    end
    alias_method :Border, :border
    alias_method :set_border, :border
    alias_method :border=, :border

    def options(color_name = nil, brightness_level = 1)
      return @options if color_name.nil?
      @options = parse_color(color_name, brightness_level)
    end
    alias_method :Options, :options
    alias_method :set_options, :options
    alias_method :options=, :options

    def focus(color_name = nil, brightness_level = 2)
      return @focus if color_name.nil?
      @focus = parse_color(color_name, brightness_level)
    end
    alias_method :Focus, :focus
    alias_method :set_focus, :focus
    alias_method :focus=, :focus

    def title(color_name = nil, brightness_level = 2)
      return @title if color_name.nil?
      @title = parse_color(color_name, brightness_level)
    end
    alias_method :Title, :title
    alias_method :set_title, :title
    alias_method :title=, :title

    def banner(color_name = nil, brightness_level = 2)
      return @banner if color_name.nil?
      @banner = parse_color(color_name, brightness_level)
    end
    alias_method :Banner, :banner
    alias_method :set_banner, :banner
    alias_method :banner=, :banner

    def subtitle(color_name = nil, brightness_level = 2)
      return @subtitle if color_name.nil?
      @subtitle = parse_color(color_name, brightness_level)
    end
    alias_method :Subtitle, :subtitle
    alias_method :set_subtitle, :subtitle
    alias_method :subtitle=, :subtitle

    def divider(color_name = nil, brightness_level = 1)
      return @divider if color_name.nil?
      @divider = parse_color(color_name, brightness_level)
    end
    alias_method :Divider, :divider
    alias_method :set_divider, :divider
    alias_method :divider=, :divider

    def font(font_id = nil)
      return @font if font_id.nil?
      @font = font_id.to_i
    end
    alias_method :Font, :font
    alias_method :set_font, :font
    alias_method :font=, :font

    private

    def parse_color(color_val, default_level = 1)
      if color_val.is_a?(Hash)
        { color: (color_val[:color] || color_val["color"]).to_s, level: (color_val[:level] || color_val["level"] || default_level).to_i }
      else
        { color: color_val.to_s, level: default_level.to_i }
      end
    end

    class << self
      def border(color_name = nil, brightness_level = 1)
        @default_border ||= { color: "cyan", level: 1 }
        return @default_border if color_name.nil?
        @default_border = { color: color_name.to_s, level: brightness_level.to_i }
      end
      alias_method :Border, :border
      alias_method :border=, :border

      def options(color_name = nil, brightness_level = 1)
        @default_options ||= { color: "white", level: 1 }
        return @default_options if color_name.nil?
        @default_options = { color: color_name.to_s, level: brightness_level.to_i }
      end
      alias_method :Options, :options
      alias_method :options=, :options

      def focus(color_name = nil, brightness_level = 2)
        @default_focus ||= { color: "green", level: 2 }
        return @default_focus if color_name.nil?
        @default_focus = { color: color_name.to_s, level: brightness_level.to_i }
      end
      alias_method :Focus, :focus
      alias_method :focus=, :focus

      def title(color_name = nil, brightness_level = 2)
        @default_title ||= { color: "yellow", level: 2 }
        return @default_title if color_name.nil?
        @default_title = { color: color_name.to_s, level: brightness_level.to_i }
      end
      alias_method :Title, :title
      alias_method :title=, :title

      def banner(color_name = nil, brightness_level = 2)
        @default_banner ||= { color: "magenta", level: 2 }
        return @default_banner if color_name.nil?
        @default_banner = { color: color_name.to_s, level: brightness_level.to_i }
      end
      alias_method :Banner, :banner
      alias_method :banner=, :banner

      def subtitle(color_name = nil, brightness_level = 2)
        @default_subtitle ||= { color: "cyan", level: 2 }
        return @default_subtitle if color_name.nil?
        @default_subtitle = { color: color_name.to_s, level: brightness_level.to_i }
      end
      alias_method :Subtitle, :subtitle
      alias_method :subtitle=, :subtitle

      def divider(color_name = nil, brightness_level = 1)
        @default_divider ||= { color: "blue", level: 1 }
        return @default_divider if color_name.nil?
        @default_divider = { color: color_name.to_s, level: brightness_level.to_i }
      end
      alias_method :Divider, :divider
      alias_method :divider=, :divider

      def font(font_id = nil)
        @default_font ||= 1
        return @default_font if font_id.nil?
        @default_font = font_id.to_i
      end
      alias_method :Font, :font
      alias_method :set_font, :font
      alias_method :font=, :font
    end
  end

  module GRprint
    module_function

    def p(text = "", ending = "\r\n")
      Kernel.print("#{text}#{ending}")
    end
  end

  attr_accessor :functions, :title, :subtitle, :banner, :banner_style, :divider, :style, :index, :style_config, :center

  alias_method :options, :functions
  alias_method :options=, :functions=
  alias_method :selected_index, :index
  alias_method :selected_index=, :index=
  alias_method :SetStyle, :style_config
  alias_method :set_style, :style_config
  alias_method :description, :subtitle
  alias_method :description=, :subtitle=

  def self.STYLES = STYLES
  def self.COLORS = COLORS
  def self.BORDERS = BORDERS
  def self.FONTS = FONTS
  def self.FONT = FONT_1

  def self.terminal_width
    cols = $stdout.winsize[1] rescue nil
    cols = $stdin.winsize[1] rescue nil if cols.nil? || cols <= 0
    (cols && cols > 0) ? cols : (ENV['COLUMNS'] ? ENV['COLUMNS'].to_i : 80)
  rescue StandardError
    80
  end

  def self.clear_screen
    Kernel.print(CLEAR_SCREEN_SEQUENCE)
  end
  class << self
    alias_method :clr, :clear_screen
  end

  def self.div(long = nil, color = "blue", level = 1, char = "─")
    width = long || [terminal_width - 2, 64].min
    color_code = COLORS.dig(color.to_s.downcase, level) || "\e[34m"
    Kernel.print("#{color_code}#{char * width}#{COLORS['reset']}\r\n")
  end

  def self.help
    w = [terminal_width - 4, 64].min
    w = [w, 42].max
    inner_w = w - 2
    h_line = "═" * inner_w
    s_line = "─" * w

    Kernel.print "\r\n"
    Kernel.print "#{Color.bright_cyan("╔" + h_line + "╗")}\r\n"
    Kernel.print "#{Color.bright_cyan("║")}#{Color.bright_yellow("GRmenu - Guia y Referencia Rapida".center(inner_w))}#{Color.bright_cyan("║")}\r\n"
    Kernel.print "#{Color.bright_cyan("║")}#{Color.gray("Navegacion interactiva en terminal TTY".center(inner_w))}#{Color.bright_cyan("║")}\r\n"
    Kernel.print "#{Color.bright_cyan("╚" + h_line + "╝")}\r\n\r\n"

    Kernel.print "#{Color.bright_magenta("[1] HELPERS NATIVOS EN MODO CRUDO")}\r\n"
    Kernel.print "#{Color.bright_blue(s_line)}\r\n"
    Kernel.print "  #{Color.bright_green("GRmenu.clear_screen")} #{Color.gray("(o GRmenu.clr)")}\r\n"
    Kernel.print "    * Limpia la terminal al instante con secuencias ANSI.\r\n"
    Kernel.print "  #{Color.bright_green("GRmenu.continue(mensaje)")}\r\n"
    Kernel.print "    * Pausa interactiva: espera una sola tecla en modo TTY crudo.\r\n"
    Kernel.print "  #{Color.bright_green("GRmenu.banner(texto, delay, color:, level:, style:, font:)")}\r\n"
    Kernel.print "    * Renderiza banner ASCII 3D con marco y animacion opcional.\r\n"
    Kernel.print "  #{Color.bright_green("GRmenu.div(longitud, color, level, char)")}\r\n"
    Kernel.print "    * Dibuja linea divisoria horizontal adaptable a la consola.\r\n"
    Kernel.print "  #{Color.bright_green("GRmenu.help")}\r\n"
    Kernel.print "    * Imprime esta guia visual interactiva en consola.\r\n\r\n"

    Kernel.print "#{Color.bright_magenta("[2] MODULO DE COLORES (Color / C)")}\r\n"
    Kernel.print "#{Color.bright_blue(s_line)}\r\n"
    Kernel.print "  #{Color.cyan("Uso directo: ")}#{Color.bright_white("puts Color.green(\"Texto\")")} | #{Color.bright_white("puts Color.bright_cyan(\"Texto\")")}\r\n"
    Kernel.print "  #{Color.cyan("Paleta: ")}#{Color.red("red")}, #{Color.green("green")}, #{Color.yellow("yellow")}, #{Color.blue("blue")}, #{Color.magenta("magenta")}, #{Color.purple("purple")}, #{Color.pink("pink")}, #{Color.cyan("cyan")}, #{Color.aqua("aqua")}, #{Color.orange("orange")}, #{Color.white("white")}, #{Color.gray("gray")}, #{Color.black("black")}.\r\n"
    Kernel.print "  #{Color.cyan("Brillo: ")}#{Color.white("1")} = Normal, #{Color.bright_white("2")} = Brillante / Bold.\r\n\r\n"

    Kernel.print "#{Color.bright_magenta("[3] FUENTES ASCII 3D DEL BANNER (font: 1 al 10)")}\r\n"
    Kernel.print "#{Color.bright_blue(s_line)}\r\n"
    Kernel.print "  #{Color.yellow("1")} -> #{Color.bright_white("ANSI Shadow 3D (Default)")}  #{Color.cyan("[██████╗  ██╗  ██╗]")}\r\n"
    Kernel.print "  #{Color.yellow("2")} -> #{Color.bright_white("Slant 3D (FIGlet)")}          #{Color.cyan("[    ____        __  __]")}\r\n"
    Kernel.print "  #{Color.yellow("3")} -> #{Color.bright_white("Doom / Standard 3D")}        #{Color.cyan("[   ____      _   _]")}\r\n"
    Kernel.print "  #{Color.yellow("4")} -> #{Color.bright_white("Graffiti Shadow 3D")}        #{Color.cyan("[  ,---.      ,--. ,--.]")}\r\n"
    Kernel.print "  #{Color.yellow("5")} -> #{Color.bright_white("Small Slant / Mini 3D")}     #{Color.cyan("[   ___     _ _]")}\r\n"
    Kernel.print "  #{Color.yellow("6")} -> #{Color.bright_white("Modular Pipe 3D")}           #{Color.cyan("[   _____    _____]")}\r\n"
    Kernel.print "  #{Color.yellow("7")} -> #{Color.bright_white("Bubble / Round Gothic")}      #{Color.cyan("[    ____     _  _]")}\r\n"
    Kernel.print "  #{Color.yellow("8")} -> #{Color.bright_white("Double-Line Wire 3D")}      #{Color.cyan("[  ╔═════╗  ║     ║]")}\r\n"
    Kernel.print "  #{Color.yellow("9")} -> #{Color.bright_white("Solid Fat 3D Block")}       #{Color.cyan("[  ██████▄  ██   ██]")}\r\n"
    Kernel.print "  #{Color.yellow("10")}-> #{Color.bright_white("Arcade Stars Matrix")}       #{Color.cyan("[  ★★★★   ★   ★]")}\r\n\r\n"

    Kernel.print "#{Color.bright_magenta("[4] ESTILOS DE MARCO (style / banner_style: 1 al 20)")}\r\n"
    Kernel.print "#{Color.bright_blue(s_line)}\r\n"
    Kernel.print "  #{Color.yellow("3")}  -> #{Color.bright_white("Doble linea")}        #{Color.cyan("╔═══╗ ║   ║ ╚═══╝")} (Default en Banner)\r\n"
    Kernel.print "  #{Color.yellow("7")}  -> #{Color.bright_white("Curvas redondeadas")} #{Color.cyan("╭───╮ │   │ ╰───╯")}\r\n"
    Kernel.print "  #{Color.yellow("4")}  -> #{Color.bright_white("Linea gruesa")}       #{Color.cyan("┏━━━┓ ┃   ┃ ┗━━━┛")}\r\n"
    Kernel.print "  #{Color.yellow("2")}  -> #{Color.bright_white("Linea simple")}       #{Color.cyan("┌───┐ │   │ └───┘")}\r\n"
    Kernel.print "  #{Color.yellow("8")}  -> #{Color.bright_white("Bloques outline")}    #{Color.cyan("▛▀▀▀▜ ▌   ▌ ▙▄▄▄▟")}\r\n"
    Kernel.print "  #{Color.yellow("19")} -> #{Color.bright_white("Circulos")}           #{Color.cyan("●○○○● ●   ● ●○○○●")} (Default en Opciones)\r\n"
    Kernel.print "  #{Color.yellow("20")} -> #{Color.bright_white("Estrellas")}          #{Color.cyan("★☆☆☆★ ★   ★ ★☆☆☆★")}\r\n\r\n"

    Kernel.print "#{Color.bright_magenta("[5] PARAMETROS DE GRmenu.new(functions, ...)")}\r\n"
    Kernel.print "#{Color.bright_blue(s_line)}\r\n"
    Kernel.print "  #{Color.bright_green("banner:")}       #{Color.white("String")}  -> Texto grande a renderizar en arte ASCII 3D.\r\n"
    Kernel.print "  #{Color.bright_green("title:")}        #{Color.white("String")}  -> Titulo en el encabezado del recuadro.\r\n"
    Kernel.print "  #{Color.bright_green("subtitle:")}     #{Color.white("String")}  -> Subtitulo / descripcion (soporta \\n).\r\n"
    Kernel.print "  #{Color.bright_green("font:")}         #{Color.white("Integer")} -> Fuente ASCII del banner (1 al 10, default 1).\r\n"
    Kernel.print "  #{Color.bright_green("style:")}        #{Color.white("Integer")} -> Estilo de marco de opciones (1 al 20, default 19).\r\n"
    Kernel.print "  #{Color.bright_green("banner_style:")} #{Color.white("Integer")} -> Estilo de marco del banner (1 al 20, default 3).\r\n"
    Kernel.print "  #{Color.bright_green("divider:")}      #{Color.white("Boolean")} -> Divisores alineados al banner (true/false).\r\n"
    Kernel.print "  #{Color.bright_green("center:")}       #{Color.white("Boolean")} -> Centrado simetrico de subtitulo y menu (default true).\r\n\r\n"

    Kernel.print "#{Color.bright_magenta("[6] METODOS DE CONFIGURACION (menu.set_style)")}\r\n"
    Kernel.print "#{Color.bright_blue(s_line)}\r\n"
    Kernel.print "  #{Color.cyan("menu.set_style.font(id)")}                 -> Cambia fuente ASCII (1..10)\r\n"
    Kernel.print "  #{Color.cyan("menu.set_style.banner(color, level)")}     -> Color y brillo del banner ASCII\r\n"
    Kernel.print "  #{Color.cyan("menu.set_style.title(color, level)")}      -> Color y brillo del titulo\r\n"
    Kernel.print "  #{Color.cyan("menu.set_style.subtitle(color, level)")}   -> Color y brillo del subtitulo\r\n"
    Kernel.print "  #{Color.cyan("menu.set_style.divider(color, level)")}    -> Color y brillo de las lineas divisorias\r\n"
    Kernel.print "  #{Color.cyan("menu.set_style.border(color, level)")}     -> Color y brillo del marco de opciones\r\n"
    Kernel.print "  #{Color.cyan("menu.set_style.options(color, level)")}    -> Color y brillo de opciones no activas\r\n"
    Kernel.print "  #{Color.cyan("menu.set_style.focus(color, level)")}      -> Color y brillo de la opcion resaltada\r\n\r\n"

    Kernel.print "#{Color.bright_magenta("[7] EJECUCION (menu.draw)")}\r\n"
    Kernel.print "#{Color.bright_blue(s_line)}\r\n"
    Kernel.print "  #{Color.bright_white("menu.draw(size_max: 38)")} -> Inicia el menu interactivo con ancho minimo.\r\n"
    Kernel.print "#{Color.bright_blue(s_line)}\r\n\r\n"
  end

  def help
    self.class.help
  end

  def self.continue(text = "Presiona cualquier tecla para continuar...")
    Kernel.print("#{Color.gray(text)} ")
    if $stdin.respond_to?(:raw) && $stdin.respond_to?(:tty?) && $stdin.tty?
      $stdin.raw(&:getch)
    elsif $stdin.respond_to?(:getch)
      $stdin.getch
    else
      $stdin.read(1)
    end
    Kernel.print("\r\n")
  end

  def self.build_ascii_lines(text, max_cols = terminal_width, font_id = 1)
    target_font = FONTS[font_id.to_i] || FONTS[1]
    clean_chars = text.to_s.upcase.chars.select { |c| target_font.key?(c) }
    return [] if clean_chars.empty?

    font_height = target_font.values.first.length

    [2, 1, 0].each do |spacing|
      lines = Array.new(font_height, "")
      clean_chars.each_with_index do |c, idx|
        fig = target_font[c]
        pad = (idx == clean_chars.length - 1) ? "" : (" " * spacing)
        font_height.times { |i| lines[i] += fig[i] + pad }
      end

      max_len = lines.map(&:length).max
      return lines if (max_len + 6) <= max_cols
    end

    nil
  end

  def self.banner(text, delay = 0, color: "magenta", level: 2, style: 3, font: 1)
    cols = terminal_width
    color_code = COLORS.dig(color.to_s.downcase, level) || "\e[1;95m"
    reset_code = COLORS["reset"]

    ascii_rows = build_ascii_lines(text, cols, font)
    border_cfg = BORDERS[style] || BORDERS[3]

    if ascii_rows
      max_len = ascii_rows.map(&:length).max
      h_fill = (border_cfg[:h] * ((max_len + 4).to_f / border_cfg[:h].length).ceil)[0...(max_len + 4)]
      
      Kernel.print("#{color_code}#{border_cfg[:tl]}#{h_fill}#{border_cfg[:tr]}#{reset_code}\r\n")
      ascii_rows.each do |line|
        pad = " " * (max_len - line.length)
        Kernel.print("#{color_code}#{border_cfg[:v]}  #{line}#{pad}  #{border_cfg[:v]}#{reset_code}\r\n")
        sleep(delay) if delay > 0
      end
      Kernel.print("#{color_code}#{border_cfg[:bl]}#{h_fill}#{border_cfg[:br]}#{reset_code}\r\n")
    else
      clean_t = text.to_s.strip
      box_w = [clean_t.length + 6, cols - 2].min
      h_fill = (border_cfg[:h] * ((box_w - 2).to_f / border_cfg[:h].length).ceil)[0...(box_w - 2)]
      Kernel.print("#{color_code}#{border_cfg[:tl]}#{h_fill}#{border_cfg[:tr]}#{reset_code}\r\n")
      Kernel.print("#{color_code}#{border_cfg[:v]} #{clean_t.center(box_w - 4)} #{border_cfg[:v]}#{reset_code}\r\n")
      Kernel.print("#{color_code}#{border_cfg[:bl]}#{h_fill}#{border_cfg[:br]}#{reset_code}\r\n")
    end
  end

  class << self
    alias_method :message, :banner
    alias_method :logo, :banner
  end

  def initialize(functions, *positional_arguments, title: nil, banner: nil, subtitle: nil, description: nil, divider: nil, style: nil, banner_style: nil, center: true, font: nil, **keyword_arguments)
    @functions = functions.is_a?(Array) ? functions : Array(functions)

    pos_title = positional_arguments[0]
    pos_style = positional_arguments[1]

    @title        = (title || pos_title || keyword_arguments[:title] || "").to_s
    @banner       = (banner || keyword_arguments[:banner] || "").to_s
    @subtitle     = (subtitle || description || keyword_arguments[:subtitle] || keyword_arguments[:description] || "").to_s
    @divider      = divider.nil? ? (!@banner.empty? || !@subtitle.empty?) : divider
    @style        = (style || pos_style || keyword_arguments[:style] || 19).to_i
    @banner_style = (banner_style || keyword_arguments[:banner_style] || 3).to_i
    @center       = center.nil? ? true : center
    @index        = 0
    @clear_seq    = CLEAR_SCREEN_SEQUENCE

    init_font = font || keyword_arguments[:font_style] || SetStyle.font || 1

    @style_config = SetStyle.new(
      border:   SetStyle.border.dup,
      options:  SetStyle.options.dup,
      focus:    SetStyle.focus.dup,
      title:    SetStyle.title.dup,
      banner:   SetStyle.banner.dup,
      subtitle: SetStyle.subtitle.dup,
      divider:  SetStyle.divider.dup,
      font:     init_font
    )
  end

  def move_up
    return @index if @functions.empty?
    @index = (@index - 1) % @functions.length
  end
  alias_method :_up, :move_up

  def move_down
    return @index if @functions.empty?
    @index = (@index + 1) % @functions.length
  end
  alias_method :_down, :move_down

  def colorize(text, color_config)
    return text.to_s if color_config.nil? || color_config.empty?

    color_name = (color_config[:color] || color_config["color"]).to_s.downcase
    brightness_level = (color_config[:level] || color_config["level"] || 1).to_i

    color_code = COLORS.dig(color_name, brightness_level)
    return text.to_s unless color_code

    "#{color_code}#{text}#{COLORS['reset']}"
  end
  alias_method :_colorize, :colorize

  def build_horizontal_line(pattern, target_width)
    return "" if target_width <= 0 || pattern.nil? || pattern.empty?

    pattern_length = pattern.length
    repetitions_needed = (target_width.to_f / pattern_length).ceil + 1
    (pattern * repetitions_needed)[0...target_width]
  end
  alias_method :_hline, :build_horizontal_line

  def render_banner_lines(term_cols)
    return [[], 0] if @banner.nil? || @banner.empty?

    font_id = @style_config.font || 1
    ascii_rows = self.class.build_ascii_lines(@banner, term_cols, font_id)
    banner_border = BORDERS[@banner_style] || BORDERS[3]
    banner_color_cfg = @style_config.banner

    lines = []
    box_w = 0
    h_top = banner_border[:ht] || banner_border[:h]
    h_bot = banner_border[:hb] || banner_border[:h]
    v_l = banner_border[:vl] || banner_border[:v]
    v_r = banner_border[:vr] || banner_border[:v]

    if ascii_rows
      content_w = ascii_rows.map(&:length).max
      box_w = content_w + 6
      top_fill = build_horizontal_line(h_top, content_w + 4)
      bot_fill = build_horizontal_line(h_bot, content_w + 4)
      
      lines << colorize("#{banner_border[:tl]}#{top_fill}#{banner_border[:tr]}", banner_color_cfg)
      ascii_rows.each do |row|
        pad = " " * (content_w - row.length)
        lines << colorize("#{v_l}  #{row}#{pad}  #{v_r}", banner_color_cfg)
      end
      lines << colorize("#{banner_border[:bl]}#{bot_fill}#{banner_border[:br]}", banner_color_cfg)
    else
      clean_b = @banner.strip
      box_w = [clean_b.length + 6, term_cols - 2].min
      top_fill = build_horizontal_line(h_top, box_w - 2)
      bot_fill = build_horizontal_line(h_bot, box_w - 2)
      
      lines << colorize("#{banner_border[:tl]}#{top_fill}#{banner_border[:tr]}", banner_color_cfg)
      lines << colorize("#{v_l} #{clean_b.center(box_w - 4)} #{v_r}", banner_color_cfg)
      lines << colorize("#{banner_border[:bl]}#{bot_fill}#{banner_border[:br]}", banner_color_cfg)
    end
    [lines, box_w]
  end

  def render_lines(size_max = 20)
    term_cols = self.class.terminal_width
    rendered_lines = []

    banner_box_width = 0
    if @banner && !@banner.empty?
      banner_lines, banner_box_width = render_banner_lines(term_cols)
      rendered_lines.concat(banner_lines)
      rendered_lines << ""
    end

    option_names = @functions.map { |func| extract_name_from_action(func) }
    calculated_width = [size_max, @title.length + 4].max
    calculated_width = ([calculated_width] + option_names.map { |name| name.length + 6 }).max
    total_width = [calculated_width, term_cols - 2].min

    reference_width = banner_box_width > 0 ? banner_box_width : total_width
    margin_left = (@center && reference_width > total_width) ? " " * ((reference_width - total_width) / 2) : ""

    if @subtitle && !@subtitle.empty?
      subtitle_lines = @subtitle.lines.map(&:chomp)
      div_w = @divider.is_a?(Numeric) ? @divider.to_i : [reference_width, term_cols - 2].min

      if @divider
        rendered_lines << colorize("─" * div_w, @style_config.divider)
      end

      subtitle_lines.each do |sub_line|
        formatted_sub = @center ? sub_line.center(div_w) : sub_line
        rendered_lines << colorize(formatted_sub, @style_config.subtitle)
      end

      if @divider
        rendered_lines << colorize("─" * div_w, @style_config.divider)
      end
      rendered_lines << ""
    end

    border_color_cfg  = @style_config.border
    options_color_cfg = @style_config.options
    focus_color_cfg   = @style_config.focus
    title_color_cfg   = @style_config.title

    box_border = BORDERS[@style]

    if box_border
      h_top = box_border[:ht] || box_border[:h]
      h_bot = box_border[:hb] || box_border[:h]
      v_l_raw = box_border[:vl] || box_border[:v]
      v_r_raw = box_border[:vr] || box_border[:v]

      top_fill = build_horizontal_line(h_top, total_width - 2)
      bot_fill = build_horizontal_line(h_bot, total_width - 2)
      mid_fill = build_horizontal_line(h_top, total_width - 2)

      v_left  = colorize(v_l_raw, border_color_cfg)
      v_right = colorize(v_r_raw, border_color_cfg)

      top_border_line = box_border[:tl] + top_fill + box_border[:tr]
      rendered_lines << "#{margin_left}#{colorize(top_border_line, border_color_cfg)}"

      unless @title.empty?
        centered_title = colorize(@title.center(total_width - 4), title_color_cfg)
        rendered_lines << "#{margin_left}#{v_left} #{centered_title} #{v_right}"

        separator_line = v_l_raw + mid_fill + v_r_raw
        rendered_lines << "#{margin_left}#{colorize(separator_line, border_color_cfg)}"
      end

      option_names.each_with_index do |option_name, current_index|
        avail_w = [total_width - 6, 1].max
        if @index == current_index
          highlighted_text = colorize("> #{option_name.ljust(avail_w)}", focus_color_cfg)
          rendered_lines << "#{margin_left}#{v_left} #{highlighted_text} #{v_right}"
        else
          normal_text = colorize("  #{option_name.ljust(avail_w)}", options_color_cfg)
          rendered_lines << "#{margin_left}#{v_left} #{normal_text} #{v_right}"
        end
      end

      bottom_border_line = box_border[:bl] + bot_fill + box_border[:br]
      rendered_lines << "#{margin_left}#{colorize(bottom_border_line, border_color_cfg)}"
    else
      symbol_char  = STYLES[@style] || "#"
      solid_border = colorize(symbol_char, border_color_cfg)
      solid_line   = symbol_char * total_width

      rendered_lines << "#{margin_left}#{colorize(solid_line, border_color_cfg)}"

      unless @title.empty?
        centered_title = colorize(@title.center(total_width - 4), title_color_cfg)
        rendered_lines << "#{margin_left}#{solid_border} #{centered_title} #{solid_border}"
        rendered_lines << "#{margin_left}#{colorize(solid_line, border_color_cfg)}"
      end

      option_names.each_with_index do |option_name, current_index|
        avail_w = [total_width - 6, 1].max
        if @index == current_index
          highlighted_text = colorize("> #{option_name.ljust(avail_w)}", focus_color_cfg)
          rendered_lines << "#{margin_left}#{solid_border} #{highlighted_text} #{solid_border}"
        else
          normal_text = colorize("  #{option_name.ljust(avail_w)}", options_color_cfg)
          rendered_lines << "#{margin_left}#{solid_border} #{normal_text} #{solid_border}"
        end
      end

      rendered_lines << "#{margin_left}#{colorize(solid_line, border_color_cfg)}"
    end

    rendered_lines
  end

  def draw(size_max: 20, min_width: nil)
    target_width = min_width || size_max || 20
    action_to_execute = nil

    is_tty = $stdin.respond_to?(:tty?) && $stdin.tty?

    begin
      Kernel.print("#{HIDE_CURSOR}#{CLEAR_SCREEN_SEQUENCE}")

      if is_tty
        $stdin.raw do |raw_input_stream|
          action_to_execute = run_interactive_loop(raw_input_stream, target_width)
        end
      else
        action_to_execute = run_interactive_loop($stdin, target_width)
      end
    ensure
      Kernel.print(SHOW_CURSOR)
    end

    if action_to_execute
      Kernel.print(CLEAR_SCREEN_SEQUENCE)
      execute_action(action_to_execute)
    else
      Kernel.print(CLEAR_SCREEN_SEQUENCE)
    end
  rescue Interrupt
    Kernel.print("#{SHOW_CURSOR}#{CLEAR_SCREEN_SEQUENCE}")
    nil
  end

  private

  def draw_frame(target_width)
    lines = render_lines(target_width)
    buffer = String.new(CURSOR_HOME)
    lines.each do |line|
      buffer << line << CLEAR_TO_EOL << "\r\n"
    end
    buffer << CLEAR_TO_EOS
    Kernel.print(buffer)
  end

  def run_interactive_loop(input_stream, target_width)
    draw_frame(target_width)

    while (key = read_single_key(input_stream))
      break if key == "q" || key == "Q" || key == "\x03" || key == "\x04"

      if key == "\e[A" || key == "\eOA" || key == "\xe0H" || key == "\x00H"
        move_up
        draw_frame(target_width)
      elsif key == "\e[B" || key == "\eOB" || key == "\xe0P" || key == "\x00P"
        move_down
        draw_frame(target_width)
      elsif key == "\r" || key == "\n"
        return @functions[@index]
      end
    end

    nil
  end

  def read_single_key(input_stream)
    unless input_stream.respond_to?(:tty?) && input_stream.tty?
      begin
        return input_stream.sysread(3) if input_stream.respond_to?(:sysread)
        return input_stream.read(1)
      rescue EOFError, Errno::EPIPE
        return nil
      end
    end

    first_char = input_stream.getch
    return nil if first_char.nil?

    if first_char == "\e"
      begin
        extra_chars = input_stream.read_nonblock(2)
        first_char << extra_chars
      rescue IO::WaitReadable, IO::EAGAINWaitReadable, EOFError
      end
    elsif first_char == "\x00" || first_char == "\xe0"
      begin
        second_char = input_stream.read_nonblock(1)
        first_char << second_char
      rescue IO::WaitReadable, IO::EAGAINWaitReadable, EOFError
        second_char = input_stream.getch rescue nil
        first_char << second_char if second_char
      end
    end

    first_char
  rescue EOFError, Errno::EPIPE, Errno::ENOTTY
    nil
  end

  def format_auto_name(raw_name)
    cleaned = raw_name.to_s.gsub(/[_-]+/, ' ').strip
    cleaned.split(' ').map(&:capitalize).join(' ')
  end

  def extract_name_from_action(action)
    case action
    when Array
      action[0].to_s
    when Method
      format_auto_name(action.name)
    when Symbol
      format_auto_name(action)
    when Proc
      if action.respond_to?(:name) && action.name
        format_auto_name(action.name)
      else
        "Opcion"
      end
    else
      if action.respond_to?(:name)
        format_auto_name(action.name)
      elsif action.respond_to?(:title)
        action.title.to_s
      else
        format_auto_name(action)
      end
    end
  end

  def execute_action(action)
    case action
    when Method, Proc
      action.call
    when Symbol
      if Object.respond_to?(action, true)
        Object.send(action)
      elsif Kernel.respond_to?(action, true)
        Kernel.send(action)
      end
    when Array
      callable = action[1]
      callable.call if callable.respond_to?(:call)
    else
      action.call if action.respond_to?(:call)
    end
  end
end

Color = GRmenu::Color unless defined?(Color)
Colors = GRmenu::Color unless defined?(Colors)
C = GRmenu::Color unless defined?(C)
Grmenu = GRmenu unless defined?(Grmenu)
