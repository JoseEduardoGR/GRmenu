import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Base64;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

// ===========================================================================
//  GRmenu 4.0.0 en Java
//  Port de python/GRmenu.py
//
//  Se corre con:  java e.java
//
//  Teclas:  flechas mover, Enter ejecutar, q salir, / buscar,
//           espacio marcar, t ver el codigo de la opcion.
//           Mouse: click y hover.
//
//  Lo que NO se pudo portar y por que, en un solo lugar:
//
//    - Windows. La version de Python tiene una rama entera con msvcrt y
//      ctypes. Java no tiene forma de poner la consola de Windows en modo
//      crudo sin una libreria nativa (JNA), asi que esta version es solo
//      Linux/macOS.
//
//    - El codigo fuente de una opcion (tecla 't'). Python lo saca en vivo
//      con inspect.getsource(). Java no guarda el fuente en el .class: no
//      hay forma de recuperarlo en tiempo de ejecucion. Aca el texto se
//      pasa a mano con new Opcion(...).conCodigo("..."), y si no se paso,
//      el panel lo dice.
//
//    - GRmenu -ex archivo.py, que cargaba un script de Python con runpy
//      para exportar su config. No tiene sentido en Java.
// ===========================================================================

class GRmenu {

    // =====================================================================
    //  Secuencias ANSI
    // =====================================================================

    static final String LIMPIAR      = "\u001b[H\u001b[2J\u001b[3J";
    static final String INICIO       = "\u001b[H";
    static final String BORRAR_ABAJO = "\u001b[J";
    static final String RESET        = "\u001b[0m";
    static final String CURSOR_OFF   = "\u001b[?25l";
    static final String CURSOR_ON    = "\u001b[?25h";
    static final String MOUSE_ON     = "\u001b[?1000h\u001b[?1003h";
    static final String MOUSE_OFF    = "\u001b[?1003l\u001b[?1000l";

    // =====================================================================
    //  Codigos de tecla
    //
    //  Una tecla normal se devuelve como su propio byte ('q' = 113). Todo
    //  lo que no es un byte suelto usa un numero negativo para no chocar.
    // =====================================================================

    static final int NADA      = -1;  // no llego ninguna tecla (tick de animacion)
    static final int ARRIBA    = -2;
    static final int ABAJO     = -3;
    static final int DERECHA   = -4;
    static final int IZQUIERDA = -5;
    static final int CLICK     = -6;
    static final int HOVER     = -7;
    static final int FIN       = -8;  // se cerro la entrada (EOF)

    static final int ENTER     = 13;
    static final int ESC       = 27;
    static final int CTRL_C    = 3;
    static final int BACKSPACE = 127;

    // =====================================================================
    //  Estilo global (el SetStyle de Python)
    // =====================================================================

    static class Color {
        final String color;
        final int level;

        Color(String color, int level) {
            this.color = color;
            this.level = level;
        }
    }

    static class SetStyle {
        static Color border      = new Color("cyan", 1);
        static Color options     = new Color("white", 1);
        static Color focus       = new Color("green", 2);
        static Color title       = new Color("yellow", 2);
        static Color banner      = new Color("magenta", 2);
        static Color subtitle    = new Color("cyan", 2);
        static Color divider     = new Color("blue", 1);
        static Color description = new Color("gray", 1);
        static int font = 1;

        static String welcomeText;
        static String welcomeImage;
        static Integer welcomeWidth;
        static Integer welcomeHeight;

        static void Border(String c, int n)      { border = new Color(c, n); }
        static void Options(String c, int n)     { options = new Color(c, n); }
        static void Focus(String c, int n)       { focus = new Color(c, n); }
        static void Title(String c, int n)       { title = new Color(c, n); }
        static void Banner(String c, int n)      { banner = new Color(c, n); }
        static void Subtitle(String c, int n)    { subtitle = new Color(c, n); }
        static void Divider(String c, int n)     { divider = new Color(c, n); }
        static void Description(String c, int n) { description = new Color(c, n); }

        static void Border(String c)      { Border(c, 1); }
        static void Options(String c)     { Options(c, 1); }
        static void Focus(String c)       { Focus(c, 2); }
        static void Title(String c)       { Title(c, 2); }
        static void Banner(String c)      { Banner(c, 2); }
        static void Subtitle(String c)    { Subtitle(c, 2); }
        static void Divider(String c)     { Divider(c, 1); }
        static void Description(String c) { Description(c, 1); }

        static void Font(int fontId) {
            font = fontId;
        }

        static void Welcome(String text, String image, Integer width, Integer height) {
            welcomeText = text;
            welcomeImage = image;
            welcomeWidth = width;
            welcomeHeight = height;
        }

        static void Welcome(String text) {
            Welcome(text, null, null, null);
        }
    }

    // =====================================================================
    //  Animaciones validas
    // =====================================================================

    static final String[] ANIMATIONS = { null, "linear", "fade", "diagonal", "rgb" };

    private static final double ANIM_FRAME_SECONDS = 0.035;
    private static final double ANIM_TICK_STEP = 0.08;

    // =====================================================================
    //  Estado del menu
    // =====================================================================

    final Nodo raiz = new Nodo();

    int style;
    String banner;
    String subtitle;
    int bannerStyle;
    boolean divider;
    boolean center;
    String animate;

    private String sttyOriginal;
    private double animTick;
    private boolean preview;
    private boolean imagenMostrada;
    private String lastShape;

    final List<Nodo> chain = new ArrayList<>();
    int focus;

    private final List<Marca> marcadas = new ArrayList<>();
    private List<Region> clickRegions = new ArrayList<>();
    private int[] lastClick;
    private int[] lastHover;

    static class Marca {
        final Nodo nodo;
        final int index;

        Marca(Nodo nodo, int index) {
            this.nodo = nodo;
            this.index = index;
        }
    }

    static class Region {
        final int r0, r1, c0, c1;
        final Nodo nodo;
        final int index;

        Region(int r0, int r1, int c0, int c1, Nodo nodo, int index) {
            this.r0 = r0; this.r1 = r1; this.c0 = c0; this.c1 = c1;
            this.nodo = nodo; this.index = index;
        }
    }

    static class Panel {
        final Nodo nodo;
        final int width;
        final List<String> lines;
        final List<Integer> targets;

        Panel(Nodo nodo, int width, List<String> lines, List<Integer> targets) {
            this.nodo = nodo;
            this.width = width;
            this.lines = lines;
            this.targets = targets;
        }
    }

    // =====================================================================
    //  Constructores
    // =====================================================================

    GRmenu(Item[] items) throws Exception {
        this(items, "", 19, "", "", 3, null, true, null, 10, false, null);
    }

    GRmenu(Item[] items, String title) throws Exception {
        this(items, title, 19, "", "", 3, null, true, null, 10, false, null);
    }

    GRmenu(Item[] items, String title, int style) throws Exception {
        this(items, title, style, "", "", 3, null, true, null, 10, false, null);
    }

    GRmenu(Item[] items, String title, int style, String banner, String subtitle,
           int bannerStyle, Boolean divider, boolean center, Integer font,
           Integer maxShowOptions, boolean searchable, String animate) throws Exception {

        if (!animacionValida(animate)) {
            throw new IllegalArgumentException(
                "animate debe ser null, \"linear\", \"fade\", \"diagonal\" o \"rgb\", no \"" + animate + "\"");
        }

        raiz.items = items == null ? new Item[0] : items;
        raiz.title = title == null ? "" : title;
        raiz.maxShowOptions = maxShowOptions;
        raiz.searchable = searchable;

        this.style = style;
        this.banner = banner == null ? "" : banner;
        this.subtitle = subtitle == null ? "" : subtitle;
        this.bannerStyle = bannerStyle;
        this.center = center;
        this.animate = animate;
        this.divider = divider != null
                     ? divider
                     : (!this.banner.isEmpty() || !this.subtitle.isEmpty());

        if (font != null) {
            SetStyle.Font(font);
        }

        chain.add(raiz);

        modoCrudo();
        salida(MOUSE_ON);
        salida(CURSOR_OFF);
        asegurarTamanoTerminal();
    }

    private static boolean animacionValida(String a) {
        for (String v : ANIMATIONS) {
            if (v == null ? a == null : v.equals(a)) {
                return true;
            }
        }
        return false;
    }

    // =====================================================================
    //  Impresion
    // =====================================================================

    // El GRprint de Python. En modo crudo la terminal deja de traducir el
    // "\n": el cursor baja pero no vuelve al margen izquierdo. Python podia
    // reemplazar el print global; Java no, asi que todo pasa por aca.
    static void p(String texto) {
        System.out.print(texto + "\r\n");
    }

    static void p() {
        p("");
    }

    private static void salida(String texto) {
        System.out.print(texto);
        System.out.flush();
    }

