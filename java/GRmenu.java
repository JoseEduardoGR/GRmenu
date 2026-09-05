// ===========================================================================
//  GRmenu 1.0.0 en Java
//  Port de la primera version de Python: java/referencia_1.0.0.py
//
//  Se corre con:  java e.java
//  Flechas arriba/abajo para moverse, Enter para ejecutar, q para salir.
// ===========================================================================

class GRmenu {

    // --- Secuencias ANSI -------------------------------------------------
    // Java no acepta \x1b. El mismo caracter se escribe \u001b.
    static final String LIMPIAR = "\u001b[H\u001b[2J\u001b[3J";
    static final String RESET   = "\u001b[0m";

    // --- Codigos internos para las flechas -------------------------------
    // Una flecha no es un caracter: la terminal manda 3 bytes. Como
    // leerTecla() devuelve un int, uso negativos para que nunca choquen
    // con un caracter real.
    static final int ARRIBA = -1;
    static final int ABAJO  = -2;
    static final int OTRA   = -3;

    // --- Estilo global (el SetStyle de Python) ---------------------------
    static Color colorBorde  = new Color("cyan", 1);
    static Color colorOpcion = new Color("white", 1);
    static Color colorFoco   = new Color("green", 2);

    static void setBorde(String color, int nivel)  { colorBorde  = new Color(color, nivel); }
    static void setOpcion(String color, int nivel) { colorOpcion = new Color(color, nivel); }
    static void setFoco(String color, int nivel)   { colorFoco   = new Color(color, nivel); }

    // --- Estado del menu -------------------------------------------------
    Opcion[] opciones;
    String titulo;
    int estilo;
    int index = 0;
    String sttyOriginal;

    GRmenu(Opcion[] opciones, String titulo, int estilo) throws Exception {
        this.opciones = opciones;
        this.titulo = titulo;
        this.estilo = estilo;
        modoCrudo();
    }

    // =====================================================================
    //  Impresion
    // =====================================================================

    // Equivale a GRprint de Python. En modo crudo la terminal ya no
    // traduce "\n": el cursor baja una linea pero NO vuelve al margen
    // izquierdo. Hay que mandar "\r\n" a mano o el recuadro sale en
    // escalera.
    static void p(String texto) {
        System.out.print(texto + "\r\n");
    }

    // =====================================================================
    //  Terminal en modo crudo
    // =====================================================================
    //  Aca esta la diferencia grande con Python. Python tiene termios y
    //  tty.setraw en su biblioteca estandar. Java no tiene nada de eso, asi
    //  que hay que pedirselo al programa `stty` del sistema.

    void modoCrudo() throws Exception {
        sttyOriginal = stty(new String[]{ "-g" });        // guarda la config actual
        stty(new String[]{ "raw", "-echo" });             // sin buffer de linea, sin eco
    }

    void restaurarTerminal() throws Exception {
        if (sttyOriginal != null) {
            stty(new String[]{ sttyOriginal });
        }
    }

    // Lanza el comando `stty` y devuelve lo que haya impreso.
    static String stty(String[] argumentos) throws Exception {
        String[] comando = new String[argumentos.length + 1];
        comando[0] = "stty";
        for (int i = 0; i < argumentos.length; i++) {
            comando[i + 1] = argumentos[i];
        }

        ProcessBuilder pb = new ProcessBuilder(comando);
        // stty tiene que hablar con la terminal de verdad, no con una
        // tuberia: por eso hereda la entrada de este programa.
        pb.redirectInput(ProcessBuilder.Redirect.INHERIT);

        Process proceso = pb.start();
        String salida = new String(proceso.getInputStream().readAllBytes());
        proceso.waitFor();
        return salida.trim();
    }

    // =====================================================================
    //  Teclado
    // =====================================================================

    // Python leia 3 bytes de un saque con os.read(fd, 3). Aca se leen de a
    // uno: una flecha llega como 27, '[', y despues 'A' o 'B'.
    static int leerTecla() throws Exception {
        int b = System.in.read();

        // -1 significa que la entrada se cerro (EOF). Hay que atenderlo
        // ANTES que nada por dos razones: si no, el menu se redibuja para
        // siempre porque -1 nunca es 'q', y ademas -1 es el mismo numero
        // que ARRIBA. Se trata como si hubieras apretado q.
        if (b == -1) {
            return 'q';
        }

        if (b != 27) {
            return b;                 // tecla normal: 'q', Enter, una letra
        }
        System.in.read();             // se salta el '['
        int flecha = System.in.read();
        if (flecha == 'A') return ARRIBA;
        if (flecha == 'B') return ABAJO;
        return OTRA;                  // izquierda / derecha
    }

