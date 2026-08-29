# frozen_string_literal: true

require 'io/console'

class GRmenu
  CLEAR_SCREEN_SEQUENCE = "\e[H\e[2J\e[3J"
  HIDE_CURSOR = "\e[?25l"
  SHOW_CURSOR = "\e[?25h"
  CURSOR_HOME = "\e[H"
  CLEAR_TO_EOL = "\e[K"
  CLEAR_TO_EOS = "\e[J"

  STYLES = {
    1  => "#", 2  => "┌", 3  => "╔", 4  => "┏", 5  => "╒",
    6  => "╓", 7  => "╭", 8  => "▛", 9  => "▓", 10 => "▒",
    11 => "░", 12 => "█", 13 => "*", 14 => "+", 15 => "=",
    16 => "~", 17 => "-", 18 => "◆", 19 => "●", 20 => "★"
  }.freeze

  COLORS = {
    "black"   => { 1 => "\e[30m", 2 => "\e[90m" },
    "red"     => { 1 => "\e[31m", 2 => "\e[91m" },
    "green"   => { 1 => "\e[32m", 2 => "\e[92m" },
    "yellow"  => { 1 => "\e[33m", 2 => "\e[93m" },
    "blue"    => { 1 => "\e[34m", 2 => "\e[94m" },
    "magenta" => { 1 => "\e[35m", 2 => "\e[95m" },
    "cyan"    => { 1 => "\e[36m", 2 => "\e[96m" },
    "white"   => { 1 => "\e[37m", 2 => "\e[97m" },
    "reset"   => "\e[0m"
  }.freeze

  BORDERS = {
    1  => { h: "=-", v: "|", tl: "#", tr: "#", bl: "#", br: "#" },
    2  => { h: "─",  v: "│", tl: "┌", tr: "┐", bl: "└", br: "┘" },
    3  => { h: "═",  v: "║", tl: "╔", tr: "╗", bl: "╚", br: "╝" },
    4  => { h: "━",  v: "┃", tl: "┏", tr: "┓", bl: "┗", br: "┛" },
    5  => { h: "═",  v: "│", tl: "╒", tr: "╕", bl: "╘", br: "╛" },
    6  => { h: "─",  v: "║", tl: "╓", tr: "╖", bl: "╙", br: "╜" },
    7  => { h: "─",  v: "│", tl: "╭", tr: "╮", bl: "╰", br: "╯" },
    8  => { h: "▀",  v: "▌", tl: "▛", tr: "▜", bl: "▙", br: "▟" },
    19 => { h: "●○", v: "●", tl: "●", tr: "●", bl: "●", br: "●" },
    20 => { h: "★☆", v: "★", tl: "★", tr: "★", bl: "★", br: "★" }
  }.freeze

  class SetStyle
    def initialize(
      border:  { color: "cyan",  level: 1 },
      options: { color: "white", level: 1 },
      focus:   { color: "green", level: 2 }
    )
      @border  = border.dup
      @options = options.dup
      @focus   = focus.dup
    end

    def border(color_name = nil, brightness_level = 1)
      return @border if color_name.nil?
      if color_name.is_a?(Hash)
        @border = color_name
      else
        @border = { color: color_name.to_s, level: brightness_level.to_i }
      end
    end
    alias_method :Border, :border
    alias_method :set_border, :border
    alias_method :border=, :border

    def options(color_name = nil, brightness_level = 1)
      return @options if color_name.nil?
      if color_name.is_a?(Hash)
        @options = color_name
      else
        @options = { color: color_name.to_s, level: brightness_level.to_i }
      end
    end
    alias_method :Options, :options
    alias_method :set_options, :options
    alias_method :options=, :options

    def focus(color_name = nil, brightness_level = 2)
      return @focus if color_name.nil?
      if color_name.is_a?(Hash)
        @focus = color_name
      else
        @focus = { color: color_name.to_s, level: brightness_level.to_i }
      end
    end
    alias_method :Focus, :focus
    alias_method :set_focus, :focus
    alias_method :focus=, :focus

    class << self
      def border(color_name = nil, brightness_level = 1)
        @default_border ||= { color: "cyan", level: 1 }
        return @default_border if color_name.nil?
        if color_name.is_a?(Hash)
          @default_border = color_name
        else
          @default_border = { color: color_name.to_s, level: brightness_level.to_i }
        end
      end
      alias_method :Border, :border
      alias_method :border=, :border

      def options(color_name = nil, brightness_level = 1)
        @default_options ||= { color: "white", level: 1 }
        return @default_options if color_name.nil?
        if color_name.is_a?(Hash)
          @default_options = color_name
        else
          @default_options = { color: color_name.to_s, level: brightness_level.to_i }
        end
      end
      alias_method :Options, :options
      alias_method :options=, :options

      def focus(color_name = nil, brightness_level = 2)
        @default_focus ||= { color: "green", level: 2 }
        return @default_focus if color_name.nil?
        if color_name.is_a?(Hash)
          @default_focus = color_name
        else
          @default_focus = { color: color_name.to_s, level: brightness_level.to_i }
        end
      end
      alias_method :Focus, :focus
      alias_method :focus=, :focus
    end
  end

  module GRprint
    module_function

    def p(text = "", ending = "\r\n")
      Kernel.print("#{text}#{ending}")
    end
  end

  attr_accessor :functions, :title, :style, :index, :style_config

  alias_method :options, :functions
  alias_method :options=, :functions=
  alias_method :selected_index, :index
  alias_method :selected_index=, :index=
  alias_method :SetStyle, :style_config
  alias_method :set_style, :style_config

  def self.STYLES
    STYLES
  end

  def self.COLORS
    COLORS
  end

  def self.BORDERS
    BORDERS
  end

  def initialize(functions, *positional_arguments, title: nil, style: nil, **keyword_arguments)
    @functions = functions.is_a?(Array) ? functions : Array(functions)

    pos_title = positional_arguments[0]
    pos_style = positional_arguments[1]

    @title = (title || pos_title || keyword_arguments[:title] || "").to_s
    @style = (style || pos_style || keyword_arguments[:style] || 19).to_i
    @index = 0
    @clear_seq = CLEAR_SCREEN_SEQUENCE

    @style_config = SetStyle.new(
      border:  SetStyle.border.dup,
      options: SetStyle.options.dup,
      focus:   SetStyle.focus.dup
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

  def menu
    Kernel.print("Press any key to start ...\r\n")
  end

  def render_lines(size_max = 20)
    option_names = @functions.map { |func| extract_name_from_action(func) }

    total_width =  [([size_max] + option_names.map { |name| name.length + 4 }).max, @title.length + 4].max unless @title.empty?

    border_color_cfg  = @style_config.border
    options_color_cfg = @style_config.options
    focus_color_cfg   = @style_config.focus

    box_border = BORDERS[@style]
    rendered_lines = []

    if box_border
      horizontal_fill = build_horizontal_line(box_border[:h], total_width - 2)
      vertical_char   = colorize(box_border[:v], border_color_cfg)

      top_border_line = box_border[:tl] + horizontal_fill + box_border[:tr]
      rendered_lines << colorize(top_border_line, border_color_cfg)

      unless @title.empty?
        centered_title = @title.center(total_width - 4)
        rendered_lines << "#{vertical_char} #{centered_title} #{vertical_char}"

        separator_line = box_border[:v] + horizontal_fill + box_border[:v]
        rendered_lines << colorize(separator_line, border_color_cfg)
      end

      option_names.each_with_index do |option_name, current_index|
        if @index == current_index
          highlighted_text = colorize(">#{option_name.ljust(total_width - 6)}", focus_color_cfg)
          rendered_lines << "#{vertical_char}  #{highlighted_text} #{vertical_char}"
        else
          normal_text = colorize("> #{option_name.ljust(total_width - 6)}", options_color_cfg)
          rendered_lines << "#{vertical_char} #{normal_text} #{vertical_char}"
        end
      end

      bottom_border_line = box_border[:bl] + horizontal_fill + box_border[:br]
      rendered_lines << colorize(bottom_border_line, border_color_cfg)
    else
      symbol_char  = STYLES[@style] || "#"
      solid_border = colorize(symbol_char, border_color_cfg)
      solid_line   = symbol_char * total_width

      rendered_lines << colorize(solid_line, border_color_cfg)

      unless @title.empty?
        centered_title = @title.center(total_width - 4)
        rendered_lines << "#{solid_border} #{centered_title} #{solid_border}"
        rendered_lines << colorize(solid_line, border_color_cfg)
      end

      option_names.each_with_index do |option_name, current_index|
        if @index == current_index
          highlighted_text = colorize(option_name.ljust(total_width - 4), focus_color_cfg)
          rendered_lines << "#{solid_border} #{highlighted_text} #{solid_border}"
        else
          normal_text = colorize(option_name.ljust(total_width - 4), options_color_cfg)
          rendered_lines << "#{solid_border} #{normal_text} #{solid_border}"
        end
      end

      rendered_lines << colorize(solid_line, border_color_cfg)
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

      if key == "\e[A" || key == "\eOA"
        move_up
        draw_frame(target_width)
      elsif key == "\e[B" || key == "\eOB"
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
    end

    first_char
  rescue EOFError, Errno::EPIPE, Errno::ENOTTY
    nil
  end

  def extract_name_from_action(action)
    case action
    when Method
      action.name.to_s
    when Symbol
      action.to_s
    when Array
      action[0].to_s
    when Proc
      if action.respond_to?(:name) && action.name
        action.name.to_s
      else
        "opcion"
      end
    else
      if action.respond_to?(:name)
        action.name.to_s
      elsif action.respond_to?(:title)
        action.title.to_s
      else
        action.to_s
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

Grmenu = GRmenu unless defined?(Grmenu)
