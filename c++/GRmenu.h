// GRmenu — menu de navegacion por teclado para terminal, en modo TTY crudo.
// Libreria header-only: no hay .cpp que compilar aparte, basta con #include "GRmenu.h".
//
// El "#pragma once" de aca abajo es el header guard: evita que este archivo
// se procese mas de una vez si llega a incluirse (directa o indirectamente)
// varias veces en la misma unidad de compilacion.
#pragma once

#include <algorithm>
#include <cstdio>
#include <functional>
#include <string>
#include <unordered_map>
#include <vector>

#include <termios.h>
#include <unistd.h>

class GRmenu {
public:
    // Una opcion del menu: el texto que se muestra y la accion a ejecutar.
    // A diferencia de Python/Ruby, en C++ no hay forma de leer el nombre de
    // una funcion en tiempo de ejecucion, asi que el nombre se pasa explicito.
    struct Option {
        std::string name;
        std::function<void()> action;
    };

    struct ColorConfig {
        std::string color;
        int level = 1;
    };

    // Equivalente a SetStyle en Python/Ruby: color de cada zona del menu.
    struct Style {
        ColorConfig border{"cyan", 1};
        ColorConfig options{"white", 1};
        ColorConfig focus{"green", 2};

        void setBorder(std::string color, int level = 1) { border = {std::move(color), level}; }
        void setOptions(std::string color, int level = 1) { options = {std::move(color), level}; }
        void setFocus(std::string color, int level = 2) { focus = {std::move(color), level}; }
    };

    GRmenu(std::vector<Option> options, std::string title = "", int style = 19)
        : options_(std::move(options)), title_(std::move(title)), style_num_(style),
          style_(defaultStyle()) {}

    // Estilo por defecto para instancias creadas *despues* de modificarlo,
    // igual que GRmenu::SetStyle a nivel de clase en la version Ruby.
    static Style& defaultStyle() {
        static Style instance;
        return instance;
    }

    Style& styleConfig() { return style_; }
    const Style& styleConfig() const { return style_; }

    // Dibuja el menu y bloquea hasta que el usuario elige una opcion (Enter)
    // o sale (q). Declarada aca, definida mas abajo con "inline" -> eso es
    // lo que permite tener la definicion en el .h sin errores de linker.
    void draw(int size_max = 20);

private:
    struct Border {
        std::string h, v, tl, tr, bl, br;
    };

    std::vector<Option> options_;
    std::string title_;
    int style_num_;
    int index_ = 0;
    Style style_;

    static constexpr const char* kClearSeq = "\x1b[H\x1b[2J\x1b[3J";
    static constexpr const char* kReset = "\x1b[0m";

    void up() {
        if (!options_.empty())
            index_ = (index_ - 1 + static_cast<int>(options_.size())) % static_cast<int>(options_.size());
    }
    void down() {
        if (!options_.empty())
            index_ = (index_ + 1) % static_cast<int>(options_.size());
    }

    // RAII: pone la terminal en modo crudo al construirse y la restaura al
    // destruirse (incluso si algo lanza una excepcion en el medio).
    struct RawModeGuard {
        termios original{};
        bool active = false;

        RawModeGuard() {
            if (::tcgetattr(STDIN_FILENO, &original) == -1) return;
            termios raw = original;
            raw.c_lflag &= ~(ECHO | ICANON | ISIG | IEXTEN);
            raw.c_iflag &= ~(BRKINT | ICRNL | INPCK | ISTRIP | IXON);
            raw.c_oflag &= ~(OPOST);
            raw.c_cflag |= CS8;
            raw.c_cc[VMIN] = 1;
            raw.c_cc[VTIME] = 0;
            if (::tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw) == -1) return;
            active = true;
        }
        ~RawModeGuard() {
            if (active) ::tcsetattr(STDIN_FILENO, TCSAFLUSH, &original);
        }
    };

    int runInteractiveLoop(int size_max);
    std::string colorize(const std::string& text, const ColorConfig& cfg) const;
    std::string hline(const std::string& pattern, int width) const;
    std::string render(int width) const;

    static const std::unordered_map<int, std::string>& STYLES();
    static const std::unordered_map<std::string, std::unordered_map<int, std::string>>& COLORS();
    static const std::unordered_map<int, Border>& BORDERS();
};

// ---------------------------------------------------------------------------
// Helpers de UTF-8: los bordes (●, ○, ★, ┌, ...) ocupan mas de un byte cada
// uno. Sin esto, calcular anchos con .size() o cortar con .substr() en medio
// de un caracter multibyte rompe la terminal.
// ---------------------------------------------------------------------------