    // OJO: en Java el % de un negativo da negativo. En Python no.
    //   Python:  (0 - 1) % 5  ->  4
    //   Java:    (0 - 1) % 5  -> -1
    // Por eso hay que sumar el largo antes de sacar el resto.
    void subir() {
        index = (index - 1 + opciones.length) % opciones.length;
    }

    void bajar() {
        index = (index + 1) % opciones.length;
    }

    // =====================================================================
    //  Colores
    // =====================================================================

    // El diccionario COLORS de Python. Los codigos ANSI ya traen la regla
    // adentro: el brillante siempre es el normal mas 60 (rojo 31 -> 91),
    // asi que con guardar un nivel alcanza.
    static int codigoColor(String nombre) {
        return switch (nombre) {
            case "black"   -> 30;
            case "red"     -> 31;
            case "green"   -> 32;
            case "yellow"  -> 33;
            case "blue"    -> 34;
            case "magenta" -> 35;
            case "cyan"    -> 36;
            case "white"   -> 37;
            default        -> -1;
        };
    }

    // El _colorize de Python.
    static String pintar(String texto, Color color) {
        if (color == null) {
            return texto;
        }
        int codigo = codigoColor(color.nombre);
        if (codigo < 0) {
            return texto;
        }
        if (color.nivel == 2) {
            codigo = codigo + 60;
        }
        return "\u001b[" + codigo + "m" + texto + RESET;
    }

    // =====================================================================
    //  Bordes
    // =====================================================================

    // El diccionario BORDERS de Python. Devuelve null si el estilo no esta
    // aca, igual que el .get() de Python devolvia None.
    static Borde bordes(int estilo) {
        return switch (estilo) {
            case 1  -> new Borde("=-", "|", "#", "#", "#", "#");
            case 2  -> new Borde("─",  "│", "┌", "┐", "└", "┘");
            case 3  -> new Borde("═",  "║", "╔", "╗", "╚", "╝");
            case 4  -> new Borde("━",  "┃", "┏", "┓", "┗", "┛");
            case 5  -> new Borde("═",  "│", "╒", "╕", "╘", "╛");
            case 6  -> new Borde("─",  "║", "╓", "╖", "╙", "╜");
            case 7  -> new Borde("─",  "│", "╭", "╮", "╰", "╯");
            case 8  -> new Borde("▀",  "▌", "▛", "▜", "▙", "▟");
            case 19 -> new Borde("●○", "●", "●", "●", "●", "●");
            case 20 -> new Borde("★☆", "★", "★", "★", "★", "★");
            default -> null;
        };
    }

    // El diccionario STYLES: un solo caracter para todo el recuadro.
    static String estiloSimple(int estilo) {
        return switch (estilo) {
            case 9  -> "▓";
            case 10 -> "▒";
            case 11 -> "░";
            case 12 -> "█";
            case 13 -> "*";
            case 14 -> "+";
            case 15 -> "=";
            case 16 -> "~";
            case 17 -> "-";
            case 18 -> "◆";
            default -> "#";
        };
    }

    // =====================================================================
    //  Ayudas de texto
    // =====================================================================
    //  Python trae center() y ljust() de fabrica. Java no: se escriben.

    // El _hline de Python: repite el patron y corta al ancho justo.
    //   Python: (h * (ancho // len(h) + 1))[:ancho]
    static String linea(String h, int ancho) {
        if (ancho <= 0) {
            return "";
        }
        return h.repeat(ancho / h.length() + 1).substring(0, ancho);
    }

    // texto.ljust(ancho)
    static String izquierda(String texto, int ancho) {
        if (texto.length() >= ancho) {
            return texto;
        }
        return texto + " ".repeat(ancho - texto.length());
    }

