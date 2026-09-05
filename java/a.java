// ===========================================================================
//  a.java - sonda de teclado
//
//  Pone la terminal en modo crudo, imprime el codigo de cada tecla que
//  apretas, y sale con q dejando la terminal como estaba.
//
//  No es parte de la libreria: es para ver con tus propios ojos que una
//  flecha no es una tecla, son tres bytes.
//
//  Se corre con:  java a.java
// ===========================================================================

class a {

    // La configuracion que tenia la terminal antes de que la tocaramos.
    // Se guarda aca para poder devolverla al final.
    static String configOriginal;


    public static void main(String[] args) throws Exception {

        modoCrudo();

        p("Modo crudo activado. Apreta teclas.");
        p("Las flechas salen como tres numeros. q para salir.");
        p("");

        while (true) {

            int b = System.in.read();

            // -1 = se cerro la entrada (EOF). Va PRIMERO: si no, -1 nunca
            // coincide con 'q' y el bucle no termina jamas.
            if (b == -1) {
                p("EOF -> se cerro la entrada");
                break;
            }

            // 27 = ESC. No es una tecla: es el arranque de una secuencia.
            // Detras vienen dos bytes mas: '[' y la letra de la flecha.
            //
            // OJO: si apretas ESC de verdad (sin flecha) el programa se
            // queda esperando esos dos bytes que nunca llegan. Se arregla,
            // pero no ahora.
            if (b == 27) {
                int corchete = System.in.read();
                int letra = System.in.read();
                p("FLECHA -> " + b + " " + corchete + " " + letra
                  + "   " + nombreFlecha(letra));
                continue;
            }

            p("TECLA  -> " + b + "   " + describir(b));

            if (b == 'q') {
                break;
            }
        }

        // Sin esto la terminal queda en modo crudo y hay que cerrarla.
        restaurar();

        // Aca ya no hace falta el "\r\n": la terminal volvio a lo normal.
        System.out.println("Terminal restaurada.");
    }

    // =====================================================================
    //  Modo crudo
    // =====================================================================
    //  Java no tiene termios como Python. Hay que pedirle el cambio al
    //  programa `stty` del sistema.

    static void modoCrudo() throws Exception {
        // "stty -g" imprime toda la configuracion actual en una sola linea.
        configOriginal = stty(new String[]{ "-g" });

        // "raw"    -> cada tecla llega al instante, sin esperar el Enter
        // "-echo"  -> lo que apretas no se muestra en pantalla
        stty(new String[]{ "raw", "-echo" });
    }


    static void restaurar() throws Exception {
        if (configOriginal != null) {
            // La linea que guardo "stty -g" se le pasa de vuelta tal cual.
            stty(new String[]{ configOriginal });
        }
    }


    // Lanza el comando `stty` y devuelve lo que haya impreso.
    static String stty(String[] argumentos) throws Exception {

        // ProcessBuilder recibe el comando y sus argumentos por separado.
        // Como el nombre del programa va primero, se arma un arreglo con
        // "stty" adelante y lo demas atras.
        String[] comando = new String[argumentos.length + 1];
        comando[0] = "stty";
        for (int i = 0; i < argumentos.length; i++) {
            comando[i + 1] = argumentos[i];
        }

        ProcessBuilder pb = new ProcessBuilder(comando);

        // ESTA LINEA ES LA CLAVE.
        // stty modifica la terminal que tenga en su entrada. Si no le
        // pasamos la nuestra, recibe una tuberia, y una tuberia no es una
        // terminal: falla con "ioctl no apropiada para el dispositivo" y
        // sale con codigo 1.
        //
        // El problema es que ese error pasa desapercibido: se va al
        // getErrorStream() del hijo, que nadie lee, y el codigo de salida
        // tampoco se mira. El programa sigue como si nada, con la terminal
        // sin cambiar.
        pb.redirectInput(ProcessBuilder.Redirect.INHERIT);

        Process proceso = pb.start();

        // Lo que stty haya impreso (solo "stty -g" imprime algo).
        String salida = new String(proceso.getInputStream().readAllBytes());

        // Esperar a que termine antes de seguir. Si no, podriamos empezar
        // a leer teclas antes de que el modo crudo este puesto.
        proceso.waitFor();

        return salida.trim();
    }


    // =====================================================================
    //  Ayudas para mostrar lo leido
    // =====================================================================

    static String nombreFlecha(int letra) {
        return switch (letra) {
            case 65 -> "(arriba)";
            case 66 -> "(abajo)";
            case 67 -> "(derecha)";
            case 68 -> "(izquierda)";
            default -> "(otra secuencia)";
        };
    }


    static String describir(int b) {
        if (b == 13) {
            return "= Enter. Es \\r, no \\n: en modo crudo la terminal ya no traduce";
        }
        if (b == 9) {
            return "= Tab";
        }
        if (b == 127) {
            return "= Backspace";
        }
        if (b == 32) {
            return "= espacio";
        }
        if (b < 32) {
            return "= caracter de control";
        }
        // (char) toma el numero y lo convierte en el caracter que representa:
        // 113 -> 'q'
        return "= '" + (char) b + "'";
    }


    // =====================================================================
    //  Impresion
    // =====================================================================

    // En modo crudo la terminal deja de traducir el "\n". El cursor baja
    // una linea pero NO vuelve al margen izquierdo, asi que el texto sale
    // en escalera. Hay que mandar "\r" (volver al margen) y "\n" (bajar).
    static void p(String texto) {
        System.out.print(texto + "\r\n");
    }
}