namespace grmenu_detail {

inline size_t utf8CharLen(unsigned char leadByte) {
    if ((leadByte & 0x80) == 0x00) return 1;
    if ((leadByte & 0xE0) == 0xC0) return 2;
    if ((leadByte & 0xF0) == 0xE0) return 3;
    if ((leadByte & 0xF8) == 0xF0) return 4;
    return 1;
}

inline size_t utf8Length(const std::string& s) {
    size_t count = 0;
    for (size_t i = 0; i < s.size(); count++)
        i += utf8CharLen(static_cast<unsigned char>(s[i]));
    return count;
}

inline std::string utf8Substr(const std::string& s, size_t maxChars) {
    size_t i = 0, count = 0;
    while (i < s.size() && count < maxChars) {
        i += utf8CharLen(static_cast<unsigned char>(s[i]));
        count++;
    }
    return s.substr(0, i);
}

inline std::string utf8Ljust(const std::string& s, int width) {
    int pad = width - static_cast<int>(utf8Length(s));
    return pad > 0 ? s + std::string(static_cast<size_t>(pad), ' ') : s;
}

inline std::string utf8Center(const std::string& s, int width) {
    int pad = width - static_cast<int>(utf8Length(s));
    if (pad <= 0) return s;
    int left = pad / 2;
    int right = pad - left;
    return std::string(static_cast<size_t>(left), ' ') + s + std::string(static_cast<size_t>(right), ' ');
}

} // namespace grmenu_detail

// ---------------------------------------------------------------------------
// Definiciones. Al estar marcadas "inline", el linker las tolera aunque este
// header se incluya desde varios .cpp del mismo programa.
// ---------------------------------------------------------------------------

inline const std::unordered_map<int, std::string>& GRmenu::STYLES() {
    static const std::unordered_map<int, std::string> table = {
        {1, "#"}, {2, "┌"}, {3, "╔"}, {4, "┏"}, {5, "╒"},
        {6, "╓"}, {7, "╭"}, {8, "▛"}, {9, "▓"}, {10, "▒"},
        {11, "░"}, {12, "█"}, {13, "*"}, {14, "+"}, {15, "="},
        {16, "~"}, {17, "-"}, {18, "◆"}, {19, "●"}, {20, "★"},
    };
    return table;
}

inline const std::unordered_map<std::string, std::unordered_map<int, std::string>>& GRmenu::COLORS() {
    static const std::unordered_map<std::string, std::unordered_map<int, std::string>> table = {
        {"black",   {{1, "\x1b[30m"}, {2, "\x1b[90m"}}},
        {"red",     {{1, "\x1b[31m"}, {2, "\x1b[91m"}}},
        {"green",   {{1, "\x1b[32m"}, {2, "\x1b[92m"}}},
        {"yellow",  {{1, "\x1b[33m"}, {2, "\x1b[93m"}}},
        {"blue",    {{1, "\x1b[34m"}, {2, "\x1b[94m"}}},
        {"magenta", {{1, "\x1b[35m"}, {2, "\x1b[95m"}}},
        {"cyan",    {{1, "\x1b[36m"}, {2, "\x1b[96m"}}},
        {"white",   {{1, "\x1b[37m"}, {2, "\x1b[97m"}}},
    };
    return table;
}

inline const std::unordered_map<int, GRmenu::Border>& GRmenu::BORDERS() {
    static const std::unordered_map<int, Border> table = {
        {1,  {"=-", "|", "#", "#", "#", "#"}},
        {2,  {"─", "│", "┌", "┐", "└", "┘"}},
        {3,  {"═", "║", "╔", "╗", "╚", "╝"}},
        {4,  {"━", "┃", "┏", "┓", "┗", "┛"}},
        {5,  {"═", "│", "╒", "╕", "╘", "╛"}},
        {6,  {"─", "║", "╓", "╖", "╙", "╜"}},
        {7,  {"─", "│", "╭", "╮", "╰", "╯"}},
        {8,  {"▀", "▌", "▛", "▜", "▙", "▟"}},
        {19, {"●○", "●", "●", "●", "●", "●"}},
        {20, {"★☆", "★", "★", "★", "★", "★"}},
    };
    return table;
}

inline std::string GRmenu::colorize(const std::string& text, const ColorConfig& cfg) const {
    if (cfg.color.empty()) return text;
    auto colorIt = COLORS().find(cfg.color);
    if (colorIt == COLORS().end()) return text;
    auto levelIt = colorIt->second.find(cfg.level);
    if (levelIt == colorIt->second.end()) return text;
    return levelIt->second + text + kReset;
}

