# frozen_string_literal: true

require 'io/console'
require 'json'
require 'zlib'
require 'open3'

class GRmenu
  CLEAR_SCREEN_SEQUENCE = "\e[H\e[2J\e[3J"
  HIDE_CURSOR           = "\e[?25l"
  SHOW_CURSOR           = "\e[?25h"
  CURSOR_HOME           = "\e[H"
  CLEAR_TO_EOL          = "\e[K"
  CLEAR_TO_EOS          = "\e[J"

  def self.find_data_file(filename)
    local_path = File.expand_path("data/#{filename}", __dir__)
    return local_path if File.exist?(local_path)
    parent_path = File.expand_path("../data/#{filename}", __dir__)
    return parent_path if File.exist?(parent_path)
    nil
  end

  def self.load_json_data(filename)
    path = find_data_file(filename)
    return {} unless path && File.exist?(path)
    JSON.parse(File.read(path))
  rescue StandardError
    {}
  end

  COLORS  = load_json_data('colors.json').freeze
  BORDERS = load_json_data('borders.json').transform_keys(&:to_i).transform_values { |v| v.is_a?(Hash) ? v.transform_keys(&:to_sym) : { h: v.to_s, v: v.to_s, tl: v.to_s, tr: v.to_s, bl: v.to_s, br: v.to_s } }.freeze
  FONTS   = load_json_data('fonts.json').transform_keys(&:to_i).freeze

  BASE_RGB = COLORS.each_with_object({}) do |(name, val), h|
    next if name == "reset"
    code = val.is_a?(Hash) ? (val["2"] || val[2] || val["1"] || val[1]) : val.to_s
    if code =~ /38;2;(\d+);(\d+);(\d+)/
      h[name] = [$1.to_i, $2.to_i, $3.to_i]
    elsif code == "90m" || code == "30m"
      h[name] = [100, 100, 100]
    elsif code == "91m" || code == "31m"
      h[name] = [255, 60, 60]
    elsif code == "92m" || code == "32m"
      h[name] = [60, 255, 60]
    elsif code == "93m" || code == "33m"
      h[name] = [255, 255, 60]
    elsif code == "94m" || code == "34m"
      h[name] = [60, 120, 255]
    elsif code == "95m" || code == "35m"
      h[name] = [255, 60, 255]
    elsif code == "96m" || code == "36m"
      h[name] = [60, 255, 255]
    elsif code == "97m" || code == "37m"
      h[name] = [250, 250, 250]
    elsif code =~ /38;5;(\d+)/
      h[name] = [150, 150, 150]
    else
      h[name] = [220, 220, 220]
    end
  end.freeze

  FONT_1  = FONTS[1] || {}
  FONT_2  = FONTS[2] || {}
  FONT_3  = FONTS[3] || {}
  FONT_4  = FONTS[4] || {}
  FONT_5  = FONTS[5] || {}
  FONT_6  = FONTS[6] || {}
  FONT_7  = FONTS[7] || {}
  FONT_8  = FONTS[8] || {}
  FONT_9  = FONTS[9] || {}
  FONT_10 = FONTS[10] || {}

  def self.rgb_color(tick, offset = 0.0)
    t = tick.to_f + offset.to_f
    r = (Math.sin(t) * 127 + 128).clamp(0, 255).to_i
    g = (Math.sin(t + 2.0943951) * 127 + 128).clamp(0, 255).to_i
    b = (Math.sin(t + 4.1887902) * 127 + 128).clamp(0, 255).to_i
    "\e[38;2;#{r};#{g};#{b}m"
  end

  def self.ansi_color(color_name, level = 1)
    name = color_name.to_s.downcase.strip
    if name.include?(":")
      parts = name.split(":")
      name = parts[0].strip
      level = parts[1].to_i if parts[1] && !parts[1].empty?
    end
    return rgb_color(0.0) if name == "rgb" || name == "rainbow" || name == "chroma"
    if name =~ /\A#?([0-9a-f]{6})\z/i
      hex = $1
      r = hex[0..1].to_i(16)
      g = hex[2..3].to_i(16)
      b = hex[4..5].to_i(16)
      return "\e[38;2;#{r};#{g};#{b}m"
    elsif name =~ /\A#?([0-9a-f]{3})\z/i
      hex = $1
      r = (hex[0] * 2).to_i(16)
      g = (hex[1] * 2).to_i(16)
      b = (hex[2] * 2).to_i(16)
      return "\e[38;2;#{r};#{g};#{b}m"
    end
    lvl_str = level.to_s
    code_raw = COLORS.dig(name, lvl_str) || COLORS.dig(name, level.to_i) || COLORS[name]
    return "\e[#{code_raw}" if code_raw
    "\e[37m"
  end

  def self.ansi_reset
    "\e[0m"
  end

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
      white:          { 1 => "\e[37m", 2 => "\e[97m" },
      neon_red:       { 1 => "\e[38;2;230;10;50m", 2 => "\e[38;2;255;7;58;1m" },
      neon_green:     { 1 => "\e[38;2;40;220;20m", 2 => "\e[38;2;57;255;20;1m" },
      neon_cyan:      { 1 => "\e[38;2;0;210;255m", 2 => "\e[38;2;0;245;255;1m" },
      neon_blue:      { 1 => "\e[38;2;0;150;255m", 2 => "\e[38;2;0;191;255;1m" },
      neon_pink:      { 1 => "\e[38;2;230;10;210m", 2 => "\e[38;2;255;16;240;1m" },
      neon_yellow:    { 1 => "\e[38;2;230;200;0m", 2 => "\e[38;2;255;235;0;1m" },
      neon_orange:    { 1 => "\e[38;2;240;80;0m", 2 => "\e[38;2;255;105;0;1m" },
      neon_purple:    { 1 => "\e[38;2;160;0;220m", 2 => "\e[38;2;191;0;255;1m" },
      neon_magenta:   { 1 => "\e[38;2;220;0;220m",   2 => "\e[38;2;255;0;255;1m" },
      neon_aqua:      { 1 => "\e[38;2;0;220;210m",   2 => "\e[38;2;0;255;230;1m" },
      neon_lime:      { 1 => "\e[38;2;120;240;0m",   2 => "\e[38;2;170;255;0;1m" },
      neon_white:     { 1 => "\e[38;2;220;230;255m", 2 => "\e[38;2;255;255;255;1m" },
      neon:           { 1 => "\e[38;2;230;10;50m", 2 => "\e[38;2;255;7;58;1m" }
    }.freeze

    module_function

    def paint(text, color_name, level = 1)
      c_str = color_name.to_s.downcase
      if c_str == "rgb" || c_str == "rainbow" || c_str == "chroma"
        return rgb(text)
      end
      code = CODES.dig(color_name.to_sym, level) || GRmenu.ansi_color(color_name, level) || "\e[37m"
      "#{code}#{text}#{RESET}"
    end

    def rgb(text, offset = 0.0)
      out = String.new("")
      idx = 0
      in_escape = false
      escape_buf = String.new("")

      text.to_s.each_char do |ch|
        if ch == "\e"
          in_escape = true
          escape_buf << ch
          next
        end
        if in_escape
          escape_buf << ch
          if ch =~ /[a-zA-Z]/
            in_escape = false
            out << escape_buf
            escape_buf.clear
          end
          next
        end

        if ch == " " || ch == "\n" || ch == "\r" || ch == "\t"
          out << ch
        else
          t = idx * 0.12 + offset
          r = (Math.sin(t) * 127 + 128).clamp(0, 255).to_i
          g = (Math.sin(t + 2.0943951) * 127 + 128).clamp(0, 255).to_i
          b = (Math.sin(t + 4.1887902) * 127 + 128).clamp(0, 255).to_i
          out << "\e[38;2;#{r};#{g};#{b}m#{ch}"
          idx += 1
        end
      end
      out << RESET
      out
    end

    def red(s);            paint(s, :red, 1);     end
    def bright_red(s);     paint(s, :red, 2);     end
    def dark_red(s);       paint(s, :red, 1);     end

    def green(s);          paint(s, :green, 1);   end
    def bright_green(s);   paint(s, :green, 2);   end
    def dark_green(s);     paint(s, :green, 1);   end

    def yellow(s);         paint(s, :yellow, 1);  end
    def bright_yellow(s);  paint(s, :yellow, 2);  end

    def blue(s);           paint(s, :blue, 1);    end
    def bright_blue(s);    paint(s, :blue, 2);    end

    def magenta(s);        paint(s, :magenta, 1); end
    def bright_magenta(s); paint(s, :magenta, 2); end

    def purple(s);         paint(s, :purple, 1);  end
    def bright_purple(s);  paint(s, :purple, 2);  end

    def pink(s);           paint(s, :pink, 1);    end
    def bright_pink(s);    paint(s, :pink, 2);    end

    def cyan(s);           paint(s, :cyan, 1);    end
    def bright_cyan(s);    paint(s, :cyan, 2);    end

    def aqua(s);           paint(s, :aqua, 1);    end
    def bright_aqua(s);    paint(s, :aqua, 2);    end

    def orange(s);         paint(s, :orange, 1);  end
    def bright_orange(s);  paint(s, :orange, 2);  end

    def white(s);          paint(s, :white, 1);   end
    def bright_white(s);   paint(s, :white, 2);   end

    def black(s);          paint(s, :black, 1);   end
    def gray(s);           paint(s, :gray, 1);    end
    def bright_gray(s);    paint(s, :gray, 2);    end
    def grey(s);           gray(s);               end

    def neon_red(s);       paint(s, :neon_red, 2);    end
    def neon_green(s);     paint(s, :neon_green, 2);  end
    def neon_cyan(s);      paint(s, :neon_cyan, 2);   end
    def neon_blue(s);      paint(s, :neon_blue, 2);   end
    def neon_pink(s);      paint(s, :neon_pink, 2);   end
    def neon_yellow(s);    paint(s, :neon_yellow, 2); end
    def neon_orange(s);    paint(s, :neon_orange, 2); end
    def neon_purple(s);    paint(s, :neon_purple, 2); end
    def neon_magenta(s);   paint(s, :neon_magenta, 2); end
    def neon_aqua(s);      paint(s, :neon_aqua, 2);    end
    def neon_lime(s);      paint(s, :neon_lime, 2);    end
    def neon_white(s);     paint(s, :neon_white, 2);   end

    def r(s);  bright_red(s);     end
    def dr(s); dark_red(s);       end
    def g(s);  bright_green(s);   end
    def y(s);  bright_yellow(s);  end
    def w(s);  bright_white(s);   end
    def gr(s); gray(s);           end
    def cy(s); bright_cyan(s);    end
    def mg(s); bright_magenta(s); end
    def bl(s); bright_blue(s);    end

    def hex(code, text)
      c = GRmenu.ansi_color(code.to_s)
      "#{c}#{text}#{RESET}"
    end

    def respond_to_missing?(method_name, include_private = false)
      GRmenu::COLORS.key?(method_name.to_s) || super
    end

    def method_missing(method_name, *args, &block)
      m_str = method_name.to_s
      if GRmenu::COLORS.key?(m_str)
        text = args[0].to_s
        lvl = args[1] || 2
        paint(text, m_str, lvl)
      else
        super
      end
    end
  end
  C = Color

  STYLES = {
    1  => "#", 2  => "┌", 3  => "╔", 4  => "┏", 5  => "╒",
    6  => "╓", 7  => "╭", 8  => "▛", 9  => "▓", 10 => "▒",
    11 => "░", 12 => "█", 13 => "*", 14 => "+", 15 => "=",
    16 => "~", 17 => "-", 18 => "◆", 19 => "●", 20 => "★"
  }.freeze

  class PNGDecoder
    attr_reader :width, :height, :pixels

    def self.load(filepath)
      return nil unless filepath && File.exist?(filepath)
      new.parse(File.binread(filepath))
    rescue StandardError
      nil
    end

    def parse(data)
      return nil unless data && data[0, 8] == "\x89PNG\r\n\x1a\n".b

      offset = 8
      idat_data = String.new("".b)
      palette = nil

      while offset < data.bytesize
        len = data[offset, 4].unpack1("N")
        type = data[offset + 4, 4]
        chunk_data = data[offset + 8, len]
        offset += 12 + len

        case type
        when "IHDR"
          @width, @height, @bit_depth, @color_type = chunk_data.unpack("NNCC")
        when "PLTE"
          palette = chunk_data.bytes.each_slice(3).to_a
        when "IDAT"
          idat_data << chunk_data
        when "IEND"
          break
        end
      end

      channels = case @color_type
                 when 0 then 1
                 when 2 then 3
                 when 3 then 1
                 when 4 then 2
                 when 6 then 4
                 else return nil
                 end

      bpp = [(@bit_depth * channels + 7) / 8, 1].max
      stride = (@width * channels * @bit_depth + 7) / 8
      scanline_len = stride + 1

      raw = Zlib::Inflate.inflate(idat_data)
      raw_bytes = raw.bytes
      return nil if raw_bytes.length < (@height * scanline_len)

      @pixels = Array.new(@height) { Array.new(@width) }
      prev_row = Array.new(stride, 0)

      @height.times do |y|
        row_start = y * scanline_len
        filter_type = raw_bytes[row_start]
        curr_filtered = raw_bytes[(row_start + 1)...(row_start + scanline_len)]
        curr_recon = Array.new(stride, 0)

        stride.times do |i|
          a = (i >= bpp) ? curr_recon[i - bpp] : 0
          b = prev_row[i]
          c = (i >= bpp) ? prev_row[i - bpp] : 0
          x = curr_filtered[i]

          recon_val = case filter_type
                      when 0 then x
                      when 1 then (x + a) & 0xFF
                      when 2 then (x + b) & 0xFF
                      when 3 then (x + ((a + b) / 2)) & 0xFF
                      when 4
                        p_val = a + b - c
                        pa = (p_val - a).abs
                        pb = (p_val - b).abs
                        pc = (p_val - c).abs
                        pr = if pa <= pb && pa <= pc
                               a
                             elsif pb <= pc
                               b
                             else
                               c
                             end
                        (x + pr) & 0xFF
                      else x
                      end
          curr_recon[i] = recon_val
        end

        prev_row = curr_recon

        if @bit_depth == 16
          @width.times do |x|
            idx = x * channels * 2
            r = curr_recon[idx]
            g = (channels >= 3) ? curr_recon[idx + 2] : r
            b = (channels >= 3) ? curr_recon[idx + 4] : r
            a = (channels == 4) ? curr_recon[idx + 6] : (channels == 2 ? curr_recon[idx + 2] : 255)
            @pixels[y][x] = [r, g, b, a]
          end
        elsif @bit_depth == 8
          @width.times do |x|
            idx = x * channels
            if @color_type == 3
              p_idx = curr_recon[idx]
              rgb_val = palette ? (palette[p_idx] || [0, 0, 0]) : [0, 0, 0]
              @pixels[y][x] = [rgb_val[0], rgb_val[1], rgb_val[2], 255]
            else
              r = curr_recon[idx]
              g = (channels >= 3) ? curr_recon[idx + 1] : r
              b = (channels >= 3) ? curr_recon[idx + 2] : r
              a = (channels == 4 || channels == 2) ? curr_recon[idx + channels - 1] : 255
              @pixels[y][x] = [r, g, b, a]
            end
          end
        end
      end
      self
    end

    def resample(target_w, target_h)
      resampled = Array.new(target_h) { Array.new(target_w) }
      x_step = @width.to_f / target_w
      y_step = @height.to_f / target_h

      target_h.times do |ty|
        sy_start = (ty * y_step).to_i
        sy_end   = [((ty + 1) * y_step).to_i, @height].min

        target_w.times do |tx|
          sx_start = (tx * x_step).to_i
          sx_end   = [((tx + 1) * x_step).to_i, @width].min

          r_sum = g_sum = b_sum = a_sum = count = 0

          (sy_start...sy_end).each do |sy|
            (sx_start...sx_end).each do |sx|
              p = @pixels[sy][sx]
              next unless p
              if p[3] > 10
                r_sum += p[0]
                g_sum += p[1]
                b_sum += p[2]
                a_sum += p[3]
                count += 1
              end
            end
          end

          if count > 0
            resampled[ty][tx] = [(r_sum / count).clamp(0, 255), (g_sum / count).clamp(0, 255), (b_sum / count).clamp(0, 255), (a_sum / count).clamp(0, 255)]
          else
            mid_y = (sy_start + sy_end) / 2
            mid_x = (sx_start + sx_end) / 2
            resampled[ty][tx] = @pixels[mid_y][mid_x] || [0, 0, 0, 0]
          end
        end
      end
      resampled
    end

    def render_ansi_lines(target_w = 40, target_h = nil)
      target_h ||= [((@height.to_f / @width) * target_w).round, 2].max
      target_h += 1 if target_h.odd?

      grid = resample(target_w, target_h)
      lines = []

      (0...target_h).step(2) do |y|
        row_top = grid[y]
        row_bot = grid[y + 1] || grid[y]
        line = String.new("")

        target_w.times do |x|
          r1, g1, b1, a1 = row_top[x]
          r2, g2, b2, a2 = row_bot[x]

          if a1 < 32 && a2 < 32
            line << "\e[0m "
          elsif a1 < 32
            line << "\e[0m\e[38;2;#{r2};#{g2};#{b2}m▄"
          elsif a2 < 32
            line << "\e[0m\e[38;2;#{r1};#{g1};#{b1}m▀"
          else
            line << "\e[38;2;#{r1};#{g1};#{b1}m\e[48;2;#{r2};#{g2};#{b2}m▀"
          end
        end
        line << "\e[0m"
        lines << line
      end

      lines
    end
  end

  def self.char_width(char)
    code = char.ord
    return 0 if code == 0 || code == 0xFE0F || code == 0xFE0E || (code >= 0x0300 && code <= 0x036F) || (code >= 0x200B && code <= 0x200F)
    return 0 if code < 32 || (code >= 0x7F && code < 0xA0)
    return 1 if code == 0x1F5BC || code == 0x1F5B4 || code == 0x1F5B5 || code == 0x1F5C2
    if (code >= 0x1100 && code <= 0x115F) ||
       (code >= 0x2329 && code <= 0x232A) ||
       (code >= 0x2E80 && code <= 0xA4CF && code != 0x303F) ||
       (code >= 0xAC00 && code <= 0xD7A3) ||
       (code >= 0xF900 && code <= 0xFAFF) ||
       (code >= 0xFE10 && code <= 0xFE19) ||
       (code >= 0xFE30 && code <= 0xFE6F) ||
       (code >= 0xFF01 && code <= 0xFF60) ||
       (code >= 0xFFE0 && code <= 0xFFE6) ||
       (code >= 0x1F300 && code <= 0x1F6FF) ||
       (code >= 0x1F900 && code <= 0x1FAFF)
      2
    else
      1
    end
  end

  def self.display_width(str)
    clean = str.to_s.gsub(/\e\[[0-9;]*[a-zA-Z]/, '')
    clean.chars.map { |c| char_width(c) }.sum
  end

  def self.pad_to_width(str, target_width, align = :left)
    current_w = display_width(str)
    pad_needed = [target_width - current_w, 0].max
    case align
    when :right
      (" " * pad_needed) + str.to_s
    when :center
      left_pad = " " * (pad_needed / 2)
      right_pad = " " * (pad_needed - (pad_needed / 2))
      left_pad + str.to_s + right_pad
    else
      str.to_s + (" " * pad_needed)
    end
  end

  def self.load_and_render_image(filepath, width = 40, height = nil, max_cols = terminal_width)
    return [] unless filepath && File.exist?(filepath)

    req_w = [width.to_i, max_cols - 6].min
    req_w = [req_w, 10].max

    conv_bin = `which convert 2>/dev/null`.strip
    conv_bin = `which magick 2>/dev/null`.strip if conv_bin.empty?

    if !conv_bin.empty?
      info, _ = Open3.capture2("identify", "-format", "%w %h", filepath) rescue ["", nil]
      orig_w, orig_h = info.strip.split.map(&:to_f)
      aspect = (orig_w && orig_w > 0) ? (orig_h / orig_w) : 0.6
      scale_h = height || (req_w * aspect).round
      scale_h += 1 if scale_h.odd?
      scale_h = [scale_h, 2].max

      cmd = [conv_bin, filepath, "-filter", "Lanczos", "-resize", "#{req_w}x#{scale_h}!", "-depth", "8", "rgba:-"]
      stdout, status = Open3.capture2(*cmd) rescue [nil, nil]
      if status && status.success? && stdout.bytesize == (req_w * scale_h * 4)
        raw = stdout.bytes
        lines = []
        (0...scale_h).step(2) do |y|
          line = String.new("")
          req_w.times do |x|
            top_idx = (y * req_w + x) * 4
            bot_idx = ((y + 1) * req_w + x) * 4
            r1, g1, b1, a1 = raw[top_idx, 4]
            r2, g2, b2, a2 = raw[bot_idx, 4]

            if a1 < 32 && a2 < 32
              line << "\e[0m "
            elsif a1 < 32
              line << "\e[0m\e[38;2;#{r2};#{g2};#{b2}m▄"
            elsif a2 < 32
              line << "\e[0m\e[38;2;#{r1};#{g1};#{b1}m▀"
            else
              line << "\e[38;2;#{r1};#{g1};#{b1}m\e[48;2;#{r2};#{g2};#{b2}m▀"
            end
          end
          line << "\e[0m"
          lines << line
        end
        return lines
      end
    end

    png = PNGDecoder.load(filepath)
    if png
      return png.render_ansi_lines(req_w, height)
    end

    []
  rescue StandardError
    []
  end

  def self.image(filepath, width: 40, height: nil, style: 3, color: "cyan", center: true)
    term_w = terminal_width
    raw_lines = load_and_render_image(filepath, width, height, term_w)
    return nil if raw_lines.empty?

    img_w = display_width(raw_lines.first)
    box_w = img_w + 4
    margin = (center && term_w > box_w) ? (" " * ((term_w - box_w) / 2)) : ""

    if style && style > 0
      border_cfg = BORDERS[style] || BORDERS[3]
      is_rgb = (color.to_s.downcase == "rgb" || color.to_s.downcase == "rainbow" || color.to_s.downcase == "chroma")
      color_code = is_rgb ? "" : ansi_color(color, 2)
      reset_code = ansi_reset

      h_top = border_cfg[:ht] || border_cfg[:h]
      h_bot = border_cfg[:hb] || border_cfg[:h]
      v_l = border_cfg[:vl] || border_cfg[:v]
      v_r = border_cfg[:vr] || border_cfg[:v]

      top_fill = (h_top * ((box_w - 2).to_f / h_top.length).ceil)[0...(box_w - 2)]
      bot_fill = (h_bot * ((box_w - 2).to_f / h_bot.length).ceil)[0...(box_w - 2)]

      if is_rgb
        Kernel.print("#{margin}#{Color.rgb("#{border_cfg[:tl]}#{top_fill}#{border_cfg[:tr]}")}\r\n")
        raw_lines.each do |line|
          Kernel.print("#{margin}#{Color.rgb(v_l)} #{line} #{Color.rgb(v_r)}\r\n")
        end
        Kernel.print("#{margin}#{Color.rgb("#{border_cfg[:bl]}#{bot_fill}#{border_cfg[:br]}")}\r\n")
      else
        Kernel.print("#{margin}#{color_code}#{border_cfg[:tl]}#{top_fill}#{border_cfg[:tr]}#{reset_code}\r\n")
        raw_lines.each do |line|
          Kernel.print("#{margin}#{color_code}#{v_l}#{reset_code} #{line} #{color_code}#{v_r}#{reset_code}\r\n")
        end
        Kernel.print("#{margin}#{color_code}#{border_cfg[:bl]}#{bot_fill}#{border_cfg[:br]}#{reset_code}\r\n")
      end
    else
      raw_lines.each do |line|
        Kernel.print("#{margin}#{line}\r\n")
      end
    end

    true
  end

  class ProgressBar
    attr_reader :total, :current, :title, :status

    def initialize(total = 100, title: nil, color: "cyan", level: 2, style: 3, width: nil)
      @total   = [total.to_i, 1].max
      @current = 0
      @title   = title
      @status  = String.new("")
      @color   = color.to_s.downcase
      @level   = level.to_i
      @style   = style.to_i
      @width   = width
      @closed  = false
      @drawn_lines_count = 0
    end

    def advance(step = 1, status: nil)
      return if @closed
      @current = [(@current + step), @total].min
      @status = status.to_s if status
      render
    end
    alias_method :increment, :advance
    alias_method :step, :advance

    def set(value, status: nil)
      return if @closed
      @current = [[value.to_i, 0].max, @total].min
      @status = status.to_s if status
      render
    end

    def render
      term_w = GRmenu.terminal_width
      box_w = @width || [term_w - 4, 60].min
      box_w = [box_w, 36].max

      is_rgb = (@color == "rgb" || @color == "rainbow" || @color == "chroma")
      tick = (@current.to_f / @total) * 6.2831853

      border_cfg = GRmenu::BORDERS[@style] || GRmenu::BORDERS[3]

      v_l = border_cfg[:vl] || border_cfg[:v]
      v_r = border_cfg[:vr] || border_cfg[:v]
      h_t = border_cfg[:ht] || border_cfg[:h]
      h_b = border_cfg[:hb] || border_cfg[:h]

      top_fill = (h_t * ((box_w - 2).to_f / h_t.length).ceil)[0...(box_w - 2)]
      bot_fill = (h_b * ((box_w - 2).to_f / h_b.length).ceil)[0...(box_w - 2)]

      pct = ((@current.to_f / @total) * 100).round
      pct_str = "#{pct}% (#{@current}/#{@total})"

      inner_w = box_w - 4
      bar_w = [inner_w - pct_str.length - 3, 10].max
      filled_len = ((@current.to_f / @total) * bar_w).round
      empty_len  = bar_w - filled_len

      lines = []
      if is_rgb
        lines << Color.rgb("#{border_cfg[:tl]}#{top_fill}#{border_cfg[:tr]}", tick)
        if @title && !@title.empty?
          t_str = @title.to_s
          if GRmenu.display_width(t_str) > inner_w
            t_str = t_str[0...[inner_w - 3, 1].max] + "..."
          end
          pad_t = [inner_w - GRmenu.display_width(t_str), 0].max
          l_p = " " * (pad_t / 2)
          r_p = " " * (pad_t - (pad_t / 2))
          lines << "#{Color.rgb(v_l, tick)} #{l_p}#{Color.rgb(t_str, tick + 0.4)}#{r_p} #{Color.rgb(v_r, tick)}"
          lines << Color.rgb("#{v_l}#{top_fill}#{v_r}", tick)
        end

        filled_part = Color.rgb("█" * filled_len, tick)
        empty_part  = Color.gray("░" * empty_len)
        bar_raw_len = 2 + filled_len + empty_len + 1 + pct_str.length
        pad_bar_len = [inner_w - bar_raw_len, 0].max
        bar_line = "[#{filled_part}#{empty_part}] #{Color.bright_white(pct_str)}" + (" " * pad_bar_len)

        lines << "#{Color.rgb(v_l, tick)} #{bar_line} #{Color.rgb(v_r, tick)}"
        if @status && !@status.empty?
          st_str = @status.to_s
          if GRmenu.display_width(st_str) > inner_w
            st_str = st_str[0...[inner_w - 3, 1].max] + "..."
          end
          pad_st = [inner_w - GRmenu.display_width(st_str), 0].max
          st_line = st_str + (" " * pad_st)
          lines << "#{Color.rgb(v_l, tick)} #{Color.gray(st_line)} #{Color.rgb(v_r, tick)}"
        end
        lines << Color.rgb("#{border_cfg[:bl]}#{bot_fill}#{border_cfg[:br]}", tick)
      else
        color_code = GRmenu.ansi_color(@color, @level)
        reset_code = GRmenu.ansi_reset

        bar_str = "[#{"█" * filled_len}#{"░" * empty_len}] #{pct_str}"
        pad_bar_len = [inner_w - GRmenu.display_width(bar_str), 0].max
        bar_line = bar_str + (" " * pad_bar_len)

        lines << "#{color_code}#{border_cfg[:tl]}#{top_fill}#{border_cfg[:tr]}#{reset_code}"
        if @title && !@title.empty?
          t_str = @title.to_s
          if GRmenu.display_width(t_str) > inner_w
            t_str = t_str[0...[inner_w - 3, 1].max] + "..."
          end
          pad_t = [inner_w - GRmenu.display_width(t_str), 0].max
          l_p = " " * (pad_t / 2)
          r_p = " " * (pad_t - (pad_t / 2))
          lines << "#{color_code}#{v_l}#{reset_code} #{l_p}#{t_str}#{r_p} #{color_code}#{v_r}#{reset_code}"
          lines << "#{color_code}#{v_l}#{top_fill}#{v_r}#{reset_code}"
        end
        lines << "#{color_code}#{v_l}#{reset_code} #{color_code}#{bar_line}#{reset_code} #{color_code}#{v_r}#{reset_code}"
        if @status && !@status.empty?
          st_str = @status.to_s
          if GRmenu.display_width(st_str) > inner_w
            st_str = st_str[0...[inner_w - 3, 1].max] + "..."
          end
          pad_st = [inner_w - GRmenu.display_width(st_str), 0].max
          st_line = st_str + (" " * pad_st)
          lines << "#{color_code}#{v_l}#{reset_code} #{Color.gray(st_line)} #{color_code}#{v_r}#{reset_code}"
        end
        lines << "#{color_code}#{border_cfg[:bl]}#{bot_fill}#{border_cfg[:br]}#{reset_code}"
      end

      frame = lines.join("\r\n") + "\r\n"

      if @drawn_lines_count && @drawn_lines_count > 0
        Kernel.print("\e[#{@drawn_lines_count}A\e[J")
      end
      Kernel.print(frame)
      $stdout.flush
      @drawn_lines_count = lines.length
    end

    def finish(status: "¡Completado!")
      return if @closed
      set(@total, status: status)
      @closed = true
      Kernel.print(GRmenu::SHOW_CURSOR)
    end
  end

  def self.spinner(message = "Cargando...", color: "cyan", level: 2, delay: 0.08, &block)
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    is_rgb = (color.to_s.downcase == "rgb" || color.to_s.downcase == "rainbow" || color.to_s.downcase == "chroma")
    color_code = is_rgb ? "" : ansi_color(color, level)
    reset_code = ansi_reset

    stop_spinner = false
    spinner_thread = Thread.new do
      frame_idx = 0
      while !stop_spinner
        f = frames[frame_idx % frames.length]
        f_color = is_rgb ? rgb_color(frame_idx * 0.3) : color_code
        msg_out = is_rgb ? Color.rgb(message, frame_idx * 0.1) : message
        Kernel.print("\r\e[K#{f_color}#{f}#{reset_code} #{msg_out}")
        $stdout.flush
        frame_idx += 1
        sleep(delay)
      end
    end

    begin
      Kernel.print(HIDE_CURSOR)
      result = block ? block.call : nil
      stop_spinner = true
      spinner_thread.join
      success_color = ansi_color("green", 2)
      Kernel.print("\r\e[K#{success_color}[OK]#{reset_code} #{message} #{Color.gray("Listo!")}\r\n")
      result
    rescue Exception => e
      stop_spinner = true
      spinner_thread.join rescue nil
      error_color = ansi_color("red", 2)
      Kernel.print("\r\e[K#{error_color}[ERROR]#{reset_code} #{message} #{Color.bright_red("(Error: #{e.message})")}\r\n")
      raise e
    ensure
      stop_spinner = true
      Kernel.print(SHOW_CURSOR)
    end
  end

  def self.progress(total = 100, title: nil, color: "cyan", level: 2, style: 3, width: nil, &block)
    bar = ProgressBar.new(total, title: title, color: color, level: level, style: style, width: width)
    Kernel.print(HIDE_CURSOR)
    bar.render
    begin
      result = block ? block.call(bar) : bar
      bar.finish
      result
    ensure
      Kernel.print(SHOW_CURSOR)
    end
  end

  def self.confirm(question = "¿Confirmar acción?", default: true, color: "cyan", style: 3)
    choice = default ? 0 : 1
    term_w = terminal_width
    q_w = display_width(question)
    box_w = [q_w + 8, term_w - 4, 38].max
    box_w = [box_w, 64].min
    inner_w = box_w - 4

    border_cfg = BORDERS[style] || BORDERS[3]
    h_top = border_cfg[:ht] || border_cfg[:h]
    h_bot = border_cfg[:hb] || border_cfg[:h]
    v_l   = border_cfg[:vl] || border_cfg[:v]
    v_r   = border_cfg[:vr] || border_cfg[:v]

    is_rgb = (color.to_s.downcase == "rgb" || color.to_s.downcase == "rainbow" || color.to_s.downcase == "chroma")
    color_code = is_rgb ? "" : ansi_color(color, 2)
    reset_code = ansi_reset

    top_fill = (h_top * ((box_w - 2).to_f / h_top.length).ceil)[0...(box_w - 2)]
    bot_fill = (h_bot * ((box_w - 2).to_f / h_bot.length).ceil)[0...(box_w - 2)]

    drawn_lines = 0

    render_confirm = lambda do
      btn_yes = (choice == 0) ? Color.bright_green("> [ Sí ] <") : Color.gray("  [ Sí ]  ")
      btn_no  = (choice == 1) ? Color.bright_red("> [ No ] <")   : Color.gray("  [ No ]  ")
      raw_btns = (choice == 0 ? "> [ Sí ] <" : "  [ Sí ]  ") + "      " + (choice == 1 ? "> [ No ] <" : "  [ No ]  ")
      btns_vis_w = display_width(raw_btns)
      pad_total = [inner_w - btns_vis_w, 0].max
      left_p = " " * (pad_total / 2)
      right_p = " " * (pad_total - (pad_total / 2))
      btn_formatted_line = "#{left_p}#{btn_yes}      #{btn_no}#{right_p}"

      q_clean = question.to_s
      if display_width(q_clean) > inner_w
        q_clean = q_clean[0...[inner_w - 3, 1].max] + "..."
      end
      pad_q = [inner_w - display_width(q_clean), 0].max
      q_left = " " * (pad_q / 2)
      q_right = " " * (pad_q - (pad_q / 2))

      lines = []
      if is_rgb
        lines << Color.rgb("#{border_cfg[:tl]}#{top_fill}#{border_cfg[:tr]}")
        lines << "#{Color.rgb(v_l)} #{q_left}#{q_clean}#{q_right} #{Color.rgb(v_r)}"
        lines << "#{Color.rgb(v_l)} #{' ' * inner_w} #{Color.rgb(v_r)}"
        lines << "#{Color.rgb(v_l)} #{btn_formatted_line} #{Color.rgb(v_r)}"
        lines << Color.rgb("#{border_cfg[:bl]}#{bot_fill}#{border_cfg[:br]}")
      else
        lines << "#{color_code}#{border_cfg[:tl]}#{top_fill}#{border_cfg[:tr]}#{reset_code}"
        lines << "#{color_code}#{v_l}#{reset_code} #{q_left}#{q_clean}#{q_right} #{color_code}#{v_r}#{reset_code}"
        lines << "#{color_code}#{v_l}#{reset_code} #{' ' * inner_w} #{color_code}#{v_r}#{reset_code}"
        lines << "#{color_code}#{v_l}#{reset_code} #{btn_formatted_line} #{color_code}#{v_r}#{reset_code}"
        lines << "#{color_code}#{border_cfg[:bl]}#{bot_fill}#{border_cfg[:br]}#{reset_code}"
      end

      frame = lines.join("\r\n") + "\r\n"
      Kernel.print("\e[#{drawn_lines}A\e[J") if drawn_lines > 0
      Kernel.print(frame)
      $stdout.flush
      drawn_lines = lines.length
    end

    is_tty = $stdin.respond_to?(:tty?) && $stdin.tty?
    result = false

    begin
      Kernel.print(HIDE_CURSOR)
      render_confirm.call

      reader = lambda do |stream|
        while (key = GRmenu.read_key_raw(stream))
          break if key == "q" || key == "Q" || key == "\x03" || key == "\e"
          if key == "s" || key == "S" || key == "y" || key == "Y"
            result = true
            break
          elsif key == "n" || key == "N"
            result = false
            break
          elsif key == "\e[D" || key == "\eOD" || key == "\xe0K" || key == "\t" || key == "\e[C" || key == "\eOC" || key == "\xe0M"
            choice = 1 - choice
            render_confirm.call
          elsif key == "\r" || key == "\n" || key == " "
            result = (choice == 0)
            break
          end
        end
      end

      if is_tty
        $stdin.raw { |s| reader.call(s) }
      else
        reader.call($stdin)
      end
    ensure
      Kernel.print(SHOW_CURSOR)
    end

    result
  end

  def self.input(prompt_text = "Ingresa un valor:", default: "", password: false, color: "cyan", style: 3)
    text = String.new(default.to_s)
    term_w = terminal_width
    p_w = display_width(prompt_text)
    box_w = [p_w + 8, term_w - 4, 42].max
    box_w = [box_w, 64].min
    inner_w = box_w - 4

    border_cfg = BORDERS[style] || BORDERS[3]
    h_top = border_cfg[:ht] || border_cfg[:h]
    h_bot = border_cfg[:hb] || border_cfg[:h]
    v_l   = border_cfg[:vl] || border_cfg[:v]
    v_r   = border_cfg[:vr] || border_cfg[:v]

    is_rgb = (color.to_s.downcase == "rgb" || color.to_s.downcase == "rainbow" || color.to_s.downcase == "chroma")
    color_code = is_rgb ? "" : ansi_color(color, 2)
    reset_code = ansi_reset

    top_fill = (h_top * ((box_w - 2).to_f / h_top.length).ceil)[0...(box_w - 2)]
    bot_fill = (h_bot * ((box_w - 2).to_f / h_bot.length).ceil)[0...(box_w - 2)]

    drawn_lines = 0

    render_input = lambda do
      display_str = password ? ("*" * text.length) : text
      avail_inp_w = [inner_w - 4, 4].max
      if display_width(display_str) > avail_inp_w
        display_str = "..." + display_str[-[avail_inp_w - 3, 1].max..-1]
      end
      input_raw = "> #{display_str}█"
      input_padded = pad_to_width(input_raw, inner_w)

      p_clean = prompt_text.to_s
      if display_width(p_clean) > inner_w
        p_clean = p_clean[0...[inner_w - 3, 1].max] + "..."
      end
      pad_p = [inner_w - display_width(p_clean), 0].max
      p_left = " " * (pad_p / 2)
      p_right = " " * (pad_p - (pad_p / 2))

      lines = []
      if is_rgb
        lines << Color.rgb("#{border_cfg[:tl]}#{top_fill}#{border_cfg[:tr]}")
        lines << "#{Color.rgb(v_l)} #{Color.bright_yellow(p_left + p_clean + p_right)} #{Color.rgb(v_r)}"
        lines << "#{Color.rgb(v_l)} #{' ' * inner_w} #{Color.rgb(v_r)}"
        lines << "#{Color.rgb(v_l)} #{Color.bright_white(input_padded)} #{Color.rgb(v_r)}"
        lines << Color.rgb("#{border_cfg[:bl]}#{bot_fill}#{border_cfg[:br]}")
      else
        lines << "#{color_code}#{border_cfg[:tl]}#{top_fill}#{border_cfg[:tr]}#{reset_code}"
        lines << "#{color_code}#{v_l}#{reset_code} #{Color.bright_yellow(p_left + p_clean + p_right)} #{color_code}#{v_r}#{reset_code}"
        lines << "#{color_code}#{v_l}#{reset_code} #{' ' * inner_w} #{color_code}#{v_r}#{reset_code}"
        lines << "#{color_code}#{v_l}#{reset_code} #{Color.bright_white(input_padded)} #{color_code}#{v_r}#{reset_code}"
        lines << "#{color_code}#{border_cfg[:bl]}#{bot_fill}#{border_cfg[:br]}#{reset_code}"
      end

      frame = lines.join("\r\n") + "\r\n"
      Kernel.print("\e[#{drawn_lines}A\e[J") if drawn_lines > 0
      Kernel.print(frame)
      $stdout.flush
      drawn_lines = lines.length
    end

    is_tty = $stdin.respond_to?(:tty?) && $stdin.tty?

    begin
      Kernel.print(HIDE_CURSOR)
      render_input.call

      reader = lambda do |stream|
        while (key = GRmenu.read_key_raw(stream))
          break if key == "\x03" || key == "\e"
          if key == "\r" || key == "\n"
            break
          elsif key == "\x7f" || key == "\b" || key == "\x08"
            text.chop!
            render_input.call
          elsif key == "\x15"
            text.clear
            render_input.call
          elsif key =~ /^[[:print:]]$/
            text << key if text.length < (inner_w - 4)
            render_input.call
          end
        end
      end

      if is_tty
        $stdin.raw { |s| reader.call(s) }
      else
        reader.call($stdin)
      end
    ensure
      Kernel.print(SHOW_CURSOR)
    end

    text
  end

  def self.checkbox(items, title: "Selección Múltiple", subtitle: "Espacio: Marcar/Desmarcar | a: Todos | n: Ninguno | i: Invertir | Enter: Confirmar", color: nil, style: nil, page_size: nil, min_width: nil, preselected: [])
    cb_sec = (@@global_theme.is_a?(Hash) && @@global_theme.dig(:sections, "checkbox")) || {}
    item_list = items.is_a?(Array) ? items : Array(items)
    return [] if item_list.empty?
    chk_mark = cb_sec["checked_mark"] || "[X]"
    unchk_mark = cb_sec["unchecked_mark"] || "[ ]"

    parsed_items = item_list.map do |it|
      case it
      when Array
        name = it[0].to_s
        is_chk = it.length > 1 ? !!it[1] : false
        desc = it.length > 2 ? it[2].to_s : ""
        { name: name, checked: is_chk, desc: desc, original: it }
      when Hash
        name = (it[:name] || it["name"] || it[:title] || it["title"] || "Item").to_s
        is_chk = !!(it[:checked] || it["checked"] || it[:selected] || it["selected"])
        desc = (it[:desc] || it["desc"] || it[:description] || it["description"]).to_s
        { name: name, checked: is_chk, desc: desc, original: it }
      else
        { name: it.to_s, checked: false, desc: "", original: it }
      end
    end

    preselected.each do |p|
      if p.is_a?(Integer) && parsed_items[p]
        parsed_items[p][:checked] = true
      else
        it = parsed_items.find { |pi| pi[:name] == p.to_s }
        it[:checked] = true if it
      end
    end

    index = 0
    rgb_tick = 0.0
    drawn_lines = 0
    cb_color = (color || cb_sec["color"] || "cyan").to_s
    style_num = (style || cb_sec["style"] || 3).to_i
    is_rgb = (cb_color.downcase == "rgb" || cb_color.downcase == "rainbow" || cb_color.downcase == "chroma")
    border_cfg = BORDERS[style_num] || BORDERS[3]
    h_top = border_cfg[:ht] || border_cfg[:h]
    h_bot = border_cfg[:hb] || border_cfg[:h]
    v_l = border_cfg[:vl] || border_cfg[:v]
    v_r = border_cfg[:vr] || border_cfg[:v]

    render_frame = lambda do
      term_w = terminal_width
      term_h = terminal_height

      max_name_w = parsed_items.map { |it| display_width(it[:name]) }.max || 10
      req_w = [max_name_w + 12, display_width(title) + 6, display_width(subtitle) + 4, min_width || 38].max
      box_w = [req_w, term_w - 4].min
      inner_w = box_w - 4

      top_fill = (h_top * ((box_w - 2).to_f / h_top.length).ceil)[0...(box_w - 2)]
      bot_fill = (h_bot * ((box_w - 2).to_f / h_bot.length).ceil)[0...(box_w - 2)]
      mid_fill = (h_top * ((box_w - 2).to_f / h_top.length).ceil)[0...(box_w - 2)]

      total_items = parsed_items.length
      max_visible = page_size ? [page_size, total_items, term_h - 10].min : [total_items, term_h - 10].min
      max_visible = [max_visible, 1].max

      start_idx = 0
      end_idx = total_items - 1
      if total_items > max_visible
        half = max_visible / 2
        start_idx = [[index - half, 0].max, total_items - max_visible].min
        end_idx = start_idx + max_visible - 1
      end

      lines = []
      if is_rgb
        lines << Color.rgb("#{border_cfg[:tl]}#{top_fill}#{border_cfg[:tr]}", rgb_tick)
        unless title.to_s.empty?
          t_clean = title.to_s
          t_clean = t_clean[0...[inner_w - 3, 1].max] + "..." if display_width(t_clean) > inner_w
          pad_t = [inner_w - display_width(t_clean), 0].max
          t_line = (" " * (pad_t / 2)) + t_clean + (" " * (pad_t - (pad_t / 2)))
          lines << "#{Color.rgb(v_l, rgb_tick)} #{Color.rgb(t_line, rgb_tick + 0.2)} #{Color.rgb(v_r, rgb_tick)}"
          lines << Color.rgb("#{v_l}#{mid_fill}#{v_r}", rgb_tick)
        end
        if start_idx > 0
          up_t = "▲ (+#{start_idx} arriba)"
          pad_u = [inner_w - display_width(up_t), 0].max
          lines << "#{Color.rgb(v_l, rgb_tick)} #{Color.gray(" " * (pad_u / 2) + up_t + " " * (pad_u - (pad_u / 2)))} #{Color.rgb(v_r, rgb_tick)}"
        end
        (start_idx..end_idx).each do |i|
          it = parsed_items[i]
          mark = it[:checked] ? chk_mark : unchk_mark
          is_active = (i == index)
          max_name_w = [inner_w - display_width(mark) - 4, 4].max
          name_str = it[:name].to_s
          name_str = name_str[0...[max_name_w - 3, 1].max] + "..." if display_width(name_str) > max_name_w
          raw_line = "#{is_active ? '> ' : '  '}#{mark} #{name_str}"
          line_padded = pad_to_width(raw_line, inner_w)
          if is_active
            lines << "#{Color.rgb(v_l, rgb_tick)} #{Color.rgb(line_padded, rgb_tick + 0.4)} #{Color.rgb(v_r, rgb_tick)}"
          elsif it[:checked]
            lines << "#{Color.rgb(v_l, rgb_tick)} #{Color.bright_green(line_padded)} #{Color.rgb(v_r, rgb_tick)}"
          else
            lines << "#{Color.rgb(v_l, rgb_tick)} #{Color.white(line_padded)} #{Color.rgb(v_r, rgb_tick)}"
          end
        end
        if end_idx < (total_items - 1)
          rem = total_items - 1 - end_idx
          dn_t = "▼ (+#{rem} abajo)"
          pad_d = [inner_w - display_width(dn_t), 0].max
          lines << "#{Color.rgb(v_l, rgb_tick)} #{Color.gray(" " * (pad_d / 2) + dn_t + " " * (pad_d - (pad_d / 2)))} #{Color.rgb(v_r, rgb_tick)}"
        end
        unless subtitle.to_s.empty?
          lines << Color.rgb("#{v_l}#{mid_fill}#{v_r}", rgb_tick)
          s_clean = subtitle.to_s
          s_clean = s_clean[0...[inner_w - 3, 1].max] + "..." if display_width(s_clean) > inner_w
          pad_sub = [inner_w - display_width(s_clean), 0].max
          sub_padded = (" " * (pad_sub / 2)) + s_clean + (" " * (pad_sub - (pad_sub / 2)))
          lines << "#{Color.rgb(v_l, rgb_tick)} #{Color.gray(sub_padded)} #{Color.rgb(v_r, rgb_tick)}"
        end
        lines << Color.rgb("#{border_cfg[:bl]}#{bot_fill}#{border_cfg[:br]}", rgb_tick)
      else
        color_code = ansi_color(cb_color, 2)
        reset_code = ansi_reset
        lines << "#{color_code}#{border_cfg[:tl]}#{top_fill}#{border_cfg[:tr]}#{reset_code}"
        unless title.to_s.empty?
          t_clean = title.to_s
          t_clean = t_clean[0...[inner_w - 3, 1].max] + "..." if display_width(t_clean) > inner_w
          pad_t = [inner_w - display_width(t_clean), 0].max
          t_line = (" " * (pad_t / 2)) + t_clean + (" " * (pad_t - (pad_t / 2)))
          lines << "#{color_code}#{v_l}#{reset_code} #{Color.bright_yellow(t_line)} #{color_code}#{v_r}#{reset_code}"
          lines << "#{color_code}#{v_l}#{top_fill}#{v_r}#{reset_code}"
        end
        if start_idx > 0
          up_t = "▲ (+#{start_idx} arriba)"
          pad_u = [inner_w - display_width(up_t), 0].max
          lines << "#{color_code}#{v_l}#{reset_code} #{Color.gray(" " * (pad_u / 2) + up_t + " " * (pad_u - (pad_u / 2)))} #{color_code}#{v_r}#{reset_code}"
        end
        (start_idx..end_idx).each do |i|
          it = parsed_items[i]
          mark = it[:checked] ? chk_mark : unchk_mark
          is_active = (i == index)
          max_name_w = [inner_w - display_width(mark) - 4, 4].max
          name_str = it[:name].to_s
          name_str = name_str[0...[max_name_w - 3, 1].max] + "..." if display_width(name_str) > max_name_w
          raw_line = "#{is_active ? '> ' : '  '}#{mark} #{name_str}"
          line_padded = pad_to_width(raw_line, inner_w)
          if is_active
            lines << "#{color_code}#{v_l}#{reset_code} #{Color.bright_yellow(line_padded)} #{color_code}#{v_r}#{reset_code}"
          elsif it[:checked]
            lines << "#{color_code}#{v_l}#{reset_code} #{Color.bright_green(line_padded)} #{color_code}#{v_r}#{reset_code}"
          else
            lines << "#{color_code}#{v_l}#{reset_code} #{Color.white(line_padded)} #{color_code}#{v_r}#{reset_code}"
          end
        end
        if end_idx < (total_items - 1)
          rem = total_items - 1 - end_idx
          dn_t = "▼ (+#{rem} abajo)"
          pad_d = [inner_w - display_width(dn_t), 0].max
          lines << "#{color_code}#{v_l}#{reset_code} #{Color.gray(" " * (pad_d / 2) + dn_t + " " * (pad_d - (pad_d / 2)))} #{color_code}#{v_r}#{reset_code}"
        end
        unless subtitle.to_s.empty?
          lines << "#{color_code}#{v_l}#{top_fill}#{v_r}#{reset_code}"
          s_clean = subtitle.to_s
          s_clean = s_clean[0...[inner_w - 3, 1].max] + "..." if display_width(s_clean) > inner_w
          pad_sub = [inner_w - display_width(s_clean), 0].max
          sub_padded = (" " * (pad_sub / 2)) + s_clean + (" " * (pad_sub - (pad_sub / 2)))
          lines << "#{color_code}#{v_l}#{reset_code} #{Color.gray(sub_padded)} #{color_code}#{v_r}#{reset_code}"
        end
        lines << "#{color_code}#{border_cfg[:bl]}#{bot_fill}#{border_cfg[:br]}#{reset_code}"
      end

      frame = lines.join("\r\n") + "\r\n"
      Kernel.print("\e[#{drawn_lines}A\e[J") if drawn_lines > 0
      Kernel.print(frame)
      $stdout.flush
      drawn_lines = lines.length
    end

    is_tty = $stdin.respond_to?(:tty?) && $stdin.tty?
    submitted = false

    begin
      Kernel.print(HIDE_CURSOR)
      render_frame.call

      reader = lambda do |stream|
        while true
          if is_rgb
            ready = false
            if stream.respond_to?(:to_io) || stream.is_a?(IO)
              begin
                sr = IO.select([stream], nil, nil, 0.035)
                ready = true if sr && sr[0] && !sr[0].empty?
              rescue StandardError
                ready = true
              end
            else
              ready = true
            end
            unless ready
              rgb_tick += 0.08
              render_frame.call
              next
            end
          end

          key = GRmenu.read_key_raw(stream)
          break if key.nil? || key == "\x03" || key == "\x04" || key == "q" || key == "Q" || key == "\e"

          if key == "\e[A" || key == "\eOA" || key == "\xe0H" || key == "\x00H"
            index = (index - 1) % parsed_items.length
            render_frame.call
          elsif key == "\e[B" || key == "\eOB" || key == "\xe0P" || key == "\x00P"
            index = (index + 1) % parsed_items.length
            render_frame.call
          elsif key == " "
            parsed_items[index][:checked] = !parsed_items[index][:checked]
            render_frame.call
          elsif key == "a" || key == "A"
            parsed_items.each { |it| it[:checked] = true }
            render_frame.call
          elsif key == "n" || key == "N"
            parsed_items.each { |it| it[:checked] = false }
            render_frame.call
          elsif key == "i" || key == "I"
            parsed_items.each { |it| it[:checked] = !it[:checked] }
            render_frame.call
          elsif key == "\r" || key == "\n"
            submitted = true
            break
          end
        end
      end

      if is_tty
        $stdin.raw { |s| reader.call(s) }
      else
        reader.call($stdin)
      end
    ensure
      Kernel.print(SHOW_CURSOR)
    end

    if submitted
      selected = parsed_items.select { |it| it[:checked] }
      selected.map { |it| it[:original] }
    else
      []
    end
  end
  class << self
    alias_method :select_multi, :checkbox
    alias_method :multiselect, :checkbox
  end

  def self.slider(prompt = "Selecciona un valor:", min: 0, max: 100, step: 1, default: nil, unit: "", color: nil, style: nil, width: 46)
    sl_sec = (@@global_theme.is_a?(Hash) && @@global_theme.dig(:sections, "slider")) || {}
    val = (default || min).to_f.clamp(min.to_f, max.to_f)
    step_val = [step.to_f, 0.001].max
    drawn_lines = 0
    rgb_tick = 0.0
    sl_color = (color || sl_sec["color"] || "cyan").to_s
    style_num = (style || sl_sec["style"] || 3).to_i
    is_rgb = (sl_color.downcase == "rgb" || sl_color.downcase == "rainbow" || sl_color.downcase == "chroma")

    border_cfg = BORDERS[style_num] || BORDERS[3]
    h_top = border_cfg[:ht] || border_cfg[:h]
    h_bot = border_cfg[:hb] || border_cfg[:h]
    v_l = border_cfg[:vl] || border_cfg[:v]
    v_r = border_cfg[:vr] || border_cfg[:v]

    render_slider = lambda do
      term_w = terminal_width
      box_w = [width, term_w - 4, display_width(prompt) + 8, 38].max
      box_w = [box_w, term_w - 2].min
      inner_w = box_w - 4

      top_fill = (h_top * ((box_w - 2).to_f / h_top.length).ceil)[0...(box_w - 2)]
      bot_fill = (h_bot * ((box_w - 2).to_f / h_bot.length).ceil)[0...(box_w - 2)]

      val_display = (val % 1 == 0) ? val.to_i.to_s : val.round(2).to_s
      val_str = unit.to_s.empty? ? val_display : "#{val_display} #{unit}"

      range_span = (max - min).to_f
      range_span = 1.0 if range_span <= 0
      fraction = ((val - min).to_f / range_span).clamp(0.0, 1.0)

      avail_bar_w = [inner_w - display_width(val_str) - 4, 6].max
      filled_len = (fraction * avail_bar_w).round
      empty_len = [avail_bar_w - filled_len, 0].max

      p_clean = prompt.to_s
      if display_width(p_clean) > inner_w
        p_clean = p_clean[0...[inner_w - 3, 1].max] + "..."
      end
      pad_p = [inner_w - display_width(p_clean), 0].max
      p_line = (" " * (pad_p / 2)) + p_clean + (" " * (pad_p - (pad_p / 2)))

      instr = (inner_w >= 30) ? "← / → Ajustar | Enter Guardar" : "←/→: Ajustar | Enter: Ok"
      if display_width(instr) > inner_w
        instr = instr[0...[inner_w - 3, 1].max] + "..."
      end
      pad_i = [inner_w - display_width(instr), 0].max
      i_line = (" " * (pad_i / 2)) + instr + (" " * (pad_i - (pad_i / 2)))

      lines = []
      if is_rgb
        lines << Color.rgb("#{border_cfg[:tl]}#{top_fill}#{border_cfg[:tr]}", rgb_tick)
        lines << "#{Color.rgb(v_l, rgb_tick)} #{Color.rgb(p_line, rgb_tick + 0.3)} #{Color.rgb(v_r, rgb_tick)}"
        lines << "#{Color.rgb(v_l, rgb_tick)} #{' ' * inner_w} #{Color.rgb(v_r, rgb_tick)}"

        filled_part = Color.rgb("█" * filled_len, rgb_tick + 0.5)
        empty_part  = Color.gray("░" * empty_len)
        bar_raw = "[#{filled_part}#{empty_part}] #{Color.bright_white(val_str)}"
        bar_vis_w = 2 + filled_len + empty_len + 1 + display_width(val_str)
        pad_b = [inner_w - bar_vis_w, 0].max
        lines << "#{Color.rgb(v_l, rgb_tick)} #{bar_raw}#{' ' * pad_b} #{Color.rgb(v_r, rgb_tick)}"
        lines << "#{Color.rgb(v_l, rgb_tick)} #{' ' * inner_w} #{Color.rgb(v_r, rgb_tick)}"
        lines << "#{Color.rgb(v_l, rgb_tick)} #{Color.gray(i_line)} #{Color.rgb(v_r, rgb_tick)}"
        lines << Color.rgb("#{border_cfg[:bl]}#{bot_fill}#{border_cfg[:br]}", rgb_tick)
      else
        color_code = ansi_color(sl_color, 2)
        reset_code = ansi_reset

        bar_raw = "[#{"█" * filled_len}#{"░" * empty_len}] #{val_str}"
        pad_b = [inner_w - display_width(bar_raw), 0].max
        bar_line = bar_raw + (" " * pad_b)

        lines << "#{color_code}#{border_cfg[:tl]}#{top_fill}#{border_cfg[:tr]}#{reset_code}"
        lines << "#{color_code}#{v_l}#{reset_code} #{Color.bright_yellow(p_line)} #{color_code}#{v_r}#{reset_code}"
        lines << "#{color_code}#{v_l}#{reset_code} #{' ' * inner_w} #{color_code}#{v_r}#{reset_code}"
        lines << "#{color_code}#{v_l}#{reset_code} #{bar_line} #{color_code}#{v_r}#{reset_code}"
        lines << "#{color_code}#{v_l}#{reset_code} #{' ' * inner_w} #{color_code}#{v_r}#{reset_code}"
        lines << "#{color_code}#{v_l}#{reset_code} #{Color.gray(i_line)} #{color_code}#{v_r}#{reset_code}"
        lines << "#{color_code}#{border_cfg[:bl]}#{bot_fill}#{border_cfg[:br]}#{reset_code}"
      end

      frame = lines.join("\r\n") + "\r\n"
      Kernel.print("\e[#{drawn_lines}A\e[J") if drawn_lines > 0
      Kernel.print(frame)
      $stdout.flush
      drawn_lines = lines.length
    end

    is_tty = $stdin.respond_to?(:tty?) && $stdin.tty?

    begin
      Kernel.print(HIDE_CURSOR)
      render_slider.call

      reader = lambda do |stream|
        while true
          if is_rgb
            ready = false
            if stream.respond_to?(:to_io) || stream.is_a?(IO)
              begin
                sr = IO.select([stream], nil, nil, 0.035)
                ready = true if sr && sr[0] && !sr[0].empty?
              rescue StandardError
                ready = true
              end
            else
              ready = true
            end
            unless ready
              rgb_tick += 0.08
              render_slider.call
              next
            end
          end

          key = GRmenu.read_key_raw(stream)
          break if key.nil? || key == "\x03" || key == "\x04" || key == "q" || key == "Q" || key == "\e"

          if key == "\e[D" || key == "\eOD" || key == "\xe0K" || key == "\x00K" || key == "h" || key == "H"
            val = (val - step_val).clamp(min.to_f, max.to_f)
            render_slider.call
          elsif key == "\e[C" || key == "\eOC" || key == "\xe0M" || key == "\x00M" || key == "l" || key == "L"
            val = (val + step_val).clamp(min.to_f, max.to_f)
            render_slider.call
          elsif key == "\e[B" || key == "\eOB" || key == "\xe0P" || key == "\x00P"
            val = (val - step_val * 5).clamp(min.to_f, max.to_f)
            render_slider.call
          elsif key == "\e[A" || key == "\eOA" || key == "\xe0H" || key == "\x00H"
            val = (val + step_val * 5).clamp(min.to_f, max.to_f)
            render_slider.call
          elsif key == "\r" || key == "\n"
            break
          end
        end
      end

      if is_tty
        $stdin.raw { |s| reader.call(s) }
      else
        reader.call($stdin)
      end
    ensure
      Kernel.print(SHOW_CURSOR)
    end

    (val % 1 == 0) ? val.to_i : val.round(2)
  end
  class << self
    alias_method :range, :slider
  end

  def self.read_key_raw(input_stream)
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

  class SetStyle
    def initialize(
      border:   { color: "cyan",    level: 1 },
      options:  { color: "white",   level: 1 },
      focus:    { color: "green",   level: 2 },
      title:    { color: "yellow",  level: 2 },
      banner:   { color: "magenta", level: 2 },
      subtitle: { color: "cyan",    level: 2 },
      divider:  { color: "blue",    level: 1 },
      font:     1,
      desc_prefix: "[i]"
    )
      @border   = border.dup
      @options  = options.dup
      @focus    = focus.dup
      @title    = title.dup
      @banner   = banner.dup
      @subtitle = subtitle.dup
      @divider  = divider.dup
      @font     = font.to_i
      @desc_prefix = desc_prefix.to_s
    end

    def desc_prefix(prefix_str = nil)
      return @desc_prefix if prefix_str.nil?
      @desc_prefix = prefix_str.to_s
      self
    end
    alias_method :description_prefix, :desc_prefix
    alias_method :desc_prefix=, :desc_prefix
    alias_method :description_prefix=, :desc_prefix

    def border(color_name = nil, brightness_level = 1)
      return @border if color_name.nil?
      @border = parse_color(color_name, brightness_level)
      self
    end
    alias_method :Border, :border
    alias_method :set_border, :border
    alias_method :border=, :border

    def options(color_name = nil, brightness_level = 1)
      return @options if color_name.nil?
      @options = parse_color(color_name, brightness_level)
      self
    end
    alias_method :Options, :options
    alias_method :set_options, :options
    alias_method :options=, :options

    def focus(color_name = nil, brightness_level = 2)
      return @focus if color_name.nil?
      @focus = parse_color(color_name, brightness_level)
      self
    end
    alias_method :Focus, :focus
    alias_method :set_focus, :focus
    alias_method :focus=, :focus

    def title(color_name = nil, brightness_level = 2)
      return @title if color_name.nil?
      @title = parse_color(color_name, brightness_level)
      self
    end
    alias_method :Title, :title
    alias_method :set_title, :title
    alias_method :title=, :title

    def banner(color_name = nil, brightness_level = 2)
      return @banner if color_name.nil?
      @banner = parse_color(color_name, brightness_level)
      self
    end
    alias_method :Banner, :banner
    alias_method :set_banner, :banner
    alias_method :banner=, :banner

    def subtitle(color_name = nil, brightness_level = 2)
      return @subtitle if color_name.nil?
      @subtitle = parse_color(color_name, brightness_level)
      self
    end
    alias_method :Subtitle, :subtitle
    alias_method :set_subtitle, :subtitle
    alias_method :subtitle=, :subtitle

    def divider(color_name = nil, brightness_level = 1)
      return @divider if color_name.nil?
      @divider = parse_color(color_name, brightness_level)
      self
    end
    alias_method :Divider, :divider
    alias_method :set_divider, :divider
    alias_method :divider=, :divider

    def font(font_id = nil)
      return @font if font_id.nil?
      @font = font_id.to_i
      self
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

      def desc_prefix(prefix_str = nil)
        @default_desc_prefix ||= "[i]"
        return @default_desc_prefix if prefix_str.nil?
        @default_desc_prefix = prefix_str.to_s
      end
      alias_method :description_prefix, :desc_prefix
      alias_method :desc_prefix=, :desc_prefix
      alias_method :description_prefix=, :desc_prefix
    end
  end

  module GRprint
    module_function

    def p(text = "", ending = "\r\n")
      Kernel.print("#{text}#{ending}")
    end
  end

  attr_accessor :functions, :title, :subtitle, :banner, :banner_style, :divider, :style, :index, :style_config, :center, :page_size, :search, :columns, :query, :image, :image_width

  alias_method :options, :functions
  alias_method :options=, :functions=
  alias_method :selected_index, :index
  alias_method :selected_index=, :index=
  alias_method :SetStyle, :style_config
  alias_method :set_style, :style_config
  alias_method :description, :subtitle
  alias_method :description=, :subtitle=

  def self.STYLES; STYLES; end
  def self.COLORS; COLORS; end
  def self.BORDERS; BORDERS; end
  def self.FONTS; FONTS; end
  def self.FONT; FONT_1; end

  def self.terminal_width
    cols = $stdout.winsize[1] rescue nil
    cols = $stdin.winsize[1] rescue nil if cols.nil? || cols <= 0
    (cols && cols > 0) ? cols : (ENV['COLUMNS'] ? ENV['COLUMNS'].to_i : 80)
  rescue StandardError
    80
  end

  def self.terminal_height
    rows = $stdout.winsize[0] rescue nil
    rows = $stdin.winsize[0] rescue nil if rows.nil? || rows <= 0
    (rows && rows > 0) ? rows : (ENV['LINES'] ? ENV['LINES'].to_i : 24)
  rescue StandardError
    24
  end

  def self.clear_screen
    Kernel.print(CLEAR_SCREEN_SEQUENCE)
  end
  class << self
    alias_method :clr, :clear_screen
  end

  @@global_theme = {}

  def self.current_theme
    @@global_theme
  end

  def self.parse_config_text(text)
    data = { global: {}, sections: {} }
    current_sec = nil
    current_sec_data = {}

    text.to_s.each_line do |line|
      line = line.strip
      next if line.empty? || line.start_with?("#")
      next if line.start_with?("GRmenu::config")

      if line.start_with?("<<")
        sec_name = line[2..-1].strip.downcase
        current_sec = sec_name
        current_sec_data = {}
      elsif line == ">>"
        if current_sec
          data[:sections][current_sec] = current_sec_data
          current_sec = nil
        end
      elsif line.include?("::")
        key, _, val = line.partition("::")
        key = key.strip.sub(/^@/, '').downcase
        val = val.strip.sub(/^["']/, '').sub(/["']$/, '')
        if current_sec
          current_sec_data[key] = val
        else
          data[:global][key] = val
        end
      end
    end
    data
  end

  def self.find_theme_file(path_or_name)
    name = path_or_name.to_s
    candidates = [
      name,
      "#{name}.gr",
      find_data_file("themes/#{name}.gr"),
      find_data_file("themes/#{name}"),
      File.expand_path("data/themes/#{name}.gr", __dir__),
      File.expand_path("data/themes/#{name}", __dir__),
      File.expand_path("../data/themes/#{name}.gr", __dir__),
      File.expand_path("../data/themes/#{name}", __dir__)
    ].compact
    candidates.find { |p| File.exist?(p) }
  end

  def self.import_config(path_or_name)
    path = find_theme_file(path_or_name)
    raise "No se encontro el tema: #{path_or_name}" unless path && File.exist?(path)
    text = File.read(path)
    parsed = parse_config_text(text)
    apply_parsed_theme(parsed)
    @@global_theme = parsed
    path
  end

  def self.theme(name)
    import_config(name)
  end

  def self.extract_color_and_level(val, default_level = 1)
    return ["white", default_level] if val.nil?
    parts = val.to_s.split(":")
    c_name = parts[0].to_s.strip
    lvl = parts[1] ? parts[1].to_i : default_level
    [c_name, lvl]
  end

  def self.apply_parsed_theme(parsed)
    sec = parsed[:sections] || {}
    glob = parsed[:global] || {}
    m = (sec["menu"] || {}).merge(glob)

    if m && !m.empty?
      if m["border"] || m["border_color"]
        c, l = extract_color_and_level(m["border"] || m["border_color"], 1)
        SetStyle.border(c, l)
      end
      if m["title"] || m["title_color"]
        c, l = extract_color_and_level(m["title"] || m["title_color"], 2)
        SetStyle.title(c, l)
      end
      if m["focus"] || m["focus_color"]
        c, l = extract_color_and_level(m["focus"] || m["focus_color"], 2)
        SetStyle.focus(c, l)
      end
      if m["options"] || m["options_color"]
        c, l = extract_color_and_level(m["options"] || m["options_color"], 1)
        SetStyle.options(c, l)
      end
      if m["banner"] || m["banner_color"]
        c, l = extract_color_and_level(m["banner"] || m["banner_color"], 2)
        SetStyle.banner(c, l)
      end
      if m["subtitle"] || m["subtitle_color"]
        c, l = extract_color_and_level(m["subtitle"] || m["subtitle_color"], 1)
        SetStyle.subtitle(c, l)
      end
      if m["divider"] || m["divider_color"]
        c, l = extract_color_and_level(m["divider"] || m["divider_color"], 1)
        SetStyle.divider(c, l)
      end
      if m["desc_prefix"] || m["description_prefix"] || m["prefix"]
        SetStyle.desc_prefix(m["desc_prefix"] || m["description_prefix"] || m["prefix"])
      end
      SetStyle.font(m["font"].to_i) if m["font"]
    end

    sec.each do |k, v|
      next unless v.is_a?(Hash)
      c_val = v["color"] || v["border"] || v["options"] || v["focus"] || v["title"] || v["banner"] || v["subtitle"] || v["divider"]
      c, l = extract_color_and_level(c_val, (v["level"] || 1).to_i)
      case k
      when "border"
        SetStyle.border(c, l)
      when "options"
        SetStyle.options(c, l)
      when "focus"
        SetStyle.focus(c, l)
      when "title"
        SetStyle.title(c, l)
      when "banner"
        SetStyle.banner(c, l)
      when "subtitle"
        SetStyle.subtitle(c, l)
      when "divider"
        SetStyle.divider(c, l)
      end
    end
    SetStyle.font(glob["font"].to_i) if glob["font"]
  end

  def self.style(css_content)
    parsed = parse_config_text(css_content)
    apply_parsed_theme(parsed)
    parsed
  end

  def self.export_config(path = nil)
    if path.nil?
      caller_loc = caller_locations.find { |c| !c.path.include?(__FILE__) }
      base = caller_loc ? caller_loc.path.sub(/\.rb$/, '') : "theme"
      path = "#{base}.gr"
    end
    lines = ["GRmenu::config<-1->", ""]
    lines << "@theme:: \"#{File.basename(path, '.gr').capitalize}\""
    lines << "@author:: \"grcode\""
    lines << "@version:: \"1.0\""
    lines << ""
    lines << "<<menu"
    lines << "  style:: 3"
    lines << "  banner_style:: 3"
    lines << "  font:: #{SetStyle.font}"
    lines << "  animate:: rgb"
    lines << "  center:: true"
    lines << "  border:: #{SetStyle.border[:color]}:#{SetStyle.border[:level]}"
    lines << "  title:: #{SetStyle.title[:color]}:#{SetStyle.title[:level]}"
    lines << "  focus:: #{SetStyle.focus[:color]}:#{SetStyle.focus[:level]}"
    lines << "  options:: #{SetStyle.options[:color]}:#{SetStyle.options[:level]}"
    lines << "  banner:: #{SetStyle.banner[:color]}:#{SetStyle.banner[:level]}"
    lines << "  subtitle:: #{SetStyle.subtitle[:color]}:#{SetStyle.subtitle[:level]}"
    lines << "  divider:: #{SetStyle.divider[:color]}:#{SetStyle.divider[:level]}"
    lines << ">>"
    lines << ""
    lines << "<<table"
    lines << "  style:: 3"
    lines << "  header_color:: yellow:2"
    lines << "  border_color:: rgb:2"
    lines << "  selected_row:: green:2"
    lines << "  row_color:: white:1"
    lines << "  zebra_striping:: true"
    lines << ">>"
    lines << ""
    lines << "<<card"
    lines << "  style:: 7"
    lines << "  border_color:: cyan:2"
    lines << "  title_color:: yellow:2"
    lines << "  content_color:: white:1"
    lines << ">>"
    lines << ""
    lines << "<<slider"
    lines << "  style:: 3"
    lines << "  color:: rgb:2"
    lines << "  fill_char:: █"
    lines << "  empty_char:: ░"
    lines << ">>"
    lines << ""
    lines << "<<checkbox"
    lines << "  style:: 3"
    lines << "  color:: rgb:2"
    lines << "  checked_mark:: [X]"
    lines << "  unchecked_mark:: [ ]"
    lines << ">>"
    lines << ""
    File.write(path, lines.join("\n") + "\n")
    path
  end

  def self.export_from_file(source_file, target_path = nil)
    raise "No existe #{source_file}" unless File.exist?(source_file)
    orig_draw = instance_method(:draw) rescue nil
    extracted = nil
    define_method(:draw) do |*|
      extracted = {
        style: @style,
        banner_style: @banner_style,
        font: @style_config&.font,
        animate: @animate,
        border: @style_config&.border,
        title: @style_config&.title,
        focus: @style_config&.focus,
        options: @style_config&.options,
        banner: @style_config&.banner,
        subtitle: @style_config&.subtitle,
        divider: @style_config&.divider
      }
      throw :grmenu_export_completed
    end
    begin
      catch(:grmenu_export_completed) do
        load(File.expand_path(source_file))
      end
    ensure
      define_method(:draw, orig_draw) if orig_draw
    end
    out = target_path || source_file.sub(/\.rb$/, '') + ".gr"
    if extracted && extracted[:border]
      lines = ["GRmenu::config<-1->", ""]
      lines << "@theme:: \"#{File.basename(out, '.gr').capitalize}\""
      lines << "@author:: \"grcode\""
      lines << "@version:: \"1.0\""
      lines << ""
      lines << "<<menu"
      lines << "  style:: #{extracted[:style] || 3}"
      lines << "  banner_style:: #{extracted[:banner_style] || 3}"
      lines << "  font:: #{extracted[:font] || 1}"
      lines << "  animate:: #{extracted[:animate] || 'rgb'}"
      lines << "  center:: true"
      lines << "  border:: #{extracted[:border][:color]}:#{extracted[:border][:level]}"
      lines << "  title:: #{extracted[:title][:color]}:#{extracted[:title][:level]}"
      lines << "  focus:: #{extracted[:focus][:color]}:#{extracted[:focus][:level]}"
      lines << "  options:: #{extracted[:options][:color]}:#{extracted[:options][:level]}"
      lines << "  banner:: #{extracted[:banner][:color]}:#{extracted[:banner][:level]}"
      lines << "  subtitle:: #{extracted[:subtitle][:color]}:#{extracted[:subtitle][:level]}"
      lines << "  divider:: #{extracted[:divider][:color]}:#{extracted[:divider][:level]}"
      lines << ">>"
      lines << ""
      lines << "<<table"
      lines << "  style:: #{extracted[:style] || 3}"
      lines << "  header_color:: yellow:2"
      lines << "  border_color:: rgb:2"
      lines << "  selected_row:: green:2"
      lines << "  row_color:: white:1"
      lines << "  zebra_striping:: true"
      lines << ">>"
      lines << ""
      lines << "<<card"
      lines << "  style:: 7"
      lines << "  border_color:: cyan:2"
      lines << "  title_color:: yellow:2"
      lines << "  content_color:: white:1"
      lines << ">>"
      lines << ""
      lines << "<<slider"
      lines << "  style:: 3"
      lines << "  color:: rgb:2"
      lines << "  fill_char:: █"
      lines << "  empty_char:: ░"
      lines << ">>"
      lines << ""
      lines << "<<checkbox"
      lines << "  style:: 3"
      lines << "  color:: rgb:2"
      lines << "  checked_mark:: [X]"
      lines << "  unchecked_mark:: [ ]"
      lines << ">>"
      lines << ""
      File.write(out, lines.join("\n") + "\n")
      out
    else
      export_config(out)
    end
  end

  def self.split_ansi_chars(str)
    segments = []
    current_style = String.new("")
    in_escape = false
    escape_buf = String.new("")

    str.to_s.each_char do |ch|
      if ch == "\e"
        in_escape = true
        escape_buf << ch
        next
      end
      if in_escape
        escape_buf << ch
        if ch =~ /[a-zA-Z]/
          in_escape = false
          current_style = escape_buf.dup
          escape_buf.clear
        end
        next
      end
      segments << { char: ch, style: current_style.dup }
    end
    segments
  end

  def self.animate_render(lines, type = :diagonal, delay = 0.012)
    type_str = type.to_s.downcase
    return if lines.nil? || lines.empty?
    rst = ansi_reset

    case type_str
    when "diagonal"
      parsed_rows = lines.map { |l| split_ansi_chars(l) }
      max_len = parsed_rows.map(&:length).max || 0
      total_steps = max_len + (parsed_rows.length * 2)
      step = 0
      while step <= total_steps
        buffer = String.new(CURSOR_HOME)
        parsed_rows.each_with_index do |row_segs, y|
          rendered_row = String.new("")
          row_segs.each_with_index do |seg, x|
            if (x + y * 2) <= step
              rendered_row << seg[:style] << seg[:char] << rst
            else
              rendered_row << " "
            end
          end
          buffer << rendered_row << CLEAR_TO_EOL << "\r\n"
        end
        buffer << CLEAR_TO_EOS
        Kernel.print(buffer)
        $stdout.flush
        sleep(delay)
        step += 4
      end
    when "linear"
      buffer = String.new(CURSOR_HOME)
      lines.each do |line|
        Kernel.print("#{line}#{CLEAR_TO_EOL}\r\n")
        $stdout.flush
        sleep(delay * 3)
      end
    when "fade"
      [1, 2].each do |lvl|
        buffer = String.new(CURSOR_HOME)
        lines.each do |line|
          clean = line.gsub(/\e\[[0-9;]*m/, '')
          buffer << ansi_color("white", lvl) << clean << rst << CLEAR_TO_EOL << "\r\n"
        end
        buffer << CLEAR_TO_EOS
        Kernel.print(buffer)
        $stdout.flush
        sleep(delay * 8)
      end
    end
  end

  def self.alert(type, message, title: nil, style: 3, color: nil, border_color: nil, title_color: nil, pause: true)
    type_sym = type.to_sym rescue :info
    tag, def_col, def_title = case type_sym
                              when :success, :ok
                                ["[✔ EXITO]", "green", "Operacion Exitosa"]
                              when :error, :fail, :danger
                                ["[✖ ERROR]", "red", "Error en el Sistema"]
                              when :warning, :warn
                                ["[⚠ AVISO]", "yellow", "Advertencia"]
                              else
                                ["[ℹ INFO]", "cyan", "Informacion"]
                              end
    card_col = border_color || color || def_col
    card_title = title || "#{tag} #{def_title}"
    card(title: card_title, content: message, style: style, color: card_col, title_color: title_color, pause: pause)
  end

  def self.card(title: nil, content: "", style: nil, color: nil, border_color: nil, title_color: nil, content_color: nil, width: nil, pause: true)
    c_sec = (@@global_theme.is_a?(Hash) && @@global_theme.dig(:sections, "card")) || {}
    style_num = (style || c_sec["style"] || 7).to_i
    border_cfg = BORDERS[style_num] || BORDERS[7]
    card_color = (border_color || color || c_sec["border_color"] || c_sec["color"] || "cyan").to_s
    title_color = (title_color || c_sec["title_color"] || "yellow").to_s
    content_color = (content_color || c_sec["content_color"] || "white").to_s
    is_rgb = card_color.downcase == "rgb" || card_color.downcase == "rainbow" || card_color.downcase == "chroma"

    lines = content.to_s.split("\n")
    content_max = lines.map { |l| display_width(l) }.max || 0
    box_w = width || [content_max + 6, title ? display_width(title) + 6 : 0, 46].max
    box_w = [box_w, terminal_width - 2].min
    inner_w = box_w - 2

    wrapped_lines = []
    lines.each do |raw_l|
      if display_width(raw_l) <= (inner_w - 2)
        wrapped_lines << raw_l
      else
        cur = String.new("")
        raw_l.split(" ").each do |w|
          if cur.empty?
            cur << w
          elsif display_width("#{cur} #{w}") <= (inner_w - 2)
            cur << " " << w
          else
            wrapped_lines << cur
            cur = String.new(w)
          end
        end
        wrapped_lines << cur unless cur.empty?
      end
    end

    tl = border_cfg[:tl] || "#"
    tr = border_cfg[:tr] || "#"
    bl = border_cfg[:bl] || "#"
    br = border_cfg[:br] || "#"
    h_char = border_cfg[:h] || "─"
    v_char = border_cfg[:v] || "│"

    brd_col = is_rgb ? Color.rgb("").sub(/\e\[0m$/, '') : ansi_color(card_color, 1)
    rst = ansi_reset

    top_str = if title && !title.empty?
                t_clean = " #{title} "
                t_len = display_width(t_clean)
                if t_len > inner_w
                  t_clean = " #{title[0...[inner_w - 6, 1].max]}... "
                  t_len = display_width(t_clean)
                end
                l_len = [(inner_w - t_len) / 2, 0].max
                r_len = [inner_w - t_len - l_len, 0].max
                h_char * l_len + ansi_color(title_color, 2) + t_clean + brd_col + h_char * r_len
              else
                h_char * inner_w
              end

    out = +""
    out << "#{brd_col}#{tl}#{top_str}#{tr}#{rst}\r\n"
    wrapped_lines.each do |line|
      pad_line = " " + line
      out << "#{brd_col}#{v_char}#{rst}#{ansi_color(content_color, 1)}#{pad_to_width(pad_line, inner_w)}#{rst}#{brd_col}#{v_char}#{rst}\r\n"
    end
    out << "#{brd_col}#{bl}#{h_char * inner_w}#{br}#{rst}\r\n"

    Kernel.print(out)
    self.continue if pause
  end

  def self.table(headers: [], rows: [], title: nil, style: nil, color: nil, page_size: nil, search: false, sort: false, animate: nil, width: nil)
    t_sec = (@@global_theme.is_a?(Hash) && @@global_theme.dig(:sections, "table")) || {}
    input_stream = STDIN
    output_stream = STDOUT
    style_num = (style || t_sec["style"] || 3).to_i
    border_cfg = BORDERS[style_num] || BORDERS[3]
    tbl_color = (color || t_sec["border_color"] || t_sec["border"] || t_sec["color"] || "cyan").to_s
    header_color = t_sec["header_color"] || "yellow"
    focus_color = t_sec["selected_row"] || t_sec["focus"] || "green"
    page_size ||= (t_sec["page_size"] || 8).to_i

    headers = headers.map(&:to_s)
    raw_rows = rows.map { |r| r.is_a?(Array) ? r.map(&:to_s) : r.values.map(&:to_s) }
    filtered_rows = raw_rows.dup
    selected_idx = 0
    query = String.new("")
    sort_col = nil
    sort_asc = true
    tick = 0.0

    calc_widths = lambda do
      col_counts = [headers.length, raw_rows.map(&:length).max || 0].max
      widths = Array.new(col_counts, 0)
      headers.each_with_index { |h, i| widths[i] = [widths[i], display_width(h)].max }
      filtered_rows.each do |row|
        row.each_with_index { |cell, i| widths[i] = [widths[i], display_width(cell)].max }
      end
      widths.map { |w| w + 2 }
    end

    draw_table = lambda do |t_tick|
      is_rgb = tbl_color.downcase == "rgb" || tbl_color.downcase == "rainbow" || tbl_color.downcase == "chroma"
      brd_color = is_rgb ? rgb_color(t_tick, 0.0) : ansi_color(tbl_color, 1)
      hdr_color = is_rgb ? rgb_color(t_tick, 0.8) : ansi_color(header_color, 2)
      foc_color = is_rgb ? rgb_color(t_tick, 1.4) : ansi_color(focus_color, 2)
      rst = ansi_reset

      col_w = calc_widths.call
      help_line = " ↑/↓: Moverse | Enter: Elegir | s: Ordenar | Esc: Salir"
      tot_w = [col_w.sum + (col_w.length - 1) + 4, title ? display_width(title) + 8 : 0, display_width(help_line) + 4, 46].max
      tot_w = [tot_w, terminal_width - 2].min
      inner_w = tot_w - 2

      if inner_w < display_width(help_line)
        help_line = " ↑/↓: Mover | Enter: Ok | Esc: Salir"
      end

      tl = border_cfg[:tl] || "#"
      tr = border_cfg[:tr] || "#"
      bl = border_cfg[:bl] || "#"
      br = border_cfg[:br] || "#"
      h_char = border_cfg[:h] || "─"
      v_char = border_cfg[:v] || "│"

      top_str = if title && !title.empty?
                  t_clean = " #{title} "
                  t_len = display_width(t_clean)
                  if t_len > inner_w
                    t_clean = " #{title[0...[(inner_w - 6), 1].max]}... "
                    t_len = display_width(t_clean)
                  end
                  left_len = [(inner_w - t_len) / 2, 0].max
                  right_len = [inner_w - t_len - left_len, 0].max
                  h_char * left_len + t_clean + h_char * right_len
                else
                  h_char * inner_w
                end

      out = String.new(CURSOR_HOME)
      out << HIDE_CURSOR
      out << "#{brd_color}#{tl}#{top_str}#{tr}#{rst}#{CLEAR_TO_EOL}\r\n"

      if search
        s_line = " Buscar: #{query}█"
        out << "#{brd_color}#{v_char}#{rst}#{pad_to_width(s_line, inner_w)}#{brd_color}#{v_char}#{rst}#{CLEAR_TO_EOL}\r\n"
        out << "#{brd_color}#{v_char}#{h_char * inner_w}#{v_char}#{rst}#{CLEAR_TO_EOL}\r\n"
      end

      hdr_cells = headers.each_with_index.map do |h, i|
        w = col_w[i] || 10
        sort_indicator = sort_col == i ? (sort_asc ? " ▲" : " ▼") : ""
        h_str = "#{h}#{sort_indicator}"
        max_c = [w - 2, 2].max
        h_str = h_str[0...[max_c - 2, 1].max] + ".." if display_width(h_str) > max_c
        pad_to_width(" #{h_str}", w)
      end
      hdr_row_str = " " + hdr_cells.join("│")
      hdr_row_str = hdr_row_str[0...inner_w] if display_width(hdr_row_str) > inner_w
      out << "#{brd_color}#{v_char}#{rst}#{hdr_color}#{pad_to_width(hdr_row_str, inner_w)}#{rst}#{brd_color}#{v_char}#{rst}#{CLEAR_TO_EOL}\r\n"
      out << "#{brd_color}#{v_char}#{h_char * inner_w}#{v_char}#{rst}#{CLEAR_TO_EOL}\r\n"

      max_visible = page_size || 8
      total_rows = filtered_rows.length
      if total_rows == 0
        empty_msg = " (Sin registros que coincidan con '#{query}')"
        out << "#{brd_color}#{v_char}#{rst}#{pad_to_width(empty_msg, inner_w)}#{brd_color}#{v_char}#{rst}#{CLEAR_TO_EOL}\r\n"
      else
        start_idx = [(selected_idx - max_visible / 2), 0].max
        start_idx = [start_idx, [total_rows - max_visible, 0].max].min
        end_idx = [start_idx + max_visible - 1, total_rows - 1].min

        if start_idx > 0
          up_str = " ▲ (+#{start_idx} arriba)"
          out << "#{brd_color}#{v_char}#{rst}#{ansi_color('gray', 1)}#{pad_to_width(up_str, inner_w)}#{rst}#{brd_color}#{v_char}#{rst}#{CLEAR_TO_EOL}\r\n"
        end

        (start_idx..end_idx).each do |r_i|
          row = filtered_rows[r_i]
          is_active = (r_i == selected_idx)
          prefix = is_active ? "> " : "  "

          row_cells = row.each_with_index.map do |cell, c_i|
            w = col_w[c_i] || 10
            c_str = cell.to_s
            max_c = [w - 2, 2].max
            c_str = c_str[0...[max_c - 2, 1].max] + ".." if display_width(c_str) > max_c
            pad_to_width(" #{c_str}", w)
          end
          row_str = prefix + row_cells.join("│")[1..-1].to_s
          row_str = row_str[0...inner_w] if display_width(row_str) > inner_w

          if is_active
            out << "#{brd_color}#{v_char}#{rst}#{foc_color}#{pad_to_width(row_str, inner_w)}#{rst}#{brd_color}#{v_char}#{rst}#{CLEAR_TO_EOL}\r\n"
          else
            out << "#{brd_color}#{v_char}#{rst}#{pad_to_width(row_str, inner_w)}#{brd_color}#{v_char}#{rst}#{CLEAR_TO_EOL}\r\n"
          end
        end

        remaining_down = total_rows - 1 - end_idx
        if remaining_down > 0
          down_str = " ▼ (+#{remaining_down} abajo)"
          out << "#{brd_color}#{v_char}#{rst}#{ansi_color('gray', 1)}#{pad_to_width(down_str, inner_w)}#{rst}#{brd_color}#{v_char}#{rst}#{CLEAR_TO_EOL}\r\n"
        end
      end

      out << "#{brd_color}#{v_char}#{h_char * inner_w}#{v_char}#{rst}#{CLEAR_TO_EOL}\r\n"
      out << "#{brd_color}#{v_char}#{rst}#{ansi_color('gray', 1)}#{pad_to_width(help_line, inner_w)}#{rst}#{brd_color}#{v_char}#{rst}#{CLEAR_TO_EOL}\r\n"
      out << "#{brd_color}#{bl}#{h_char * inner_w}#{br}#{rst}#{CLEAR_TO_EOL}\r\n"
      out << CLEAR_TO_EOS
      output_stream.print(out)
      output_stream.flush
    end

    loop_res = nil
    reader = lambda do |stream|
      loop do
        draw_table.call(tick)
        is_anim = color.to_s.downcase == "rgb" || color.to_s.downcase == "rainbow" || color.to_s.downcase == "chroma"
        if is_anim
          ready = false
          if stream.respond_to?(:to_io) || stream.is_a?(IO)
            begin
              res = IO.select([stream], nil, nil, 0.035)
              ready = true if res && res[0] && !res[0].empty?
            rescue StandardError
              ready = true
            end
          else
            ready = true
          end
          unless ready
            tick += 0.08
            next
          end
        end

        key = read_key_raw(stream)
        break if key.nil? || key == "\x03" || key == "\x04"

        if key == "\e[A" || key == "\eOA" || key == "\xe0H" || key == "\x00H"
          if filtered_rows.length > 0
            selected_idx = (selected_idx - 1) % filtered_rows.length
          end
        elsif key == "\e[B" || key == "\eOB" || key == "\xe0P" || key == "\x00P"
          if filtered_rows.length > 0
            selected_idx = (selected_idx + 1) % filtered_rows.length
          end
        elsif key == "\e[5~" || key == "\e[D"
          if filtered_rows.length > 0
            selected_idx = [(selected_idx - (page_size || 8)), 0].max
          end
        elsif key == "\e[6~" || key == "\e[C"
          if filtered_rows.length > 0
            selected_idx = [(selected_idx + (page_size || 8)), filtered_rows.length - 1].min
          end
        elsif key == "\r" || key == "\n"
          if filtered_rows.length > 0
            loop_res = filtered_rows[selected_idx]
          end
          break
        elsif key == "\e"
          if search && !query.empty?
            query.clear
            filtered_rows = raw_rows.dup
            selected_idx = 0
          else
            loop_res = nil
            break
          end
        elsif key == "\x7f" || key == "\b" || key == "\x08"
          if search && !query.empty?
            query.chop!
            if query.empty?
              filtered_rows = raw_rows.dup
            else
              filtered_rows = raw_rows.select { |r| r.any? { |c| c.downcase.include?(query.downcase) } }
            end
            selected_idx = 0
          end
        elsif key == "\x15"
          if search
            query.clear
            filtered_rows = raw_rows.dup
            selected_idx = 0
          end
        elsif (!search || query.empty?) && (key == "s" || key == "S")
          if sort
            sort_col = ((sort_col || -1) + 1) % [headers.length, 1].max
            filtered_rows.sort_by! { |r| r[sort_col] || "" }
            selected_idx = 0
          end
        elsif (!search || query.empty?) && (key == "q" || key == "Q")
          loop_res = nil
          break
        elsif search && key =~ /^[[:print:]]$/
          query << key
          filtered_rows = raw_rows.select { |r| r.any? { |c| c.downcase.include?(query.downcase) } }
          selected_idx = 0
        end
      end
    end

    begin
      output_stream.print("#{HIDE_CURSOR}#{CLEAR_SCREEN_SEQUENCE}")
      if input_stream.respond_to?(:raw) && input_stream.respond_to?(:tty?) && input_stream.tty?
        input_stream.raw { |s| reader.call(s) }
      else
        reader.call(input_stream)
      end
    ensure
      output_stream.print("#{SHOW_CURSOR}#{CLEAR_SCREEN_SEQUENCE}")
    end
    loop_res
  end

  def self.div(long = nil, color = "blue", level = 1, char = "─")
    width = long || [terminal_width - 2, 64].min
    if color.to_s.downcase == "rgb" || color.to_s.downcase == "rainbow" || color.to_s.downcase == "chroma"
      Kernel.print("#{Color.rgb(char * width)}\r\n")
    else
      color_code = ansi_color(color, level)
      reset_code = ansi_reset
      Kernel.print("#{color_code}#{char * width}#{reset_code}\r\n")
    end
  end

  def self.help(section = :all)
    path = find_data_file("help.txt")
    return unless path && File.exist?(path)
    content = File.read(path)
    COLORS.each do |c_name, lvls|
      if lvls.is_a?(Hash)
        content.gsub!("{#{c_name}}", ansi_color(c_name, 1))
        content.gsub!("{bright_#{c_name}}", ansi_color(c_name, 2))
      end
    end
    content.gsub!("{reset}", ansi_reset)
    Kernel.print("\r\n#{content}\r\n")
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

      max_len = lines.map { |l| display_width(l) }.max
      return lines if (max_len + 6) <= max_cols
    end

    nil
  end

  def self.banner(text, delay = 0, color: "magenta", level: 2, style: 3, font: 1)
    cols = terminal_width
    is_rgb = (color.to_s.downcase == "rgb" || color.to_s.downcase == "rainbow" || color.to_s.downcase == "chroma")
    color_code = is_rgb ? "" : ansi_color(color, level)
    reset_code = ansi_reset

    ascii_rows = build_ascii_lines(text, cols, font)
    border_cfg = BORDERS[style] || BORDERS[3]
    h_top = border_cfg[:ht] || border_cfg[:h]
    h_bot = border_cfg[:hb] || border_cfg[:h]
    v_l = border_cfg[:vl] || border_cfg[:v]
    v_r = border_cfg[:vr] || border_cfg[:v]

    if ascii_rows
      max_len = ascii_rows.map { |r| display_width(r) }.max
      top_fill = (h_top * ((max_len + 4).to_f / h_top.length).ceil)[0...(max_len + 4)]
      bot_fill = (h_bot * ((max_len + 4).to_f / h_bot.length).ceil)[0...(max_len + 4)]

      if is_rgb
        Kernel.print("#{Color.rgb("#{border_cfg[:tl]}#{top_fill}#{border_cfg[:tr]}")}\r\n")
        ascii_rows.each_with_index do |line, idx|
          pad = " " * (max_len - display_width(line))
          row_content = "  #{line}#{pad}  "
          Kernel.print("#{Color.rgb(v_l)}#{Color.rgb(row_content, idx * 0.2)}#{Color.rgb(v_r)}\r\n")
          sleep(delay) if delay > 0
        end
        Kernel.print("#{Color.rgb("#{border_cfg[:bl]}#{bot_fill}#{border_cfg[:br]}")}\r\n")
      else
        Kernel.print("#{color_code}#{border_cfg[:tl]}#{top_fill}#{border_cfg[:tr]}#{reset_code}\r\n")
        ascii_rows.each do |line|
          pad = " " * (max_len - display_width(line))
          Kernel.print("#{color_code}#{v_l}  #{line}#{pad}  #{v_r}#{reset_code}\r\n")
          sleep(delay) if delay > 0
        end
        Kernel.print("#{color_code}#{border_cfg[:bl]}#{bot_fill}#{border_cfg[:br]}#{reset_code}\r\n")
      end
    else
      clean_t = text.to_s.strip
      box_w = [display_width(clean_t) + 6, cols - 2].min
      top_fill = (h_top * ((box_w - 2).to_f / h_top.length).ceil)[0...(box_w - 2)]
      bot_fill = (h_bot * ((box_w - 2).to_f / h_bot.length).ceil)[0...(box_w - 2)]

      pad_t = [box_w - 4 - display_width(clean_t), 0].max
      l_p = " " * (pad_t / 2)
      r_p = " " * (pad_t - (pad_t / 2))

      if is_rgb
        Kernel.print("#{Color.rgb("#{border_cfg[:tl]}#{top_fill}#{border_cfg[:tr]}")}\r\n")
        Kernel.print("#{Color.rgb(v_l)} #{Color.rgb(l_p + clean_t + r_p)} #{Color.rgb(v_r)}\r\n")
        Kernel.print("#{Color.rgb("#{border_cfg[:bl]}#{bot_fill}#{border_cfg[:br]}")}\r\n")
      else
        Kernel.print("#{color_code}#{border_cfg[:tl]}#{top_fill}#{border_cfg[:tr]}#{reset_code}\r\n")
        Kernel.print("#{color_code}#{v_l} #{l_p}#{clean_t}#{r_p} #{v_r}#{reset_code}\r\n")
        Kernel.print("#{color_code}#{border_cfg[:bl]}#{bot_fill}#{border_cfg[:br]}#{reset_code}\r\n")
      end
    end
  end

  class << self
    alias_method :message, :banner
    alias_method :logo, :banner
  end

  def initialize(functions, *positional_arguments, title: nil, banner: nil, subtitle: nil, description: nil, divider: nil, style: nil, banner_style: nil, center: true, font: nil, page_size: nil, search: false, columns: 1, image: nil, image_width: nil, **keyword_arguments)
    @functions = functions.is_a?(Array) ? functions : Array(functions)

    pos_title = positional_arguments[0]
    pos_style = positional_arguments[1]

    @title        = (title || pos_title || keyword_arguments[:title] || "").to_s
    @banner       = (banner || keyword_arguments[:banner] || "").to_s
    @subtitle     = (subtitle || description || keyword_arguments[:subtitle] || keyword_arguments[:description] || "").to_s
    @divider      = divider.nil? ? (!@banner.empty? || !@subtitle.empty?) : divider

    theme_menu_sec = (@@global_theme.is_a?(Hash) && @@global_theme.dig(:sections, 'menu')) || {}
    th_style       = theme_menu_sec['style']&.to_i
    th_bstyle      = theme_menu_sec['banner_style']&.to_i

    @style        = (style || pos_style || keyword_arguments[:style] || th_style || 19).to_i
    @banner_style = (banner_style || keyword_arguments[:banner_style] || th_bstyle || 3).to_i
    @center       = center.nil? ? (theme_menu_sec.key?('center') ? (theme_menu_sec['center'].to_s != 'false') : true) : center
    @page_size    = (page_size || keyword_arguments[:page_size])&.to_i
    @search       = search || keyword_arguments[:search] || false
    @columns      = [(columns || keyword_arguments[:columns] || 1).to_i, 1].max
    @image        = image || keyword_arguments[:image]
    @image_width  = (image_width || keyword_arguments[:image_width])&.to_i
    @animate      = (keyword_arguments[:animate] || (@@global_theme.is_a?(Hash) && @@global_theme.dig(:sections, 'menu', 'animate')) || false).to_s
    @desc_prefix  = keyword_arguments[:desc_prefix] || keyword_arguments[:description_prefix]
    @query        = String.new("")
    @index        = 0
    @rgb_tick     = 0.0

    @cached_image_lines = nil
    @cached_image_cols  = nil

    init_font = font || keyword_arguments[:font_style] || SetStyle.font || 1
    init_pfx  = @desc_prefix || (@@global_theme.is_a?(Hash) && (@@global_theme.dig(:sections, 'menu', 'desc_prefix') || @@global_theme.dig(:sections, 'menu', 'prefix'))) || SetStyle.desc_prefix || "[i]"

    @style_config = SetStyle.new(
      border:   SetStyle.border.dup,
      options:  SetStyle.options.dup,
      focus:    SetStyle.focus.dup,
      title:    SetStyle.title.dup,
      banner:   SetStyle.banner.dup,
      subtitle: SetStyle.subtitle.dup,
      divider:  SetStyle.divider.dup,
      font:     init_font,
      desc_prefix: init_pfx
    )
  end

  def current_matching_indices
    if @search && !@query.empty?
      indices = []
      @functions.each_with_index do |func, idx|
        name = extract_name_from_action(func)
        indices << idx if name.downcase.include?(@query.downcase)
      end
      indices
    else
      (0...@functions.length).to_a
    end
  end

  def move_up
    matching = current_matching_indices
    return @index if matching.empty?
    cols = @columns
    pos = matching.index(@index) || 0
    if cols <= 1
      new_pos = (pos - 1) % matching.length
    else
      new_pos = pos - cols
      if new_pos < 0
        new_pos = pos
        while (new_pos + cols) < matching.length
          new_pos += cols
        end
      end
    end
    @index = matching[new_pos]
  end
  alias_method :_up, :move_up

  def move_down
    matching = current_matching_indices
    return @index if matching.empty?
    cols = @columns
    pos = matching.index(@index) || 0
    if cols <= 1
      new_pos = (pos + 1) % matching.length
    else
      new_pos = pos + cols
      if new_pos >= matching.length
        new_pos = pos % cols
      end
    end
    @index = matching[new_pos]
  end
  alias_method :_down, :move_down

  def move_left
    matching = current_matching_indices
    return @index if matching.empty?
    cols = @columns
    pos = matching.index(@index) || 0
    if cols <= 1
      new_pos = (pos - 1) % matching.length
    else
      if (pos % cols) == 0
        new_pos = [pos + (cols - 1), matching.length - 1].min
      else
        new_pos = pos - 1
      end
    end
    @index = matching[new_pos]
  end

  def move_right
    matching = current_matching_indices
    return @index if matching.empty?
    cols = @columns
    pos = matching.index(@index) || 0
    if cols <= 1
      new_pos = (pos + 1) % matching.length
    else
      if (pos % cols) == (cols - 1) || pos == (matching.length - 1)
        new_pos = pos - (pos % cols)
      else
        new_pos = pos + 1
      end
    end
    @index = matching[new_pos]
  end

  def colorize(text, color_config, phase_offset = 0.0)
    return text.to_s if color_config.nil? || color_config.empty?

    color_name = (color_config[:color] || color_config["color"]).to_s.downcase.strip
    brightness_level = (color_config[:level] || color_config["level"] || 1).to_i

    if color_name.include?(":")
      parts = color_name.split(":")
      color_name = parts[0].strip
      brightness_level = parts[1].to_i if parts[1] && !parts[1].empty?
    end

    is_neon_color = color_name.start_with?("neon")
    is_anim_active = is_neon_color || (@animate && ["diagonal", "linear", "fade", "rgb", "rainbow", "chroma", "neon"].include?(@animate.to_s.downcase))
    is_chroma = color_name == "rgb" || color_name == "rainbow" || color_name == "chroma" || @animate.to_s.downcase == "rgb"

    if is_chroma
      tick = @rgb_tick || 0.0
      out = String.new("")
      char_count = 0
      in_escape = false
      escape_buf = String.new("")

      text.to_s.each_char do |ch|
        if ch == "\e"
          in_escape = true
          escape_buf << ch
          next
        end
        if in_escape
          escape_buf << ch
          if ch =~ /[a-zA-Z]/
            in_escape = false
            out << escape_buf
            escape_buf.clear
          end
          next
        end

        if ch == " " || ch == "\t" || ch == "\r" || ch == "\n"
          out << ch
        else
          c_code = self.class.rgb_color(tick, char_count * 0.12 + phase_offset)
          out << "#{c_code}#{ch}"
          char_count += 1
        end
      end
      out << self.class.ansi_reset
      return out
    end

    if is_anim_active
      tick = @rgb_tick || 0.0
      base = if color_name =~ /\A#?([0-9a-f]{6})\z/i
               h = $1
               [h[0..1].to_i(16), h[2..3].to_i(16), h[4..5].to_i(16)]
             elsif color_name =~ /\A#?([0-9a-f]{3})\z/i
               h = $1
               [(h[0] * 2).to_i(16), (h[1] * 2).to_i(16), (h[2] * 2).to_i(16)]
             else
               BASE_RGB[color_name] || [255, 255, 255]
             end

      if @animate.to_s.downcase == "fade"
        factor = (Math.sin(tick + phase_offset) + 1.0) / 2.0
        f = 0.35 + 0.65 * factor
        r = (base[0] * f).clamp(0, 255).to_i
        g = (base[1] * f).clamp(0, 255).to_i
        b = (base[2] * f).clamp(0, 255).to_i
        glow = (factor > 0.85) ? ";1" : ""
        return "\e[38;2;#{r};#{g};#{b}#{glow}m#{text}#{self.class.ansi_reset}"
      else
        out = String.new("")
        char_count = 0
        in_escape = false
        escape_buf = String.new("")

        text.to_s.each_char do |ch|
          if ch == "\e"
            in_escape = true
            escape_buf << ch
            next
          end
          if in_escape
            escape_buf << ch
            if ch =~ /[a-zA-Z]/
              in_escape = false
              out << escape_buf
              escape_buf.clear
            end
            next
          end

          if ch == " " || ch == "\t" || ch == "\r" || ch == "\n"
            out << ch
          else
            phase = char_count * 0.22 + phase_offset
            factor = (Math.sin(tick + phase) + 1.0) / 2.0
            f = 0.35 + 0.65 * factor
            r = (base[0] * f).clamp(0, 255).to_i
            g = (base[1] * f).clamp(0, 255).to_i
            b = (base[2] * f).clamp(0, 255).to_i
            glow = (factor > 0.85) ? ";1" : ""
            out << "\e[38;2;#{r};#{g};#{b}#{glow}m#{ch}"
            char_count += 1
          end
        end
        out << self.class.ansi_reset
        return out
      end
    end

    color_code = self.class.ansi_color(color_name, brightness_level)
    return text.to_s unless color_code

    "#{color_code}#{text}#{self.class.ansi_reset}"
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

    h_top = banner_border[:ht] || banner_border[:h]
    h_bot = banner_border[:hb] || banner_border[:h]
    v_l = banner_border[:vl] || banner_border[:v]
    v_r = banner_border[:vr] || banner_border[:v]

    lines = []
    box_w = 0
    if ascii_rows
      content_w = ascii_rows.map { |r| GRmenu.display_width(r) }.max
      box_w = content_w + 6
      top_fill = build_horizontal_line(h_top, content_w + 4)
      bot_fill = build_horizontal_line(h_bot, content_w + 4)
      
      lines << colorize("#{banner_border[:tl]}#{top_fill}#{banner_border[:tr]}", banner_color_cfg, 0.0)
      ascii_rows.each_with_index do |row, r_i|
        pad = " " * (content_w - GRmenu.display_width(row))
        lines << colorize("#{v_l}  #{row}#{pad}  #{v_r}", banner_color_cfg, r_i * 0.2)
      end
      lines << colorize("#{banner_border[:bl]}#{bot_fill}#{banner_border[:br]}", banner_color_cfg, 1.2)
    else
      clean_b = @banner.strip
      b_vis_w = GRmenu.display_width(clean_b)
      box_w = [b_vis_w + 6, term_cols - 2].min
      top_fill = build_horizontal_line(h_top, box_w - 2)
      bot_fill = build_horizontal_line(h_bot, box_w - 2)
      
      pad_b = [box_w - 4 - b_vis_w, 0].max
      l_p = " " * (pad_b / 2)
      r_p = " " * (pad_b - (pad_b / 2))

      lines << colorize("#{banner_border[:tl]}#{top_fill}#{banner_border[:tr]}", banner_color_cfg, 0.0)
      lines << colorize("#{v_l} #{l_p}#{clean_b}#{r_p} #{v_r}", banner_color_cfg, 0.4)
      lines << colorize("#{banner_border[:bl]}#{bot_fill}#{banner_border[:br]}", banner_color_cfg, 0.8)
    end
    [lines, box_w]
  end

  def render_image_lines(term_cols)
    return @cached_image_lines if @cached_image_lines && @cached_image_cols == term_cols

    return [[], 0] unless @image && File.exist?(@image)

    raw_lines = self.class.load_and_render_image(@image, @image_width || 40, nil, term_cols)
    return [[], 0] if raw_lines.empty?

    img_w = self.class.display_width(raw_lines.first)
    box_w = img_w + 4
    banner_border = BORDERS[@banner_style] || BORDERS[3]
    banner_color_cfg = @style_config.banner

    h_top = banner_border[:ht] || banner_border[:h]
    h_bot = banner_border[:hb] || banner_border[:h]
    v_l = banner_border[:vl] || banner_border[:v]
    v_r = banner_border[:vr] || banner_border[:v]

    top_fill = build_horizontal_line(h_top, img_w + 2)
    bot_fill = build_horizontal_line(h_bot, img_w + 2)

    lines = []
    lines << colorize("#{banner_border[:tl]}#{top_fill}#{banner_border[:tr]}", banner_color_cfg)
    raw_lines.each do |r_line|
      lines << "#{colorize(v_l, banner_color_cfg)} #{r_line} #{colorize(v_r, banner_color_cfg)}"
    end
    lines << colorize("#{banner_border[:bl]}#{bot_fill}#{banner_border[:br]}", banner_color_cfg)

    @cached_image_cols = term_cols
    @cached_image_lines = [lines, box_w]
    @cached_image_lines
  end

  def render_lines(size_max = 20)
    term_cols = self.class.terminal_width
    term_rows = self.class.terminal_height
    rendered_lines = []

    header_box_width = 0
    header_lines_count = 0

    if @image && File.exist?(@image)
      img_lines, img_box_w = render_image_lines(term_cols)
      unless img_lines.empty?
        rendered_lines.concat(img_lines)
        rendered_lines << ""
        header_lines_count += img_lines.length + 1
        header_box_width = [header_box_width, img_box_w].max
      end
    end

    if @banner && !@banner.empty?
      banner_lines, banner_box_w = render_banner_lines(term_cols)
      unless banner_lines.empty?
        rendered_lines.concat(banner_lines)
        rendered_lines << ""
        header_lines_count += banner_lines.length + 1
        header_box_width = [header_box_width, banner_box_w].max
      end
    end

    matching_indices = current_matching_indices
    all_names = @functions.map { |func| extract_name_from_action(func) }
    all_descriptions = @functions.map { |func| extract_description_from_action(func) }

    active_desc = all_descriptions[@index] || ""

    cols = @columns
    max_item_len = all_names.empty? ? 10 : all_names.map { |n| GRmenu.display_width(n) }.max
    grid_suggested_w = (max_item_len + 6) * cols + 4

    calculated_width = [size_max, GRmenu.display_width(@title) + 4, grid_suggested_w].max
    calculated_width = ([calculated_width, GRmenu.display_width(active_desc) + 8].max) unless active_desc.empty?
    calculated_width = ([calculated_width, GRmenu.display_width(@query) + 16].max) if @search
    total_width = [calculated_width, term_cols - 2].min

    reference_width = header_box_width > 0 ? header_box_width : total_width
    margin_left = (@center && reference_width > total_width) ? " " * ((reference_width - total_width) / 2) : ""

    subtitle_lines_count = 0
    if @subtitle && !@subtitle.empty?
      subtitle_lines = @subtitle.lines.map(&:chomp)
      div_w = @divider.is_a?(Numeric) ? @divider.to_i : [reference_width, term_cols - 2].min

      if @divider
        rendered_lines << colorize("─" * div_w, @style_config.divider, 0.0)
        subtitle_lines_count += 1
      end

      subtitle_lines.each_with_index do |sub_line, s_i|
        pad_sub = [div_w - GRmenu.display_width(sub_line), 0].max
        formatted_sub = @center ? (" " * (pad_sub / 2) + sub_line + " " * (pad_sub - (pad_sub / 2))) : sub_line
        rendered_lines << colorize(formatted_sub, @style_config.subtitle, s_i * 0.3)
        subtitle_lines_count += 1
      end

      if @divider
        rendered_lines << colorize("─" * div_w, @style_config.divider, 0.6)
        subtitle_lines_count += 1
      end
      rendered_lines << ""
      subtitle_lines_count += 1
    end

    border_color_cfg  = @style_config.border
    options_color_cfg = @style_config.options
    focus_color_cfg   = @style_config.focus
    title_color_cfg   = @style_config.title

    box_border = BORDERS[@style]

    overhead = header_lines_count + subtitle_lines_count + 6
    overhead += 2 unless active_desc.empty?
    overhead += 2 if @search
    available_rows = [term_rows - overhead - 2, 2].max

    rows_data = matching_indices.each_slice(cols).to_a
    total_rows = rows_data.length

    effective_page_rows = if @page_size && @page_size > 0
                            [@page_size, total_rows, available_rows].min
                          else
                            [total_rows, available_rows].min
                          end
    effective_page_rows = [effective_page_rows, 1].max

    curr_matching_pos = matching_indices.index(@index) || 0
    curr_row = total_rows > 0 ? (curr_matching_pos / cols) : 0

    start_row = 0
    end_row = [total_rows - 1, 0].max
    if total_rows > effective_page_rows
      half_r = effective_page_rows / 2
      start_row = [[curr_row - half_r, 0].max, total_rows - effective_page_rows].min
      end_row = start_row + effective_page_rows - 1
    end

    visible_rows_data = rows_data[start_row..end_row] || []
    has_more_above = start_row > 0
    has_more_below = end_row < (total_rows - 1)

    avail_w = [total_width - 4, 1].max
    col_w = [(avail_w - (cols - 1) * 2) / cols, 1].max

    if box_border
      h_top = box_border[:ht] || box_border[:h]
      h_bot = box_border[:hb] || box_border[:h]
      v_l_raw = box_border[:vl] || box_border[:v]
      v_r_raw = box_border[:vr] || box_border[:v]

      top_fill = build_horizontal_line(h_top, total_width - 2)
      bot_fill = build_horizontal_line(h_bot, total_width - 2)
      mid_fill = build_horizontal_line(h_top, total_width - 2)

      v_left  = colorize(v_l_raw, border_color_cfg, 0.2)
      v_right = colorize(v_r_raw, border_color_cfg, 0.8)

      top_border_line = box_border[:tl] + top_fill + box_border[:tr]
      rendered_lines << "#{margin_left}#{colorize(top_border_line, border_color_cfg, 0.0)}"

      unless @title.empty?
        pad_t = [total_width - 4 - GRmenu.display_width(@title), 0].max
        title_padded = " " * (pad_t / 2) + @title + " " * (pad_t - (pad_t / 2))
        centered_title = colorize(title_padded, title_color_cfg, 0.4)
        rendered_lines << "#{margin_left}#{v_left} #{centered_title} #{v_right}"

        separator_line = v_l_raw + mid_fill + v_r_raw
        rendered_lines << "#{margin_left}#{colorize(separator_line, border_color_cfg, 0.6)}"
      end

      if @search
        search_prompt = "Buscar: #{@query}█"
        pad_s = [avail_w - GRmenu.display_width(search_prompt), 0].max
        search_padded = search_prompt + (" " * pad_s)
        rendered_lines << "#{margin_left}#{v_left} #{Color.bright_yellow(search_padded)} #{v_right}"
        separator_line = v_l_raw + mid_fill + v_r_raw
        rendered_lines << "#{margin_left}#{colorize(separator_line, border_color_cfg, 0.8)}"
      end

      if has_more_above
        up_text = "▲ (+#{start_row} #{cols > 1 ? 'filas' : 'arriba'})"
        pad_up = [avail_w - GRmenu.display_width(up_text), 0].max
        up_indicator = colorize(" " * (pad_up / 2) + up_text + " " * (pad_up - (pad_up / 2)), { color: "gray", level: 2 })
        rendered_lines << "#{margin_left}#{v_left} #{up_indicator} #{v_right}"
      end

      if rows_data.empty?
        no_res_txt = "(Sin resultados)"
        pad_no = [avail_w - GRmenu.display_width(no_res_txt), 0].max
        no_res = colorize(" " * (pad_no / 2) + no_res_txt + " " * (pad_no - (pad_no / 2)), { color: "gray", level: 1 })
        rendered_lines << "#{margin_left}#{v_left} #{no_res} #{v_right}"
      else
        visible_rows_data.each_with_index do |row_indices, r_idx|
          cells = []
          cols.times do |c_idx|
            item_idx = row_indices[c_idx]
            if item_idx
              op_name = all_names[item_idx]
              if @index == item_idx
                cell_raw = "> #{op_name}"
                pad_c = [col_w - GRmenu.display_width(cell_raw), 0].max
                cells << colorize(cell_raw + (" " * pad_c), focus_color_cfg, r_idx * 0.3)
              else
                cell_raw = "  #{op_name}"
                pad_c = [col_w - GRmenu.display_width(cell_raw), 0].max
                cells << colorize(cell_raw + (" " * pad_c), options_color_cfg, r_idx * 0.2)
              end
            else
              cells << (" " * col_w)
            end
          end
          row_str = cells.join("  ")
          pad_r = [avail_w - (col_w * cols + (cols - 1) * 2), 0].max
          row_padded = row_str + (" " * pad_r)
          rendered_lines << "#{margin_left}#{v_left} #{row_padded} #{v_right}"
        end
      end

      if has_more_below
        remaining_below = total_rows - 1 - end_row
        down_text = "▼ (+#{remaining_below} #{cols > 1 ? 'filas' : 'abajo'})"
        pad_down = [avail_w - GRmenu.display_width(down_text), 0].max
        down_indicator = colorize(" " * (pad_down / 2) + down_text + " " * (pad_down - (pad_down / 2)), { color: "gray", level: 2 })
        rendered_lines << "#{margin_left}#{v_left} #{down_indicator} #{v_right}"
      end

      unless active_desc.empty?
        separator_line = v_l_raw + mid_fill + v_r_raw
        rendered_lines << "#{margin_left}#{colorize(separator_line, border_color_cfg, 1.0)}"
        pfx = (@style_config&.desc_prefix || @desc_prefix || SetStyle.desc_prefix || "[i]").to_s
        pfx = "#{pfx} " unless pfx.end_with?(" ")
        raw_desc = "#{pfx}#{active_desc}"
        pad_d = [avail_w - GRmenu.display_width(raw_desc), 0].max
        desc_text = colorize(raw_desc + (" " * pad_d), { color: "cyan", level: 1 })
        rendered_lines << "#{margin_left}#{v_left} #{desc_text} #{v_right}"
      end

      bottom_border_line = box_border[:bl] + bot_fill + box_border[:br]
      rendered_lines << "#{margin_left}#{colorize(bottom_border_line, border_color_cfg, 1.4)}"
    else
      symbol_char  = STYLES[@style] || "#"
      solid_border = colorize(symbol_char, border_color_cfg)
      solid_line   = symbol_char * total_width

      rendered_lines << "#{margin_left}#{colorize(solid_line, border_color_cfg)}"

      unless @title.empty?
        pad_t = [total_width - 4 - GRmenu.display_width(@title), 0].max
        title_padded = " " * (pad_t / 2) + @title + " " * (pad_t - (pad_t / 2))
        centered_title = colorize(title_padded, title_color_cfg)
        rendered_lines << "#{margin_left}#{solid_border} #{centered_title} #{solid_border}"
        rendered_lines << "#{margin_left}#{colorize(solid_line, border_color_cfg)}"
      end

      if @search
        search_prompt = "Buscar: #{@query}█"
        pad_s = [avail_w - GRmenu.display_width(search_prompt), 0].max
        search_padded = search_prompt + (" " * pad_s)
        rendered_lines << "#{margin_left}#{solid_border} #{Color.bright_yellow(search_padded)} #{solid_border}"
        rendered_lines << "#{margin_left}#{colorize(solid_line, border_color_cfg)}"
      end

      if has_more_above
        up_text = "▲ (+#{start_row} #{cols > 1 ? 'filas' : 'arriba'})"
        pad_up = [avail_w - GRmenu.display_width(up_text), 0].max
        up_indicator = colorize(" " * (pad_up / 2) + up_text + " " * (pad_up - (pad_up / 2)), { color: "gray", level: 2 })
        rendered_lines << "#{margin_left}#{solid_border} #{up_indicator} #{solid_border}"
      end

      if rows_data.empty?
        no_res_txt = "(Sin resultados)"
        pad_no = [avail_w - GRmenu.display_width(no_res_txt), 0].max
        no_res = colorize(" " * (pad_no / 2) + no_res_txt + " " * (pad_no - (pad_no / 2)), { color: "gray", level: 1 })
        rendered_lines << "#{margin_left}#{solid_border} #{no_res} #{solid_border}"
      else
        visible_rows_data.each_with_index do |row_indices, r_idx|
          cells = []
          cols.times do |c_idx|
            item_idx = row_indices[c_idx]
            if item_idx
              op_name = all_names[item_idx]
              if @index == item_idx
                cell_raw = "> #{op_name}"
                pad_c = [col_w - GRmenu.display_width(cell_raw), 0].max
                cells << colorize(cell_raw + (" " * pad_c), focus_color_cfg, r_idx * 0.3)
              else
                cell_raw = "  #{op_name}"
                pad_c = [col_w - GRmenu.display_width(cell_raw), 0].max
                cells << colorize(cell_raw + (" " * pad_c), options_color_cfg, r_idx * 0.2)
              end
            else
              cells << (" " * col_w)
            end
          end
          row_str = cells.join("  ")
          pad_r = [avail_w - (col_w * cols + (cols - 1) * 2), 0].max
          row_padded = row_str + (" " * pad_r)
          rendered_lines << "#{margin_left}#{solid_border} #{row_padded} #{solid_border}"
        end
      end

      if has_more_below
        remaining_below = total_rows - 1 - end_row
        down_text = "▼ (+#{remaining_below} #{cols > 1 ? 'filas' : 'abajo'})"
        pad_down = [avail_w - GRmenu.display_width(down_text), 0].max
        down_indicator = colorize(" " * (pad_down / 2) + down_text + " " * (pad_down - (pad_down / 2)), { color: "gray", level: 2 })
        rendered_lines << "#{margin_left}#{solid_border} #{down_indicator} #{solid_border}"
      end

      unless active_desc.empty?
        rendered_lines << "#{margin_left}#{colorize(solid_line, border_color_cfg)}"
        pfx = (@style_config&.desc_prefix || @desc_prefix || SetStyle.desc_prefix || "[i]").to_s
        pfx = "#{pfx} " unless pfx.end_with?(" ")
        raw_desc = "#{pfx}#{active_desc}"
        pad_d = [avail_w - GRmenu.display_width(raw_desc), 0].max
        desc_text = colorize(raw_desc + (" " * pad_d), { color: "cyan", level: 1 })
        rendered_lines << "#{margin_left}#{solid_border} #{desc_text} #{solid_border}"
      end

      rendered_lines << "#{margin_left}#{colorize(solid_line, border_color_cfg)}"
    end

    rendered_lines
  end

  def has_rgb_animation?
    configs = [
      @style_config.border,
      @style_config.options,
      @style_config.focus,
      @style_config.title,
      @style_config.banner,
      @style_config.subtitle,
      @style_config.divider
    ]
    configs.any? do |c|
      if c.is_a?(Hash)
        val = (c[:color] || c["color"]).to_s.downcase
        val == "rgb" || val == "rainbow" || val == "chroma"
      else
        false
      end
    end
  end

  def has_active_animation?
    return true if @animate && ["diagonal", "linear", "fade", "rgb", "rainbow", "chroma", "neon"].include?(@animate.to_s.downcase)
    return true if has_rgb_animation?
    configs = [
      @style_config.border,
      @style_config.options,
      @style_config.focus,
      @style_config.title,
      @style_config.banner,
      @style_config.subtitle,
      @style_config.divider
    ]
    configs.any? do |c|
      if c.is_a?(Hash)
        val = (c[:color] || c["color"]).to_s.downcase.strip
        val.start_with?("neon")
      else
        false
      end
    end
  end

  def style(css_content)
    parsed = self.class.parse_config_text(css_content)
    m = ((parsed[:sections] && parsed[:sections]["menu"]) || {}).merge(parsed[:global] || {})
    if m["style"]
      @style = m["style"].to_i
      @border_config = BORDERS[@style] || BORDERS[3]
    end
    @banner_style = m["banner_style"].to_i if m["banner_style"]
    @animate = m["animate"].to_s if m["animate"]
    @center = (m["center"].to_s != "false") if m.key?("center")
    if m["border"] || m["border_color"]
      c, l = self.class.extract_color_and_level(m["border"] || m["border_color"], 1)
      @style_config.border(c, l)
    end
    if m["options"] || m["options_color"]
      c, l = self.class.extract_color_and_level(m["options"] || m["options_color"], 1)
      @style_config.options(c, l)
    end
    if m["focus"] || m["focus_color"]
      c, l = self.class.extract_color_and_level(m["focus"] || m["focus_color"], 2)
      @style_config.focus(c, l)
    end
    if m["title"] || m["title_color"]
      c, l = self.class.extract_color_and_level(m["title"] || m["title_color"], 2)
      @style_config.title(c, l)
    end
    if m["banner"] || m["banner_color"]
      c, l = self.class.extract_color_and_level(m["banner"] || m["banner_color"], 2)
      @style_config.banner(c, l)
    end
    if m["subtitle"] || m["subtitle_color"]
      c, l = self.class.extract_color_and_level(m["subtitle"] || m["subtitle_color"], 1)
      @style_config.subtitle(c, l)
    end
    if m["divider"] || m["divider_color"]
      c, l = self.class.extract_color_and_level(m["divider"] || m["divider_color"], 1)
      @style_config.divider(c, l)
    end
    if m["desc_prefix"] || m["description_prefix"] || m["prefix"]
      @style_config.desc_prefix(m["desc_prefix"] || m["description_prefix"] || m["prefix"])
    end
    @style_config.font(m["font"].to_i) if m["font"]
    self
  end

  def export_config(path = nil)
    if path.nil?
      caller_loc = caller_locations.find { |c| !c.path.include?(__FILE__) }
      base = caller_loc ? caller_loc.path.sub(/\.rb$/, '') : "theme"
      path = "#{base}.gr"
    end
    b_cfg = @style_config&.border || SetStyle.border
    t_cfg = @style_config&.title || SetStyle.title
    f_cfg = @style_config&.focus || SetStyle.focus
    o_cfg = @style_config&.options || SetStyle.options
    bn_cfg = @style_config&.banner || SetStyle.banner
    s_cfg = @style_config&.subtitle || SetStyle.subtitle
    d_cfg = @style_config&.divider || SetStyle.divider
    dp_val = @style_config&.desc_prefix || SetStyle.desc_prefix

    lines = ["GRmenu::config<-1->", ""]
    lines << "@theme:: \"#{File.basename(path, '.gr').capitalize}\""
    lines << "@author:: \"grcode\""
    lines << "@version:: \"1.0\""
    lines << ""
    lines << "<<menu"
    lines << "  style:: #{@style || 3}"
    lines << "  banner_style:: #{@banner_style || 3}"
    lines << "  font:: #{@style_config&.font || SetStyle.font}"
    lines << "  animate:: #{@animate || 'rgb'}"
    lines << "  center:: #{@center.nil? ? true : @center}"
    lines << "  desc_prefix:: #{dp_val}"
    lines << "  border:: #{b_cfg[:color]}:#{b_cfg[:level]}"
    lines << "  title:: #{t_cfg[:color]}:#{t_cfg[:level]}"
    lines << "  focus:: #{f_cfg[:color]}:#{f_cfg[:level]}"
    lines << "  options:: #{o_cfg[:color]}:#{o_cfg[:level]}"
    lines << "  banner:: #{bn_cfg[:color]}:#{bn_cfg[:level]}"
    lines << "  subtitle:: #{s_cfg[:color]}:#{s_cfg[:level]}"
    lines << "  divider:: #{d_cfg[:color]}:#{d_cfg[:level]}"
    lines << ">>"
    lines << ""
    lines << "<<table"
    lines << "  style:: #{@style || 3}"
    lines << "  header_color:: yellow:2"
    lines << "  border_color:: #{b_cfg[:color]}:#{b_cfg[:level]}"
    lines << "  selected_row:: #{f_cfg[:color]}:#{f_cfg[:level]}"
    lines << "  row_color:: white:1"
    lines << "  zebra_striping:: true"
    lines << ">>"
    lines << ""
    lines << "<<card"
    lines << "  style:: 7"
    lines << "  border_color:: #{b_cfg[:color]}:#{b_cfg[:level]}"
    lines << "  title_color:: #{t_cfg[:color]}:#{t_cfg[:level]}"
    lines << "  content_color:: white:1"
    lines << ">>"
    lines << ""
    lines << "<<slider"
    lines << "  style:: #{@style || 3}"
    lines << "  color:: #{b_cfg[:color]}:#{b_cfg[:level]}"
    lines << "  fill_char:: █"
    lines << "  empty_char:: ░"
    lines << ">>"
    lines << ""
    lines << "<<checkbox"
    lines << "  style:: #{@style || 3}"
    lines << "  color:: #{b_cfg[:color]}:#{b_cfg[:level]}"
    lines << "  checked_mark:: [X]"
    lines << "  unchecked_mark:: [ ]"
    lines << ">>"
    lines << ""
    File.write(path, lines.join("\n") + "\n")
    path
  end
  alias_method :export_theme, :export_config

  def draw(size_max: 20, min_width: nil)
    if ARGV.any? { |a| ["-theme", "--theme", "-ex", "--export-theme"].include?(a.to_s.downcase) }
      out_idx = ARGV.index { |a| ["-o", "--out", "--output"].include?(a.to_s.downcase) }
      target_file = out_idx ? ARGV[out_idx + 1] : "tema_exportado.gr"
      export_config(target_file)
      Kernel.puts Color.bright_green("[OK] Tema exportado exitosamente a: #{target_file}")
      exit(0)
    end

    target_width = min_width || size_max || 20
    action_to_execute = nil

    is_tty = $stdin.respond_to?(:tty?) && $stdin.tty?

    begin
      Kernel.print("#{HIDE_CURSOR}#{CLEAR_SCREEN_SEQUENCE}")

      if @animate && !["false", "rgb", "", "nil"].include?(@animate.downcase)
        intro_lines = render_lines(target_width)
        self.class.animate_render(intro_lines, @animate)
      end

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
    lines.each_with_index do |line, idx|
      buffer << line << CLEAR_TO_EOL
      buffer << "\r\n" if idx < lines.length - 1
    end
    buffer << CLEAR_TO_EOS
    Kernel.print(buffer)
  end

  def run_interactive_loop(input_stream, target_width)
    matching = current_matching_indices
    @index = matching.first || 0 unless matching.include?(@index)
    @rgb_tick = 0.0
    draw_frame(target_width)

    animating = has_active_animation?

    while true
      if animating
        ready = false
        if input_stream.respond_to?(:to_io) || input_stream.is_a?(IO)
          begin
            select_res = IO.select([input_stream], nil, nil, 0.035)
            ready = true if select_res && select_res[0] && !select_res[0].empty?
          rescue StandardError
            ready = true
          end
        else
          ready = true
        end

        unless ready
          @rgb_tick += 0.08
          draw_frame(target_width)
          next
        end
      end

      key = read_single_key(input_stream)
      break if key.nil? || key == "\x03" || key == "\x04"

      if !@search && (key == "q" || key == "Q")
        break
      end

      if key == "\e"
        if @search && !@query.empty?
          @query.clear
          matching = current_matching_indices
          @index = matching.first || 0
          draw_frame(target_width)
        else
          break
        end
      elsif key == "\e[A" || key == "\eOA" || key == "\xe0H" || key == "\x00H"
        move_up
        draw_frame(target_width)
      elsif key == "\e[B" || key == "\eOB" || key == "\xe0P" || key == "\x00P"
        move_down
        draw_frame(target_width)
      elsif key == "\e[D" || key == "\eOD" || key == "\xe0K" || key == "\x00K"
        move_left
        draw_frame(target_width)
      elsif key == "\e[C" || key == "\eOC" || key == "\xe0M" || key == "\x00M"
        move_right
        draw_frame(target_width)
      elsif key == "\x7f" || key == "\b" || key == "\x08"
        if @search && !@query.empty?
          @query.chop!
          matching = current_matching_indices
          @index = matching.first || 0
          draw_frame(target_width)
        end
      elsif key == "\x15"
        if @search
          @query.clear
          matching = current_matching_indices
          @index = matching.first || 0
          draw_frame(target_width)
        end
      elsif key == "\r" || key == "\n"
        matching = current_matching_indices
        return @functions[@index] if matching.include?(@index)
      elsif @search && key =~ /^[[:print:]]$/
        @query << key
        matching = current_matching_indices
        @index = matching.first || 0
        draw_frame(target_width)
      end
    end

    nil
  end

  def read_single_key(input_stream)
    GRmenu.read_key_raw(input_stream)
  end

  def format_auto_name(raw_name)
    cleaned = raw_name.to_s.gsub(/[_-]+/, ' ').strip
    cleaned.split(' ').map(&:capitalize).join(' ')
  end

  def extract_name_from_action(action)
    case action
    when Array
      action[0].to_s
    when Hash
      (action[:name] || action[:title] || action["name"] || action["title"] || "Opcion").to_s
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

  def extract_description_from_action(action)
    if action.is_a?(Array) && action.length >= 3
      action[2].to_s
    elsif action.is_a?(Hash)
      (action[:desc] || action[:description] || action["desc"] || action["description"]).to_s
    else
      ""
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
      if callable.is_a?(Symbol)
        if Object.respond_to?(callable, true)
          Object.send(callable)
        elsif Kernel.respond_to?(callable, true)
          Kernel.send(callable)
        end
      elsif callable.respond_to?(:call)
        callable.call
      end
    when Hash
      callable = action[:action] || action[:call] || action["action"] || action["call"]
      if callable.is_a?(Symbol)
        if Object.respond_to?(callable, true)
          Object.send(callable)
        elsif Kernel.respond_to?(callable, true)
          Kernel.send(callable)
        end
      elsif callable.respond_to?(:call)
        callable.call
      end
    else
      action.call if action.respond_to?(:call)
    end
  end
end

Color = GRmenu::Color unless defined?(Color)
Colors = GRmenu::Color unless defined?(Colors)
C = GRmenu::Color unless defined?(C)
Grmenu = GRmenu unless defined?(Grmenu)