    // texto.center(ancho)
    static String centrar(String texto, int ancho) {
        if (texto.length() >= ancho) {
            return texto;
        }
        int sobra = ancho - texto.length();
        int izq = sobra / 2;
        return " ".repeat(izq) + texto + " ".repeat(sobra - izq);
    }

    // =====================================================================
    //  Dibujo
    // =====================================================================

    void menu() {
        p("Press any key to start ...");
    }

    void dibujarCaja(int anchoMin) {
        // El ancho lo manda la opcion mas larga (o el titulo).
        int ancho = anchoMin;
        for (int i = 0; i < opciones.length; i++) {
            int necesario = opciones[i].nombre().length() + 4;
            if (necesario > ancho) {
                ancho = necesario;
            }
        }
        if (!titulo.isEmpty() && titulo.length() + 4 > ancho) {
            ancho = titulo.length() + 4;
        }

        Borde b = bordes(estilo);

        if (b != null) {
            String l = linea(b.h, ancho - 2);
            String v = pintar(b.v, colorBorde);

            p(pintar(b.tl + l + b.tr, colorBorde));

            if (!titulo.isEmpty()) {
                p(v + " " + centrar(titulo, ancho - 4) + " " + v);
                p(pintar(b.v + l + b.v, colorBorde));
            }

            for (int i = 0; i < opciones.length; i++) {
                String nombre = opciones[i].nombre();
                if (i == index) {
                    p(v + "  " + pintar(">" + izquierda(nombre, ancho - 6), colorFoco) + " " + v);
                } else {
                    p(v + " " + pintar("> " + izquierda(nombre, ancho - 6), colorOpcion) + " " + v);
                }
            }

            p(pintar(b.bl + l + b.br, colorBorde));

        } else {
            String s = estiloSimple(estilo);
            String barra = pintar(s.repeat(ancho), colorBorde);
            String lado = pintar(s, colorBorde);

            p(barra);
            if (!titulo.isEmpty()) {
                p(lado + " " + centrar(titulo, ancho - 4) + " " + lado);
                p(barra);
            }
            for (int i = 0; i < opciones.length; i++) {
                String nombre = izquierda(opciones[i].nombre(), ancho - 4);
                if (i == index) {
                    p(lado + " " + pintar(nombre, colorFoco) + " " + lado);
                } else {
                    p(lado + " " + pintar(nombre, colorOpcion) + " " + lado);
                }
            }
            p(barra);
        }
    }

    void draw(int anchoMin) throws Exception {
        menu();

        while (true) {
            int tecla = leerTecla();

            if (tecla == 'q') {
                break;
            }

            System.out.print(LIMPIAR);

            if (tecla == ARRIBA) subir();
            if (tecla == ABAJO)  bajar();

            dibujarCaja(anchoMin);

            if (tecla == '\r') {
                restaurarTerminal();
                p(LIMPIAR);
                opciones[index].ejecutar();
                return;
            }
        }

        // Tu version de Python NO hace esto al salir con 'q': la terminal
        // queda en modo crudo y hay que cerrarla. Es un bug del original.
        restaurarTerminal();
    }



    // ===========================================================================
    //  Una opcion del menu.
    //
    //  En Python la lista era de funciones sueltas, porque una funcion en Python
    //  es un valor que se puede guardar en una lista. En Java no: una funcion no
    //  vive sola, vive dentro de un objeto. Asi que el contrato es una interfaz,
    //  y cada opcion es una clase que la implementa.
    // ===========================================================================
    interface Opcion {
        String nombre();
        void ejecutar();
    }

    // --- Un color de la paleta: nombre + nivel (1 normal, 2 brillante) ---------
    static class Color {
        String nombre;
        int nivel;

        Color(String nombre, int nivel) {
            this.nombre = nombre;
            this.nivel = nivel;
        }
    }

    // --- Las 6 piezas con las que se dibuja un recuadro ------------------------
    //  En Python era dict(h=..., v=..., tl=...). Aca es una clase: los nombres
    //  de los campos quedan fijos y el compilador te avisa si escribis "tl" mal.
    static class Borde {
        String h, v, tl, tr, bl, br;

        Borde(String h, String v, String tl, String tr, String bl, String br) {
            this.h = h;
            this.v = v;
            this.tl = tl;
            this.tr = tr;
            this.bl = bl;
            this.br = br;
        }
    }
}