    // =====================================================================
    //  Terminal en modo crudo
    // =====================================================================
    //  Python tiene termios y tty.setraw. Java no tiene nada equivalente,
    //  asi que el cambio se le pide al programa `stty` del sistema.

    private void modoCrudo() throws Exception {
        sttyOriginal = stty("-g");
        stty("raw", "-echo");
    }

    void restaurarTerminal() {
        try {
            if (sttyOriginal != null && !sttyOriginal.isEmpty()) {
                stty(sttyOriginal);
            }
        } catch (Exception e) {
            // Si stty falla aca no hay nada mejor que hacer: seguimos y al
            // menos devolvemos el cursor y apagamos el mouse.
        }
        salida(MOUSE_OFF);
        salida(CURSOR_ON);
    }

    static String stty(String... argumentos) throws Exception {
        String[] comando = new String[argumentos.length + 1];
        comando[0] = "stty";
        System.arraycopy(argumentos, 0, comando, 1, argumentos.length);

        ProcessBuilder pb = new ProcessBuilder(comando);
        // stty modifica la terminal que tenga en su entrada: si le damos una
        // tuberia falla con "ioctl no apropiada para el dispositivo".
        pb.redirectInput(ProcessBuilder.Redirect.INHERIT);

        Process proceso = pb.start();
        String salida = new String(proceso.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
        proceso.waitFor();
        return salida.trim();
    }

    // Python usaba os.get_terminal_size(). Java no lo trae: se lo
    // preguntamos a stty, que devuelve "filas columnas".
    static int[] tamanoTerminal() {
        try {
            String salida = stty("size");
            String[] partes = salida.trim().split("\\s+");
            if (partes.length >= 2) {
                return new int[]{ Integer.parseInt(partes[0]), Integer.parseInt(partes[1]) };
            }
        } catch (Exception e) {
            // sin terminal real
        }
        return new int[]{ 24, 80 };
    }

    static int anchoTerminal() {
        return tamanoTerminal()[1];
    }

    // =====================================================================
    //  Agrandar la terminal si el menu no entra
    // =====================================================================

    int[] estimarTamano() {
        int width = 20;
        for (Item it : raiz.items) {
            width = Math.max(width, it.nombre().length() + 8);
        }
        if (!raiz.title.isEmpty()) {
            width = Math.max(width, raiz.title.length() + 4);
        }
        int limite = raiz.maxShowOptions == null ? raiz.items.length : raiz.maxShowOptions;
        int visibles = Math.min(raiz.items.length, limite);
        int height = 2 + (raiz.title.isEmpty() ? 0 : 1) + visibles + 2;

        if (!banner.isEmpty()) {
            List<String> rows = buildAsciiLines(banner, 999, SetStyle.font);
            if (rows != null) {
                width = Math.max(width, largoMaximo(rows) + 6);
                height += rows.size() + 3;
            } else {
                width = Math.max(width, banner.trim().length() + 6);
                height += 3;
            }
        }
        if (!subtitle.isEmpty()) {
            String[] subLines = subtitle.split("\n", -1);
            int ancho = 0;
            for (String ln : subLines) {
                ancho = Math.max(ancho, ln.length());
            }
            width = Math.max(width, ancho + 2);
            height += subLines.length + (divider ? 2 : 0) + 1;
        }
        return new int[]{ width + 2, height + 2 };
    }

    void asegurarTamanoTerminal() {
        int[] actual = tamanoTerminal();
        int curRows = actual[0];
        int curCols = actual[1];

        int[] necesario = estimarTamano();
        int needCols = Math.min(necesario[0], 300);
        int needRows = Math.min(necesario[1], 80);
        if (needCols <= curCols && needRows <= curRows) {
            return;
        }

        int rows = Math.max(needRows, curRows);
        int cols = Math.max(needCols, curCols);

        // XTWINOPS: la soporta xterm y varios mas. kitty la rechaza a
        // proposito, por eso abajo esta el segundo intento.
        salida("\u001b[8;" + rows + ";" + cols + "t");
        if (esperarTamano(needCols, needRows)) {
            return;
        }

        if (System.getenv("KITTY_WINDOW_ID") != null) {
            try {
                ProcessBuilder pb = new ProcessBuilder(
                    "kitty", "@", "resize-os-window", "--self", "--unit", "cells",
                    "--width", String.valueOf(cols), "--height", String.valueOf(rows));
                pb.redirectOutput(ProcessBuilder.Redirect.DISCARD);
                pb.redirectError(ProcessBuilder.Redirect.DISCARD);
                pb.start().waitFor();
            } catch (Exception e) {
                return;
            }
            esperarTamano(needCols, needRows);
        }
    }

    private static boolean esperarTamano(int needCols, int needRows) {
        for (int i = 0; i < 10; i++) {
            dormir(20);
            int[] size = tamanoTerminal();
            if (size[1] >= needCols && size[0] >= needRows) {
                return true;
            }
        }
        return false;
    }

    private static void dormir(long ms) {
        try {
            Thread.sleep(ms);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    // =====================================================================
    //  Teclado y mouse
    // =====================================================================

    int leerTecla() throws IOException {
        InputStream in = System.in;
        int b = in.read();

        // -1 = se cerro la entrada. Va primero: si no, nunca coincide con
        // 'q' y el bucle no termina.
        if (b == -1) {
            return FIN;
        }
        if (b != ESC) {
            return b;
        }

        // Detras de un ESC puede venir una secuencia. Python leia los 3
        // bytes de un saque con os.read(fd, 3); aca hay que preguntar si
        // hay mas, con una pausa minima para darle tiempo a llegar.
        dormir(3);
        if (in.available() <= 0) {
            return ESC;             // Escape de verdad, solo
        }
        int c = in.read();
        if (c != '[') {
            return ESC;
        }
        int t = in.read();
        switch (t) {
            case 'A': return ARRIBA;
            case 'B': return ABAJO;
            case 'C': return DERECHA;
            case 'D': return IZQUIERDA;
            case 'M': return leerMouse(in);
            default:  return NADA;
        }
    }

    int[] ultimoClick() {
        return lastClick;
    }

    int[] ultimoHover() {
        return lastHover;
    }

    private int leerMouse(InputStream in) throws IOException {
        int cb = in.read();
        int cx = in.read();
        int cy = in.read();
        if (cb < 0 || cx < 0 || cy < 0) {
            return FIN;
        }
        int code = cb - 32;
        if (code == 64) return ARRIBA;      // rueda arriba
        if (code == 65) return ABAJO;       // rueda abajo
        if ((code & 32) != 0) {
            lastHover = new int[]{ cx - 32, cy - 32 };
            return HOVER;
        }
        if (code == 0) {
            lastClick = new int[]{ cx - 32, cy - 32 };
            return CLICK;
        }
        return NADA;
    }

    // Con animacion no se puede bloquear esperando tecla: hay que redibujar
    // aunque no pase nada. Python usaba select con timeout; Java pregunta
    // por available() en una espera corta.
    int leerTeclaOTick() throws IOException {
        if (animate == null) {
            return leerTecla();
        }
        long limite = System.nanoTime() + (long) (ANIM_FRAME_SECONDS * 1_000_000_000L);
        while (System.nanoTime() < limite) {
            if (System.in.available() > 0) {
                return leerTecla();
            }
            dormir(2);
        }
        animTick += ANIM_TICK_STEP;
        return NADA;
    }

    // =====================================================================
    //  Navegacion
    // =====================================================================

    List<Integer> indicesFiltrados(Nodo node) {
        List<Integer> todos = new ArrayList<>();
        if (!node.searchActive) {
            for (int i = 0; i < node.items.length; i++) {
                todos.add(i);
            }
            return todos;
        }
        String query = node.searchQuery.trim().toLowerCase();
        if (query.isEmpty()) {
            for (int i = 0; i < node.items.length; i++) {
                todos.add(i);
            }
            return todos;
        }
        for (int i = 0; i < node.items.length; i++) {
            if (node.items[i].nombre().toLowerCase().contains(query)) {
                todos.add(i);
            }
        }
        return todos;
    }

    static void ajustarScroll(Nodo node, List<Integer> filtered) {
        Integer limit = node.maxShowOptions;
        int total = filtered.size();
        if (limit == null || limit <= 0 || limit >= total) {
            node.scroll = 0;
            return;
        }
        int pos = filtered.indexOf(node.index);
        if (pos < 0) {
            pos = 0;
        }
        if (pos < node.scroll) {
            node.scroll = pos;
        } else if (pos >= node.scroll + limit) {
            node.scroll = pos - limit + 1;
        }
        node.scroll = Math.max(0, Math.min(node.scroll, total - limit));
    }

    private void mover(int paso) {
        Nodo node = chain.get(focus);
        List<Integer> filtered = indicesFiltrados(node);
        if (filtered.isEmpty()) {
            return;
        }
        int pos = filtered.indexOf(node.index);
        if (pos < 0) {
            pos = 0;
        }
        int n = filtered.size();
        node.index = filtered.get(((pos + paso) % n + n) % n);
        ajustarScroll(node, filtered);
    }

    void subir() {
        mover(-1);
    }

    void bajar() {
        mover(1);
    }

    // =====================================================================
    //  Datos: colores, bordes y fuentes (data/*.json)
    // =====================================================================

    private static Map<String, Map<String, String>> coloresCache;
    private static Map<String, int[]> rgbCache;
    private static Map<String, Map<String, String>> bordesCache;
    private static Map<String, Map<String, List<String>>> fuentesCache;

    static Path rutaDatos(String archivo) {
        String[] candidatos = { "data", "../data", "../../data" };
        for (String base : candidatos) {
            Path pth = Path.of(base, archivo);
            if (Files.exists(pth)) {
                return pth;
            }
        }
        return Path.of("data", archivo);
    }

    private static String leerArchivo(Path pth) {
        try {
            return Files.readString(pth, StandardCharsets.UTF_8);
        } catch (IOException e) {
            throw new RuntimeException("No se pudo leer " + pth + ": " + e.getMessage(), e);
        }
    }

    @SuppressWarnings("unchecked")
    static Map<String, Map<String, String>> COLORS() {
        if (coloresCache == null) {
            Map<String, Object> raw = Json.parseObjeto(leerArchivo(rutaDatos("colors.json")));
            Map<String, Map<String, String>> out = new LinkedHashMap<>();
            Map<String, int[]> rgb = new LinkedHashMap<>();
            for (Map.Entry<String, Object> e : raw.entrySet()) {
                Map<String, String> niveles = new LinkedHashMap<>();
                if (e.getValue() instanceof Map) {
                    Map<String, Object> codes = (Map<String, Object>) e.getValue();
                    for (Map.Entry<String, Object> c : codes.entrySet()) {
                        if (c.getKey().equals("rgb")) {
                            List<Object> t = (List<Object>) c.getValue();
                            rgb.put(e.getKey(), new int[]{
                                ((Double) t.get(0)).intValue(),
                                ((Double) t.get(1)).intValue(),
                                ((Double) t.get(2)).intValue() });
                        } else {
                            niveles.put(c.getKey(), "\u001b[" + c.getValue());
                        }
                    }
                } else {
                    niveles.put("1", "\u001b[" + e.getValue());
                    niveles.put("2", "\u001b[" + e.getValue());
                }
                out.put(e.getKey(), niveles);
            }
            coloresCache = out;
            rgbCache = rgb;
        }
        return coloresCache;
    }

    static int[] rgbDe(String nombre) {
        COLORS();
        int[] v = rgbCache.get(nombre);
        return v == null ? new int[]{ 255, 255, 255 } : v;
    }

    static String reset() {
        Map<String, String> r = COLORS().get("reset");
        if (r == null || r.isEmpty()) {
            return RESET;
        }
        return r.values().iterator().next();
    }

    @SuppressWarnings("unchecked")
    static Map<String, Map<String, String>> BORDERS() {
        if (bordesCache == null) {
            Map<String, Object> raw = Json.parseObjeto(leerArchivo(rutaDatos("borders.json")));
            Map<String, Map<String, String>> out = new LinkedHashMap<>();
            for (Map.Entry<String, Object> e : raw.entrySet()) {
                Map<String, String> piezas = new LinkedHashMap<>();
                if (e.getValue() instanceof Map) {
                    for (Map.Entry<String, Object> c : ((Map<String, Object>) e.getValue()).entrySet()) {
                        piezas.put(c.getKey(), String.valueOf(c.getValue()));
                    }
                } else {
                    // Estilo "simple": un solo caracter para las 6 piezas.
                    String s = String.valueOf(e.getValue());
                    for (String k : new String[]{ "h", "v", "tl", "tr", "bl", "br" }) {
                        piezas.put(k, s);
                    }
                }
                out.put(e.getKey(), piezas);
            }
            bordesCache = out;
        }
        return bordesCache;
    }

    static Map<String, String> borde(int estilo) {
        return BORDERS().get(String.valueOf(estilo));
    }

    @SuppressWarnings("unchecked")
    static Map<String, Map<String, List<String>>> FONTS() {
        if (fuentesCache == null) {
            Map<String, Object> raw = Json.parseObjeto(leerArchivo(rutaDatos("fonts.json")));
            Map<String, Map<String, List<String>>> out = new LinkedHashMap<>();
            for (Map.Entry<String, Object> fuente : raw.entrySet()) {
                Map<String, List<String>> glifos = new LinkedHashMap<>();
                for (Map.Entry<String, Object> g : ((Map<String, Object>) fuente.getValue()).entrySet()) {
                    List<String> filas = new ArrayList<>();
                    for (Object o : (List<Object>) g.getValue()) {
                        filas.add(String.valueOf(o));
                    }
                    glifos.put(g.getKey(), filas);
                }
                out.put(fuente.getKey(), glifos);
            }
            fuentesCache = out;
        }
        return fuentesCache;
    }

    // =====================================================================
    //  Color
    // =====================================================================

    static String pintar(String texto, Color cfg) {
        if (cfg == null) {
            return texto;
        }
        Map<String, String> niveles = COLORS().get(cfg.color);
        if (niveles == null) {
            return texto;
        }
        String code = niveles.get(String.valueOf(cfg.level));
        if (code == null || code.isEmpty()) {
            return texto;
        }
        return code + texto + reset();
    }

    private static int[] ondaRgb(double t) {
        int r = (int) Math.max(0, Math.min(255, Math.sin(t) * 127 + 128));
        int g = (int) Math.max(0, Math.min(255, Math.sin(t + 2.0943951) * 127 + 128));
        int b = (int) Math.max(0, Math.min(255, Math.sin(t + 4.1887902) * 127 + 128));
        return new int[]{ r, g, b };
    }

    private static int[] escalarRgb(int[] base, double factor) {
        double low = 0.25;
        double f = low + (1 - low) * factor;
        return new int[]{
            (int) Math.max(0, Math.min(255, base[0] * f)),
            (int) Math.max(0, Math.min(255, base[1] * f)),
            (int) Math.max(0, Math.min(255, base[2] * f)),
        };
    }

    private int[] colorAnimado(Color cfg, double t) {
        if ("rgb".equals(animate)) {
            return ondaRgb(t);
        }
        int[] base = rgbDe(cfg == null ? null : cfg.color);
        double factor = (Math.sin(t) + 1) / 2;
        return escalarRgb(base, factor);
    }

    String pintarAnim(String texto, Color cfg) {
        return pintarAnim(texto, cfg, 0, 0);
    }

    String pintarAnim(String texto, Color cfg, int row, int col) {
        if (animate == null || cfg == null) {
            return pintar(texto, cfg);
        }
        if ("fade".equals(animate)) {
            int[] c = colorAnimado(cfg, animTick);
            return "\u001b[38;2;" + c[0] + ";" + c[1] + ";" + c[2] + "m" + texto + RESET;
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < texto.length(); i++) {
            char ch = texto.charAt(i);
            if (ch == ' ' || ch == '\n' || ch == '\t') {
                sb.append(ch);
                continue;
            }
            int pos = col + i;
            double phase;
            if ("rgb".equals(animate)) {
                phase = pos * 0.12;
            } else if ("diagonal".equals(animate)) {
                phase = pos * 0.3 + row * 0.6;
            } else {
                phase = pos * 0.3;
            }
            int[] c = colorAnimado(cfg, animTick + phase);
            sb.append("\u001b[38;2;").append(c[0]).append(';').append(c[1]).append(';')
              .append(c[2]).append('m').append(ch);
        }
        return sb.append(RESET).toString();
    }

    // =====================================================================
    //  Ayudas de texto
    //
    //  Python trae center(), ljust() y rjust() de fabrica. Java no.
    // =====================================================================

    static String hline(String h, int ancho) {
        if (ancho <= 0 || h == null || h.isEmpty()) {
            return "";
        }
        return h.repeat(ancho / h.length() + 1).substring(0, ancho);
    }

    static String izq(String texto, int ancho) {
        if (texto.length() >= ancho) {
            return texto;
        }
        return texto + " ".repeat(ancho - texto.length());
    }

    static String der(String texto, int ancho) {
        if (texto.length() >= ancho) {
            return texto;
        }
        return " ".repeat(ancho - texto.length()) + texto;
    }

    static String centrado(String texto, int ancho) {
        if (texto.length() >= ancho) {
            return texto;
        }
        int sobra = ancho - texto.length();
        int izquierda = sobra / 2;
        return " ".repeat(izquierda) + texto + " ".repeat(sobra - izquierda);
    }

    static String recortar(String texto, int ancho) {
        return texto.length() > ancho ? texto.substring(0, ancho) : texto;
    }

    private static int largoMaximo(List<String> filas) {
        int max = 0;
        for (String f : filas) {
            max = Math.max(max, f.length());
        }
        return max;
    }

    // =====================================================================
    //  Banner en arte ASCII
    // =====================================================================

    static List<String> buildAsciiLines(String texto, int maxCols, int fontId) {
        Map<String, Map<String, List<String>>> fuentes = FONTS();
        Map<String, List<String>> glifos = fuentes.get(String.valueOf(fontId));
        if (glifos == null) {
            glifos = fuentes.get("1");
        }
        if (glifos == null) {
            return null;
        }
        List<String> chars = new ArrayList<>();
        for (char c : texto.toUpperCase().toCharArray()) {
            String k = String.valueOf(c);
            if (glifos.containsKey(k)) {
                chars.add(k);
            }
        }
        if (chars.isEmpty()) {
            return null;
        }
        int height = glifos.values().iterator().next().size();
        for (int spacing : new int[]{ 2, 1, 0 }) {
            List<String> lines = new ArrayList<>();
            StringBuilder[] sb = new StringBuilder[height];
            for (int r = 0; r < height; r++) {
                sb[r] = new StringBuilder();
            }
            for (int i = 0; i < chars.size(); i++) {
                String pad = i == chars.size() - 1 ? "" : " ".repeat(spacing);
                List<String> g = glifos.get(chars.get(i));
                for (int r = 0; r < height; r++) {
                    sb[r].append(g.get(r)).append(pad);
                }
            }
            for (StringBuilder s : sb) {
                lines.add(s.toString());
            }
            if (largoMaximo(lines) + 6 <= maxCols) {
                return lines;
            }
        }
        return null;
    }

    // Helper suelto: dibuja un banner sin crear un menu.
    static void banner(String texto, int delayMs, String color, int level, int estilo, int font) {
        int cols = anchoTerminal();
        Color cfg = new Color(color, level);
        Map<String, String> b = borde(estilo);
        if (b == null) {
            b = borde(3);
        }
        List<String> rows = buildAsciiLines(texto, cols, font);
        if (rows != null) {
            int width = largoMaximo(rows) + 4;
            String linea = hline(b.get("h"), width);
            p(pintar(b.get("tl") + linea + b.get("tr"), cfg));
            for (String r : rows) {
                p(pintar(b.get("v") + "  " + r + "  " + b.get("v"), cfg));
                if (delayMs > 0) {
                    dormir(delayMs);
                }
            }
            p(pintar(b.get("bl") + linea + b.get("br"), cfg));
        } else {
            String t = texto.trim();
            int width = Math.min(t.length() + 4, cols - 4);
            String linea = hline(b.get("h"), width);
            p(pintar(b.get("tl") + linea + b.get("tr"), cfg));
            p(pintar(b.get("v") + " " + centrado(t, width) + " " + b.get("v"), cfg));
            p(pintar(b.get("bl") + linea + b.get("br"), cfg));
        }
    }

    static void banner(String texto) {
        banner(texto, 0, "magenta", 2, 3, 1);
    }

    // =====================================================================
    //  Codigo fuente de una opcion (tecla 't')
    // =====================================================================

    static List<String> fuente(Item item, int maxLines) {
        List<String> out = new ArrayList<>();
        if (item instanceof Nodo) {
            out.add("(esto es un submenu, no tiene codigo fuente)");
            return out;
        }
        String codigo = item instanceof Opcion ? ((Opcion) item).codigo : null;
        if (codigo == null || codigo.isEmpty()) {
            out.add("(Java no guarda el codigo fuente en el .class:");
            out.add(" no hay equivalente de inspect.getsource().");
            out.add("");
            out.add(" Pasalo a mano si lo querres ver aca:");
            out.add("   new Opcion(\"...\", accion).conCodigo(\"...\")");
            return out;
        }
        String[] lineas = codigo.split("\n", -1);
        for (int i = 0; i < lineas.length && i < maxLines; i++) {
            out.add(lineas[i]);
        }
        if (lineas.length > maxLines) {
            out.add("... (+" + (lineas.length - maxLines) + " lineas)");
        }
        return out.isEmpty() ? List.of("(sin contenido)") : out;
    }

    // =====================================================================
    //  Imagenes
    // =====================================================================

    static String protocoloImagen() {
        if (System.getenv("KITTY_WINDOW_ID") != null
            || "xterm-kitty".equals(System.getenv("TERM"))) {
            return "kitty";
        }
        String prog = System.getenv("TERM_PROGRAM");
        if ("iTerm.app".equals(prog) || "WezTerm".equals(prog)) {
            return "iterm2";
        }
        return null;
    }

    private static final double CELL_ASPECT = 0.5;

    // Lee el ancho y alto de la imagen del encabezado del archivo, sin
    // decodificarla. Igual que _sniff_image_size en Python.
    static int[] medirImagen(String ruta) {
        try {
            byte[] datos = Files.readAllBytes(Path.of(ruta));
            if (datos.length >= 24 && (datos[0] & 0xFF) == 0x89
                && datos[1] == 'P' && datos[2] == 'N' && datos[3] == 'G') {
                return new int[]{ leerBE(datos, 16, 4), leerBE(datos, 20, 4) };
            }
            if (datos.length >= 10 && datos[0] == 'G' && datos[1] == 'I' && datos[2] == 'F') {
                return new int[]{ leerLE(datos, 6, 2), leerLE(datos, 8, 2) };
            }
            if (datos.length >= 26 && datos[0] == 'B' && datos[1] == 'M') {
                return new int[]{ Math.abs(leerLE(datos, 18, 4)), Math.abs(leerLE(datos, 22, 4)) };
            }
            if (datos.length >= 4 && (datos[0] & 0xFF) == 0xFF && (datos[1] & 0xFF) == 0xD8) {
                int i = 2;
                while (i + 9 < datos.length) {
                    if ((datos[i] & 0xFF) != 0xFF) {
                        return null;
                    }
                    int kind = datos[i + 1] & 0xFF;
                    if (kind == 0xD8 || kind == 0xD9) {
                        i += 2;
                        continue;
                    }
                    int segLen = leerBE(datos, i + 2, 2);
                    if (kind >= 0xC0 && kind <= 0xCF && kind != 0xC4 && kind != 0xC8 && kind != 0xCC) {
                        return new int[]{ leerBE(datos, i + 7, 2), leerBE(datos, i + 5, 2) };
                    }
                    i += 2 + segLen;
                }
            }
        } catch (Exception e) {
            return null;
        }
        return null;
    }

    private static int leerBE(byte[] d, int off, int n) {
        int v = 0;
        for (int i = 0; i < n; i++) {
            v = (v << 8) | (d[off + i] & 0xFF);
        }
        return v;
    }

    private static int leerLE(byte[] d, int off, int n) {
        int v = 0;
        for (int i = n - 1; i >= 0; i--) {
            v = (v << 8) | (d[off + i] & 0xFF);
        }
        return v;
    }

    static void mostrarImagen(String ruta, Integer width, Integer height) {
        String protocolo = protocoloImagen();
        byte[] datos;
        try {
            datos = Files.readAllBytes(Path.of(ruta));
        } catch (IOException e) {
            p("No se pudo leer la imagen: " + ruta);
            return;
        }
        String b64 = Base64.getEncoder().encodeToString(datos);
        StringBuilder sb = new StringBuilder();
        if ("kitty".equals(protocolo)) {
            String size = "";
            if (width != null)  size += ",c=" + width;
            if (height != null) size += ",r=" + height;
            int chunkSize = 4096;
            int total = Math.max(1, (b64.length() + chunkSize - 1) / chunkSize);
            for (int i = 0; i < total; i++) {
                String chunk = b64.substring(i * chunkSize, Math.min(b64.length(), (i + 1) * chunkSize));
                int more = i < total - 1 ? 1 : 0;
                String header = i == 0 ? "a=T,f=100" + size + ",m=" + more : "m=" + more;
                sb.append("\u001b_G").append(header).append(';').append(chunk).append("\u001b\\");
            }
            sb.append('\n');
        } else {
            String size = "";
            if (width != null)  size += ";width=" + width;
            if (height != null) size += ";height=" + height;
            sb.append("\u001b]1337;File=inline=1;size=").append(datos.length)
              .append(size).append(':').append(b64).append('\u0007').append('\n');
        }
        salida(sb.toString());
    }

    static void borrarImagenes() {
        salida("\u001b_Ga=d,d=A\u001b\\");
    }

    private Integer bannerCols() {
        if (banner.isEmpty()) {
            return null;
        }
        int cols = anchoTerminal();
        List<String> rows = buildAsciiLines(banner, cols, SetStyle.font);
        if (rows != null) {
            return largoMaximo(rows) + 6;
        }
        return Math.min(banner.trim().length() + 6, cols - 2);
    }

    void welcome() {
        salida(LIMPIAR);
        String image = SetStyle.welcomeImage;
        String text = SetStyle.welcomeText;
        if (image == null && text == null) {
            text = LOGO_ASCII;
        }
        if (image != null) {
            if (protocoloImagen() != null) {
                Integer width = SetStyle.welcomeWidth;
                Integer height = SetStyle.welcomeHeight;
                if (width == null && height == null) {
                    Integer bc = bannerCols();
                    width = bc == null ? 40 : bc;
                    int[] size = medirImagen(image);
                    if (size != null && size[0] > 0) {
                        height = Math.max(1, (int) Math.round(
                            (double) size[1] / size[0] * width * CELL_ASPECT));
                    }
                }
                mostrarImagen(image, width, height);
                imagenMostrada = true;
            } else if (text != null) {
                for (String linea : text.split("\n", -1)) {
                    p(linea);
                }
            } else {
                p("Esta terminal no soporta imagenes");
            }
        } else if (text != null) {
            for (String linea : text.split("\n", -1)) {
                p(linea);
            }
        } else {
            p("Press any key to start ...");
        }
    }

    static final String LOGO_ASCII =
        "\u001b[97m  ██████╗     ██████╗   \u001b[94m    ██████╗      ██████╗     ██████╗      ███████╗  \u001b[0m\n"
      + "\u001b[97m ██╔════╝     ██╔══██╗  \u001b[94m   ██╔════╝     ██╔═══██╗    ██║  ██║     ██╔════╝  \u001b[0m\n"
      + "\u001b[97m ██║  ███╗    ██████╔╝  \u001b[94m   ██║          ██║   ██║    ██║  ██║     █████╗    \u001b[0m\n"
      + "\u001b[97m ██║   ██║    ██╔══██╗  \u001b[94m   ██║          ██║   ██║    ██║  ██║     ██╔══╝    \u001b[0m\n"
      + "\u001b[97m ╚██████╔╝    ██║  ██║  \u001b[94m   ╚██████╗     ╚██████╔╝    ██████╔╝     ███████╗  \u001b[0m\n"
      + "\u001b[97m  ╚═════╝     ╚═╝  ╚═╝  \u001b[94m    ╚═════╝      ╚═════╝     ╚═════╝      ╚══════╝  \u001b[0m";

    // =====================================================================
    //  Dibujo de un panel de opciones
    // =====================================================================

    Panel renderOptionPanel(Nodo node, int sizeMax, int estilo, boolean focused) {
        Map<String, String> b = borde(estilo);
        Color bc = SetStyle.border;
        Color oc = SetStyle.options;
        Color fc = SetStyle.focus;
        Color tc = SetStyle.title;
        Color dc = SetStyle.description;

        String title = node.title == null ? "" : node.title;
        boolean searching = node.searchActive;
        String searchRow = searching ? "Buscar: " + node.searchQuery + "_" : "";

        List<Integer> marcas = marcasDe(node);

        int width = sizeMax;
        for (Item it : node.items) {
            width = Math.max(width, it.nombre().length() + 8);
        }
        if (!title.isEmpty()) {
            width = Math.max(width, title.length() + 4);
        }
        if (!searchRow.isEmpty()) {
            width = Math.max(width, searchRow.length() + 4);
        }

        List<Integer> filtered = indicesFiltrados(node);
        Integer limit = node.maxShowOptions;
        int total = filtered.size();
        boolean truncated = limit != null && limit > 0 && limit < total;
        List<Integer> window = truncated
            ? filtered.subList(Math.min(node.scroll, total), Math.min(node.scroll + limit, total))
            : filtered;

        List<String> lines = new ArrayList<>();
        List<Integer> targets = new ArrayList<>();

        if (b != null) {
            String linea = hline(b.get("h"), width - 2);
            String vL = pintarAnim(b.get("v"), bc);
            String vR = pintarAnim(b.get("v"), bc, 0, width - 1);

            lines.add(pintarAnim(b.get("tl") + linea + b.get("tr"), bc, lines.size(), 0));
            targets.add(null);
            if (!title.isEmpty()) {
                lines.add(vL + " " + pintarAnim(centrado(title, width - 4), tc, lines.size(), 0) + " " + vR);
                targets.add(null);
                lines.add(pintarAnim(b.get("v") + linea + b.get("v"), bc, lines.size(), 0));
                targets.add(null);
            }
            if (searching) {
                lines.add(vL + " " + pintar(izq(searchRow, width - 4), dc) + " " + vR);
                targets.add(null);
                lines.add(pintarAnim(b.get("v") + linea + b.get("v"), bc, lines.size(), 0));
                targets.add(null);
            }
            if (window.isEmpty()) {
                lines.add(vL + " " + pintar(izq("(sin coincidencias)", width - 4), oc) + " " + vR);
                targets.add(null);
            }
            for (int i : window) {
                String name = node.items[i].nombre();
                if (marcas.contains(i)) {
                    Color color = node.index == i ? (focused ? fc : oc) : oc;
                    lines.add(vL + " " + pintar("[x] " + izq(name, width - 8), color) + " " + vR);
                } else if (node.index == i) {
                    lines.add(vL + "  " + pintar(">" + izq(name, width - 6), focused ? fc : oc) + " " + vR);
                } else {
                    lines.add(vL + " " + pintar("> " + izq(name, width - 6), oc) + " " + vR);
                }
                targets.add(i);
            }
            lines.add(pintarAnim(b.get("bl") + linea + b.get("br"), bc, lines.size(), 0));
            targets.add(null);
        } else {
            String simbolo = "#";
            String barra = pintar(simbolo.repeat(width), bc);
            String lado = pintar(simbolo, bc);

            lines.add(barra);
            targets.add(null);
            if (!title.isEmpty()) {
                lines.add(lado + " " + pintar(centrado(title, width - 4), tc) + " " + lado);
                targets.add(null);
                lines.add(barra);
                targets.add(null);
            }
            if (searching) {
                lines.add(lado + " " + pintar(izq(searchRow, width - 4), dc) + " " + lado);
                targets.add(null);
                lines.add(barra);
                targets.add(null);
            }
            if (window.isEmpty()) {
                lines.add(lado + " " + pintar(izq("(sin coincidencias)", width - 4), oc) + " " + lado);
                targets.add(null);
            }
            for (int i : window) {
                Color color = node.index == i ? (focused ? fc : oc) : oc;
                String contenido = marcas.contains(i)
                    ? "[x] " + node.items[i].nombre()
                    : node.items[i].nombre();
                lines.add(lado + " " + pintar(izq(contenido, width - 4), color) + " " + lado);
                targets.add(i);
            }
            lines.add(barra);
            targets.add(null);
        }

        agregarPie(node, lines, targets, width, truncated, filtered, total, marcas, dc);
        return new Panel(node, width, lines, targets);
    }

    void agregarPie(Nodo node, List<String> lines, List<Integer> targets, int width,
                    boolean truncated, List<Integer> filtered, int total,
                    List<Integer> marcas, Color dc) {
        if (truncated) {
            int pos = filtered.indexOf(node.index) + 1;
            lines.add(pintar(der(pos + " de " + total, width), dc));
            targets.add(null);
        }
        if (!marcas.isEmpty()) {
            String plural = marcas.size() == 1 ? "" : "s";
            lines.add(pintar(der(marcas.size() + " marcada" + plural, width), dc));
            targets.add(null);
        }
        Item actual = node.actual();
        String desc = actual == null ? "" : actual.descripcion();
        if (desc != null && !desc.isEmpty()) {
            lines.add(pintar(der(desc, width), dc));
            targets.add(null);
        }
    }

    List<Integer> marcasDe(Nodo node) {
        List<Integer> out = new ArrayList<>();
        for (Marca m : marcadas) {
            if (m.nodo == node) {
                out.add(m.index);
            }
        }
        return out;
    }

    Panel renderSourcePanel(Nodo node, int sizeMax, int estilo, int cols) {
        Map<String, String> b = borde(estilo);
        Color bc = SetStyle.border;
        Color oc = SetStyle.options;
        Color tc = SetStyle.title;

        Item actual = node.actual();
        List<String> src = actual == null ? List.of("(vacio)") : fuente(actual, 20);
        String title = "Preview: " + (actual == null ? "" : actual.nombre());

        int width = sizeMax;
        for (String l : src) {
            width = Math.max(width, l.length() + 4);
        }
        width = Math.max(width, title.length() + 4);
        width = Math.min(width, Math.max(20, cols - 4));

        List<String> lines = new ArrayList<>();
        if (b != null) {
            String linea = hline(b.get("h"), width - 2);
            String vL = pintarAnim(b.get("v"), bc);
            String vR = pintarAnim(b.get("v"), bc, 0, width - 1);
            lines.add(pintarAnim(b.get("tl") + linea + b.get("tr"), bc, lines.size(), 0));
            lines.add(vL + " " + pintarAnim(centrado(title, width - 4), tc, lines.size(), 0) + " " + vR);
            lines.add(pintarAnim(b.get("v") + linea + b.get("v"), bc, lines.size(), 0));
            for (String ln : src) {
                lines.add(vL + " " + pintar(izq(recortar(ln, width - 4), width - 4), oc) + " " + vR);
            }
            lines.add(pintarAnim(b.get("bl") + linea + b.get("br"), bc, lines.size(), 0));
        } else {
            String simbolo = "#";
            String barra = pintar(simbolo.repeat(width), bc);
            String lado = pintar(simbolo, bc);
            lines.add(barra);
            lines.add(lado + " " + pintar(centrado(title, width - 4), tc) + " " + lado);
            lines.add(barra);
            for (String ln : src) {
                lines.add(lado + " " + pintar(izq(recortar(ln, width - 4), width - 4), oc) + " " + lado);
            }
            lines.add(barra);
        }
        lines.add(pintar(der("'t' para volver al menu", width), SetStyle.description));

        List<Integer> targets = new ArrayList<>();
        for (int i = 0; i < lines.size(); i++) {
            targets.add(null);
        }
        return new Panel(node, width, lines, targets);
    }

    // =====================================================================
    //  Banner y subtitulo arriba del menu
    // =====================================================================

    int[] imprimirBannerSubtitulo(int cols, int contentW) {
        int printedRows = 0;
        int bannerW = 0;

        if (!banner.isEmpty()) {
            Map<String, String> bb = borde(bannerStyle);
            if (bb == null) {
                bb = borde(3);
            }
            List<String> rows = buildAsciiLines(banner, cols, SetStyle.font);
            if (rows != null) {
                bannerW = largoMaximo(rows) + 6;
                String bline = hline(bb.get("h"), bannerW - 2);
                p(pintarAnim(bb.get("tl") + bline + bb.get("tr"), SetStyle.banner, 0, 0));
                int r = 1;
                for (String row : rows) {
                    p(pintarAnim(bb.get("v") + "  " + row + "  " + bb.get("v"), SetStyle.banner, r, 0));
                    r++;
                }
                p(pintarAnim(bb.get("bl") + bline + bb.get("br"), SetStyle.banner, rows.size() + 1, 0));
                printedRows += rows.size() + 2;
            } else {
                String btext = banner.trim();
                bannerW = Math.min(btext.length() + 6, cols - 2);
                String bline = hline(bb.get("h"), bannerW - 2);
                p(pintarAnim(bb.get("tl") + bline + bb.get("tr"), SetStyle.banner, 0, 0));
                p(pintarAnim(bb.get("v") + " " + centrado(btext, bannerW - 4) + " " + bb.get("v"),
                             SetStyle.banner, 1, 0));
                p(pintarAnim(bb.get("bl") + bline + bb.get("br"), SetStyle.banner, 2, 0));
                printedRows += 3;
            }
            p();
            printedRows++;
        }

        int ref = bannerW != 0 ? bannerW : contentW;

        if (!subtitle.isEmpty()) {
            int divW = Math.min(ref, cols - 2);
            if (divider) {
                p(pintar("─".repeat(Math.max(0, divW)), SetStyle.divider));
                printedRows++;
            }
            String[] subLines = subtitle.split("\n", -1);
            for (String sub : subLines) {
                p(pintar(center ? centrado(sub, divW) : sub, SetStyle.subtitle));
            }
            printedRows += subLines.length;
            if (divider) {
                p(pintar("─".repeat(Math.max(0, divW)), SetStyle.divider));
                printedRows++;
            }
            p();
            printedRows++;
        }
        return new int[]{ printedRows, ref };
    }

    // =====================================================================
    //  draw
    // =====================================================================

    void draw() throws Exception {
        draw(20);
    }

    void draw(int sizeMax) throws Exception {
        welcome();
        try {
            drawLoop(sizeMax);
        } finally {
            restaurarTerminal();
        }
    }

    void drawLoop(int sizeMax) throws Exception {
        boolean firstKey = true;

        while (true) {
            int key = firstKey ? leerTecla() : leerTeclaOTick();
            firstKey = false;

            // --- mouse ---
            if (key == CLICK && lastClick != null && !preview) {
                int col = lastClick[0];
                int row = lastClick[1];
                for (Region r : clickRegions) {
                    if (row >= r.r0 && row < r.r1 && col >= r.c0 && col < r.c1 && chain.contains(r.nodo)) {
                        r.nodo.index = r.index;
                        focus = chain.indexOf(r.nodo);
                        key = ENTER;
                        break;
                    }
                }
            } else if (key == HOVER && lastHover != null && !preview) {
                int col = lastHover[0];
                int row = lastHover[1];
                boolean changed = false;
                for (Region r : clickRegions) {
                    if (row >= r.r0 && row < r.r1 && col >= r.c0 && col < r.c1 && chain.contains(r.nodo)) {
                        if (r.nodo.index != r.index || chain.get(focus) != r.nodo) {
                            r.nodo.index = r.index;
                            focus = chain.indexOf(r.nodo);
                            changed = true;
                        }
                        break;
                    }
                }
                if (!changed) {
                    continue;
                }
            }

            Nodo focusNode = chain.get(focus);
            boolean searching = focusNode.searchActive;

            if (key == CTRL_C || key == FIN || (key == 'q' && !searching)) {
                break;
            }

            if (imagenMostrada) {
                if ("kitty".equals(protocoloImagen())) {
                    borrarImagenes();
                }
                imagenMostrada = false;
            }

            // --- busqueda ---
            if (searching) {
                if (key == '/' || key == ESC) {
                    focusNode.searchActive = false;
                    focusNode.searchQuery = "";
                    searching = false;
                } else if (key == BACKSPACE || key == 8) {
                    if (!focusNode.searchQuery.isEmpty()) {
                        focusNode.searchQuery =
                            focusNode.searchQuery.substring(0, focusNode.searchQuery.length() - 1);
                    }
                } else if (key >= 32 && key <= 126) {
                    focusNode.searchQuery += (char) key;
                }
                if (searching) {
                    List<Integer> filtered = indicesFiltrados(focusNode);
                    if (!filtered.isEmpty() && !filtered.contains(focusNode.index)) {
                        focusNode.index = filtered.get(0);
                    }
                    ajustarScroll(focusNode, filtered);
                }
            } else if (key == '/' && focusNode.searchable && !preview) {
                focusNode.searchActive = true;
                focusNode.searchQuery = "";
            } else if (key == 't') {
                preview = !preview;
            } else if (key == ' ' && !preview) {
                Item fila = focusNode.actual();
                if (fila != null && !(fila instanceof Nodo)) {
                    if (!quitarMarca(focusNode, focusNode.index)) {
                        marcadas.add(new Marca(focusNode, focusNode.index));
                    }
                }
            }

            if (!preview && !searching) {
                if (key == ARRIBA) subir();
                if (key == ABAJO)  bajar();
            }

            focusNode = chain.get(focus);
            Item focusRow = focusNode.actual();

            // --- entrar / salir de submenus ---
            if (!preview) {
                if ((key == DERECHA || key == ENTER) && focusRow instanceof Nodo
                    && chain.size() < GRSubMenu.MAX_DEPTH) {
                    chain.add((Nodo) focusRow);
                    focus++;
                } else if (key == IZQUIERDA && focus > 0) {
                    focus--;
                    while (chain.size() > focus + 1) {
                        chain.remove(chain.size() - 1);
                    }
                }
            }

            focusNode = chain.get(focus);
            focusRow = focusNode.actual();

            // --- dibujo ---
            Nodo lastNode = chain.get(chain.size() - 1);
            Item lastRow = lastNode.actual();
            boolean hasLookahead = !preview
                                && chain.size() < GRSubMenu.MAX_DEPTH
                                && lastRow instanceof Nodo;
            String shape = chain.size() + "|" + preview + "|" + hasLookahead;
            if (!shape.equals(lastShape)) {
                salida(LIMPIAR);
            } else {
                salida(INICIO);
            }
            lastShape = shape;

            int cols = anchoTerminal();
            List<Panel> panels = new ArrayList<>();
            int estilo = style;
            for (int depth = 0; depth < chain.size(); depth++) {
                Nodo node = chain.get(depth);
                if (node.style != null) {
                    estilo = node.style;
                }
                boolean isDeepest = depth == chain.size() - 1;
                if (isDeepest && preview) {
                    panels.add(renderSourcePanel(node, sizeMax, estilo, cols));
                } else {
                    panels.add(renderOptionPanel(node, sizeMax, estilo, depth == focus));
                }
            }
            if (hasLookahead) {
                Nodo lookahead = (Nodo) lastRow;
                int lookaheadStyle = lookahead.style != null ? lookahead.style : estilo;
                panels.add(renderOptionPanel(lookahead, sizeMax, lookaheadStyle, false));
            }

            int chainW = 0;
            for (Panel pn : panels) {
                if (chain.contains(pn.nodo)) {
                    chainW += pn.width;
                }
            }
            chainW += 2 * (chain.size() - 1);

            int[] cabecera = imprimirBannerSubtitulo(cols, chainW);
            int printedRows = cabecera[0];
            int ref = cabecera[1];

            String outerPad = (center && ref > chainW) ? " ".repeat((ref - chainW) / 2) : "";

            int height = 0;
            for (Panel pn : panels) {
                height = Math.max(height, pn.lines.size());
            }

            List<Integer> panelCols = new ArrayList<>();
            int colCursor = outerPad.length() + 1;
            for (Panel pn : panels) {
                panelCols.add(colCursor);
                colCursor += pn.width + 2;
            }

            List<Region> regiones = new ArrayList<>();
            for (int rowI = 0; rowI < height; rowI++) {
                StringBuilder fila = new StringBuilder(outerPad);
                for (int pi = 0; pi < panels.size(); pi++) {
                    Panel pn = panels.get(pi);
                    if (pi > 0) {
                        fila.append("  ");
                    }
                    fila.append(rowI < pn.lines.size() ? pn.lines.get(rowI) : " ".repeat(pn.width));
                    Integer target = rowI < pn.targets.size() ? pn.targets.get(rowI) : null;
                    if (target != null) {
                        int absRow = printedRows + rowI + 1;
                        regiones.add(new Region(absRow, absRow + 1,
                                                panelCols.get(pi), panelCols.get(pi) + pn.width,
                                                pn.nodo, target));
                    }
                }
                p(fila.toString());
            }
            clickRegions = regiones;
            salida(BORRAR_ABAJO);

            // --- ejecutar ---
            if (key == ENTER && !preview && !(focusRow instanceof Nodo)) {
                List<Item> aEjecutar = new ArrayList<>();
                if (!marcadas.isEmpty()) {
                    for (Marca m : marcadas) {
                        aEjecutar.add(m.nodo.items[m.index]);
                    }
                } else if (focusRow != null) {
                    aEjecutar.add(focusRow);
                }
                if (!aEjecutar.isEmpty()) {
                    restaurarTerminal();
                    System.out.println(LIMPIAR);
                    for (Item it : aEjecutar) {
                        if (it instanceof Opcion) {
                            ((Opcion) it).ejecutar();
                        }
                    }
                    break;
                }
            }
        }
    }

    private boolean quitarMarca(Nodo nodo, int index) {
        for (int i = 0; i < marcadas.size(); i++) {
            Marca m = marcadas.get(i);
            if (m.nodo == nodo && m.index == index) {
                marcadas.remove(i);
                return true;
            }
        }
        return false;
    }

    // =====================================================================
    //  Configuracion .gr
    // =====================================================================
    //  Formato propio, pensado para leerse a ojo:
    //
    //     GRmenu::config::1
    //     <<border
    //       color:: cyan
    //       level:: 1
    //     >>
    //     font:: 1

    static final String CONFIG_HEADER = "GRmenu::config::1";
    static final String[] CONFIG_COLOR_SECTIONS = {
        "border", "options", "focus", "title", "banner", "subtitle", "divider", "description"
    };

    static Color seccion(String nombre) {
        return switch (nombre) {
            case "border"      -> SetStyle.border;
            case "options"     -> SetStyle.options;
            case "focus"       -> SetStyle.focus;
            case "title"       -> SetStyle.title;
            case "banner"      -> SetStyle.banner;
            case "subtitle"    -> SetStyle.subtitle;
            case "divider"     -> SetStyle.divider;
            case "description" -> SetStyle.description;
            default            -> null;
        };
    }

    static void ponerSeccion(String nombre, Color c) {
        switch (nombre) {
            case "border"      -> SetStyle.border = c;
            case "options"     -> SetStyle.options = c;
            case "focus"       -> SetStyle.focus = c;
            case "title"       -> SetStyle.title = c;
            case "banner"      -> SetStyle.banner = c;
            case "subtitle"    -> SetStyle.subtitle = c;
            case "divider"     -> SetStyle.divider = c;
            case "description" -> SetStyle.description = c;
            default -> { }
        }
    }

    static String ExportConfig(String path) throws IOException {
        StringBuilder sb = new StringBuilder();
        sb.append(CONFIG_HEADER).append("\n\n");
        for (String nombre : CONFIG_COLOR_SECTIONS) {
            Color cfg = seccion(nombre);
            sb.append("<<").append(nombre).append('\n');
            sb.append("  color:: ").append(cfg.color).append('\n');
            sb.append("  level:: ").append(cfg.level).append('\n');
            sb.append(">>\n\n");
        }
        sb.append("font:: ").append(SetStyle.font).append("\n\n");
        sb.append("<<welcome\n");
        sb.append("  text:: ").append(SetStyle.welcomeText == null
            ? "" : SetStyle.welcomeText.replace("\n", "\\n")).append('\n');
        sb.append("  image:: ").append(SetStyle.welcomeImage == null ? "" : SetStyle.welcomeImage).append('\n');
        sb.append("  width:: ").append(SetStyle.welcomeWidth == null ? "" : SetStyle.welcomeWidth).append('\n');
        sb.append("  height:: ").append(SetStyle.welcomeHeight == null ? "" : SetStyle.welcomeHeight).append('\n');
        sb.append(">>\n");
        Files.writeString(Path.of(path), sb.toString(), StandardCharsets.UTF_8);
        return path;
    }

    static Map<String, Map<String, String>> parseConfig(String path) throws IOException {
        List<String> raw = Files.readAllLines(Path.of(path), StandardCharsets.UTF_8);
        List<String> lines = new ArrayList<>();
        for (String ln : raw) {
            String s = ln.trim();
            if (!s.isEmpty() && !s.startsWith("#")) {
                lines.add(s);
            }
        }
        if (lines.isEmpty() || !lines.get(0).startsWith("GRmenu::config")) {
            throw new IllegalArgumentException(
                "'" + path + "' no es un archivo de configuracion GRmenu (.gr) valido: "
                + "falta la cabecera '" + CONFIG_HEADER + "'");
        }
        Map<String, Map<String, String>> data = new LinkedHashMap<>();
        Map<String, String> sueltos = new LinkedHashMap<>();
        data.put("", sueltos);

        String section = null;
        Map<String, String> sectionData = null;
        for (int i = 1; i < lines.size(); i++) {
            String s = lines.get(i);
            if (s.startsWith("<<")) {
                if (section != null) {
                    throw new IllegalArgumentException(
                        "'" + path + "': seccion '" + section + "' sin cerrar antes de abrir '"
                        + s.substring(2) + "'");
                }
                section = s.substring(2).trim();
                sectionData = new LinkedHashMap<>();
            } else if (s.equals(">>")) {
                if (section == null) {
                    throw new IllegalArgumentException("'" + path + "': '>>' sin ninguna seccion abierta");
                }
                data.put(section, sectionData);
                section = null;
            } else if (s.contains("::")) {
                int idx = s.indexOf("::");
                String clave = s.substring(0, idx).trim();
                String valor = s.substring(idx + 2).trim();
                (section != null ? sectionData : sueltos).put(clave, valor);
            } else {
                throw new IllegalArgumentException("'" + path + "': linea invalida: '" + s + "'");
            }
        }
        if (section != null) {
            throw new IllegalArgumentException(
                "'" + path + "': seccion '" + section + "' nunca se cerro con '>>'");
        }
        return data;
    }

    static void ImportConfig(String path) throws IOException {
        Map<String, Map<String, String>> data = parseConfig(path);
        for (String nombre : CONFIG_COLOR_SECTIONS) {
            Map<String, String> sect = data.get(nombre);
            if (sect == null) {
                continue;
            }
            Color actual = seccion(nombre);
            String color = sect.get("color");
            if (color == null || color.isEmpty()) {
                color = actual.color;
            }
            int level = actual.level;
            String lv = sect.get("level");
            if (lv != null && !lv.isEmpty()) {
                level = Integer.parseInt(lv);
            }
            ponerSeccion(nombre, new Color(color, level));
        }
        String font = data.get("").get("font");
        if (font != null && !font.isEmpty()) {
            SetStyle.Font(Integer.parseInt(font));
        }
        Map<String, String> w = data.get("welcome");
        if (w != null) {
            String text = vacioANull(w.get("text"));
            SetStyle.Welcome(
                text == null ? null : text.replace("\\n", "\n"),
                vacioANull(w.get("image")),
                enteroONull(w.get("width")),
                enteroONull(w.get("height")));
        }
    }

    private static String vacioANull(String v) {
        return v == null || v.isEmpty() ? null : v;
    }

    private static Integer enteroONull(String v) {
        return v == null || v.isEmpty() ? null : Integer.valueOf(v);
    }

    // =====================================================================
    //  Ayuda por linea de comandos
    // =====================================================================

    static void printHeader(String title, String subtitle) {
        banner(title, 0, "magenta", 2, 3, 1);
        int cols = Math.min(anchoTerminal(), 66);
        Color azul = new Color("blue", 1);
        Color cyan = new Color("cyan", 2);
        p(pintar("─".repeat(cols), azul));
        for (String line : subtitle.split("\n", -1)) {
            p(pintar(centrado(line, cols), cyan));
        }
        p(pintar("─".repeat(cols), azul));
        p();
    }

    static String stylePreview(int n) {
        Map<String, String> b = borde(n);
        if (b != null) {
            String h5 = hline(b.get("h"), 5);
            return b.get("tl") + h5 + b.get("tr") + "  " + b.get("v") + "     " + b.get("v")
                 + "  " + b.get("bl") + h5 + b.get("br");
        }
        return "#######  #     #  #######";
    }

    static void printStyleHelp() {
        Color magenta = new Color("magenta", 2);
        Color azul = new Color("blue", 1);
        Color amarillo = new Color("yellow", 2);
        p(pintar("Estilos de marco disponibles (style / bannerStyle, 1 al 20):", magenta));
        p(pintar("─".repeat(66), azul));
        for (int n = 1; n <= 20; n++) {
            p("  " + pintar(der(String.valueOf(n), 2), amarillo) + " -> " + stylePreview(n));
        }
        p();
        p("Se usan en: new GRmenu(..., style, ...), o en runtime con");
        p("  menu.style = N / menu.bannerStyle = N antes de menu.draw().");
    }

    static String fontPreview(int fontId) {
        List<String> rows = buildAsciiLines("GR", 200, fontId);
        return rows == null ? "(sin glifos para la muestra)" : rows.get(0);
    }

    static void printBannerHelp() {
        Color magenta = new Color("magenta", 2);
        Color azul = new Color("blue", 1);
        Color amarillo = new Color("yellow", 2);
        Color verde = new Color("green", 2);
        Color cyan = new Color("cyan", 1);
        p(pintar("Fuentes ASCII 3D del banner (font, 1 al 10):", magenta));
        p(pintar("─".repeat(66), azul));
        for (int n = 1; n <= 10; n++) {
            p("  " + pintar(der(String.valueOf(n), 2), amarillo) + " -> " + fontPreview(n));
        }
        p();
        p("Parametros relacionados con el banner:");
        p("  " + pintar(izq("banner", 14), verde) + " -> texto a renderizar en arte ASCII 3D.");
        p("  " + pintar(izq("bannerStyle", 14), verde) + " -> estilo de marco del banner (ver --Style).");
        p("  " + pintar(izq("font", 14), verde) + " -> fuente ASCII de arriba (1 al 10).");
        p("  " + pintar(izq("SetStyle.Banner(color, level)", 30), cyan) + " -> color del banner.");
        p("  " + pintar(izq("SetStyle.Font(fontId)", 30), cyan) + " -> fuente global por defecto.");
        p("  " + pintar(izq("GRmenu.banner(texto, ...)", 30), cyan) + " -> helper suelto, sin crear un menu.");
    }

    static void printDividerHelp() {
        Color magenta = new Color("magenta", 2);
        Color azul = new Color("blue", 1);
        Color verde = new Color("green", 2);
        Color cyan = new Color("cyan", 1);
        p(pintar("Parametro divider:", magenta));
        p(pintar("─".repeat(66), azul));
        p("Dibuja una linea divisoria arriba y abajo del subtitulo, junto al banner.");
        p();
        p("  " + pintar(izq("divider=null", 15), verde) + " -> (default) se activa solo si hay banner o subtitle.");
        p("  " + pintar(izq("divider=true", 15), verde) + " -> siempre se dibuja.");
        p("  " + pintar(izq("divider=false", 15), verde) + " -> nunca se dibuja.");
        p();
        p("  " + pintar(izq("SetStyle.Divider(color, level)", 30), cyan) + " -> color de las lineas (default: blue, 1).");
    }

    static void printAllHelp() {
        Color magenta = new Color("magenta", 2);
        Color azul = new Color("blue", 1);
        Color verde = new Color("green", 2);
        Color cyan = new Color("cyan", 1);
        Color blanco = new Color("white", 2);

        p(pintar("Parametros de new GRmenu(items, ...):", magenta));
        p(pintar("─".repeat(66), azul));
        String[][] params = {
            { "items", "opciones: new Opcion(nombre, accion) o GRSubMenu." },
            { "title", "titulo del recuadro de opciones." },
            { "style", "estilo de marco de opciones (1 al 20, default 19)." },
            { "banner", "texto grande en arte ASCII 3D." },
            { "subtitle", "subtitulo, soporta '\\n' para varias lineas." },
            { "bannerStyle", "estilo de marco del banner (1 al 20, default 3)." },
            { "font", "fuente ASCII del banner (1 al 10, default 1)." },
            { "divider", "lineas divisorias junto al banner/subtitle." },
            { "center", "centrado simetrico (default true)." },
            { "maxShowOptions", "cuantas opciones se ven a la vez (default 10)." },
            { "searchable", "habilita buscar con '/'." },
            { "animate", "null, \"linear\", \"fade\", \"diagonal\" o \"rgb\"." },
        };
        for (String[] fila : params) {
            p("  " + pintar(izq(fila[0], 16), verde) + " -> " + fila[1]);
        }
        p();
        printStyleHelp();
        p();
        printBannerHelp();
        p();
        printDividerHelp();
        p();
        p(pintar("Colores disponibles (GRmenu.COLORS()):", magenta));
        p(pintar("─".repeat(66), azul));
        StringBuilder nombres = new StringBuilder("  ");
        boolean primero = true;
        for (String c : COLORS().keySet()) {
            if (c.equals("reset")) {
                continue;
            }
            if (!primero) {
                nombres.append(", ");
            }
            nombres.append(pintar(c, new Color(c, 2)));
            primero = false;
        }
        p(nombres.toString());
        p("  Brillo: 1 = normal, 2 = brillante.");
        p();
        p(pintar("Metodos de SetStyle:", magenta));
        p(pintar("─".repeat(66), azul));
        String[][] metodos = {
            { "SetStyle.Border(color, level)", "color y brillo del marco de opciones." },
            { "SetStyle.Options(color, level)", "color y brillo de opciones no activas." },
            { "SetStyle.Focus(color, level)", "color y brillo de la opcion resaltada." },
            { "SetStyle.Title(color, level)", "color y brillo del titulo." },
            { "SetStyle.Banner(color, level)", "color y brillo del banner." },
            { "SetStyle.Subtitle(color, level)", "color y brillo del subtitulo." },
            { "SetStyle.Divider(color, level)", "color y brillo de las lineas divisorias." },
            { "SetStyle.Font(fontId)", "fuente ASCII global del banner (1 al 10)." },
            { "SetStyle.Welcome(text, image, w, h)", "contenido de la pantalla de bienvenida." },
        };
        for (String[] fila : metodos) {
            p("  " + pintar(izq(fila[0], 38), cyan) + " -> " + fila[1]);
        }
        p();
        p(pintar("Ejecucion:", magenta));
        p(pintar("─".repeat(66), azul));
        p("  " + pintar(izq("menu.draw(sizeMax)", 24), blanco) + " -> arranca el menu (flechas, Enter, q).");
        p();
    }

    static void printCliHelp() {
        p("Uso: java GRmenu.java [opcion]");
        p();
        p("  -h, --help      Muestra esta ayuda.");
        p("  -a, --All       Guia completa (estilos, fuentes, colores, parametros).");
        p("  -s, --Style     Estilos de marco disponibles (1 al 20).");
        p("  -b, --Banner    Fuentes del banner (1 al 10) y sus parametros.");
        p("  -d, --Divider   Explica el parametro divider.");
        p();
        p("El ejemplo de uso esta en e.java: java e.java");
    }

    public static void main(String[] args) {
        String arg = args.length > 0 ? args[0] : "";
        switch (arg) {
            case "-a", "--All" -> {
                printHeader("GRMENU", "Guia y Referencia Rapida\nNavegacion interactiva en terminal TTY");
                printAllHelp();
            }
            case "-s", "--Style" -> {
                printHeader("STYLE", "Estilos de marco disponibles\n(style / bannerStyle, 1 al 20)");
                printStyleHelp();
            }
            case "-b", "--Banner" -> {
                printHeader("BANNER", "Fuentes ASCII 3D del banner\n(font, 1 al 10)");
                printBannerHelp();
            }
            case "-d", "--Divider" -> {
                printHeader("DIVIDER", "Lineas divisorias junto al banner y subtitulo");
                printDividerHelp();
            }
            default -> {
                printHeader("GRMENU", "Ayuda de linea de comandos");
                printCliHelp();
            }
        }
    }
}