inline std::string GRmenu::hline(const std::string& pattern, int width) const {
    using namespace grmenu_detail;
    if (width <= 0 || pattern.empty()) return "";
    int patLen = static_cast<int>(utf8Length(pattern));
    int reps = width / patLen + 1;
    std::string repeated;
    repeated.reserve(pattern.size() * static_cast<size_t>(reps));
    for (int i = 0; i < reps; ++i) repeated += pattern;
    return utf8Substr(repeated, static_cast<size_t>(width));
}

inline std::string GRmenu::render(int width) const {
    using namespace grmenu_detail;
    std::string out;
    auto line = [&](const std::string& text) { out += text + "\r\n"; };

    auto borderIt = BORDERS().find(style_num_);
    if (borderIt != BORDERS().end()) {
        const Border& b = borderIt->second;
        std::string fill = hline(b.h, width - 2);
        std::string v = colorize(b.v, style_.border);

        line(colorize(b.tl + fill + b.tr, style_.border));
        if (!title_.empty()) {
            line(v + " " + utf8Center(title_, width - 4) + " " + v);
            line(colorize(b.v + fill + b.v, style_.border));
        }
        for (size_t i = 0; i < options_.size(); ++i) {
            const std::string& name = options_[i].name;
            if (static_cast<int>(i) == index_) {
                std::string opt = colorize(">" + utf8Ljust(name, width - 6), style_.focus);
                line(v + "  " + opt + " " + v);
            } else {
                std::string opt = colorize("> " + utf8Ljust(name, width - 6), style_.options);
                line(v + " " + opt + " " + v);
            }
        }
        line(colorize(b.bl + fill + b.br, style_.border));
    } else {
        auto styleIt = STYLES().find(style_num_);
        std::string symbol = styleIt != STYLES().end() ? styleIt->second : "#";

        std::string solidLine;
        for (int i = 0; i < width; ++i) solidLine += symbol;
        std::string border = colorize(symbol, style_.border);

        line(colorize(solidLine, style_.border));
        if (!title_.empty()) {
            line(border + " " + utf8Center(title_, width - 4) + " " + border);
            line(colorize(solidLine, style_.border));
        }
        for (size_t i = 0; i < options_.size(); ++i) {
            const std::string& name = options_[i].name;
            const ColorConfig& cfg = (static_cast<int>(i) == index_) ? style_.focus : style_.options;
            line(border + " " + colorize(utf8Ljust(name, width - 4), cfg) + " " + border);
        }
        line(colorize(solidLine, style_.border));
    }
    return out;
}

inline int GRmenu::runInteractiveLoop(int size_max) {
    using namespace grmenu_detail;
    char buf[8];
    while (true) {
        ssize_t n = ::read(STDIN_FILENO, buf, sizeof(buf) - 1);
        if (n <= 0) return -1;
        std::string key(buf, static_cast<size_t>(n));
        if (key == "q") return -1;

        if (key == "\x1b[A") up();
        else if (key == "\x1b[B") down();

        int width = size_max;
        for (const auto& opt : options_)
            width = std::max<int>(width, static_cast<int>(utf8Length(opt.name)) + 4);
        if (!title_.empty())
            width = std::max<int>(width, static_cast<int>(utf8Length(title_)) + 4);

        std::fputs(kClearSeq, stdout);
        std::fputs(render(width).c_str(), stdout);
        std::fflush(stdout);

        if ((key == "\r" || key == "\n") && !options_.empty())
            return index_;
    }
}

inline void GRmenu::draw(int size_max) {
    std::fputs("Presiona una tecla para comenzar...\r\n", stdout);
    std::fflush(stdout);

    int selected = -1;
    {
        RawModeGuard guard;
        if (!guard.active) {
            std::fputs("GRmenu requiere una terminal TTY real.\n", stderr);
            return;
        }
        selected = runInteractiveLoop(size_max);
    } // el destructor de guard restaura la terminal aca

    std::fputs(kClearSeq, stdout);
    std::fflush(stdout);

    if (selected >= 0 && options_[static_cast<size_t>(selected)].action)
        options_[static_cast<size_t>(selected)].action();
}

// Azucar sintactico opcional: GRMENU_ACTION(mi_funcion) arma un Option con
// el nombre de la funcion (via stringize del preprocesador) y la funcion en
// si, para no tener que escribir el nombre a mano.
#define GRMENU_ACTION(fn) GRmenu::Option{#fn, fn}
