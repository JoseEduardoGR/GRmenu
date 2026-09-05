import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

// ===========================================================================
//  Json - lector minimo de JSON
//
//  Python trae json en su biblioteca estandar. Java no trae ninguno: hay que
//  usar una libreria externa (Jackson, Gson) o escribirlo. Como GRmenu se
//  corre con "java e.java" sin Maven ni Gradle, esta escrito aca.
//
//  Solo lee (no escribe), que es todo lo que la libreria necesita para
//  data/colors.json, data/borders.json y data/fonts.json.
//
//  Lo que devuelve segun lo que encuentre:
//      objeto   -> Map<String, Object>
//      arreglo  -> List<Object>
//      texto    -> String
//      numero   -> Double
//      booleano -> Boolean
//      null     -> null
// ===========================================================================

class Json {

    private final String texto;
    private int pos;

    private Json(String texto) {
        this.texto = texto;
        this.pos = 0;
    }

    // --- Entrada publica -------------------------------------------------

    static Object parse(String texto) {
        Json j = new Json(texto);
        j.saltarEspacios();
        Object valor = j.valor();
        j.saltarEspacios();
        if (j.pos < j.texto.length()) {
            throw new RuntimeException("JSON: sobra texto en la posicion " + j.pos);
        }
        return valor;
    }

    @SuppressWarnings("unchecked")
    static Map<String, Object> parseObjeto(String texto) {
        Object o = parse(texto);
        if (!(o instanceof Map)) {
            throw new RuntimeException("JSON: se esperaba un objeto");
        }
        return (Map<String, Object>) o;
    }

    // --- Analisis --------------------------------------------------------

    private Object valor() {
        saltarEspacios();
        if (pos >= texto.length()) {
            throw new RuntimeException("JSON: se corto el texto");
        }
        char c = texto.charAt(pos);
        if (c == '{') return objeto();
        if (c == '[') return arreglo();
        if (c == '"') return cadena();
        if (c == 't' || c == 'f') return booleano();
        if (c == 'n') return nulo();
        return numero();
    }

    private Map<String, Object> objeto() {
        // LinkedHashMap conserva el orden en que vinieron las claves, que es
        // el que se usa para listar los colores en la ayuda.
        Map<String, Object> mapa = new LinkedHashMap<>();
        esperar('{');
        saltarEspacios();
        if (mirar() == '}') {
            pos++;
            return mapa;
        }
        while (true) {
            saltarEspacios();
            String clave = cadena();
            saltarEspacios();
            esperar(':');
            mapa.put(clave, valor());
            saltarEspacios();
            char c = mirar();
            if (c == ',') {
                pos++;
                continue;
            }
            esperar('}');
            return mapa;
        }
    }

    private List<Object> arreglo() {
        List<Object> lista = new ArrayList<>();
        esperar('[');
        saltarEspacios();
        if (mirar() == ']') {
            pos++;
            return lista;
        }
        while (true) {
            lista.add(valor());
            saltarEspacios();
            char c = mirar();
            if (c == ',') {
                pos++;
                continue;
            }
            esperar(']');
            return lista;
        }
    }

    private String cadena() {
        esperar('"');
        StringBuilder sb = new StringBuilder();
        while (true) {
            if (pos >= texto.length()) {
                throw new RuntimeException("JSON: cadena sin cerrar");
            }
            char c = texto.charAt(pos++);
            if (c == '"') {
                return sb.toString();
            }
            if (c != '\\') {
                sb.append(c);
                continue;
            }
            char e = texto.charAt(pos++);
            switch (e) {
                case '"'  -> sb.append('"');
                case '\\' -> sb.append('\\');
                case '/'  -> sb.append('/');
                case 'b'  -> sb.append('\b');
                case 'f'  -> sb.append('\f');
                case 'n'  -> sb.append('\n');
                case 'r'  -> sb.append('\r');
                case 't'  -> sb.append('\t');
                case 'u'  -> {
                    sb.append((char) Integer.parseInt(texto.substring(pos, pos + 4), 16));
                    pos += 4;
                }
                default -> throw new RuntimeException("JSON: escape desconocido \\" + e);
            }
        }
    }

    private Double numero() {
        int ini = pos;
        while (pos < texto.length() && "+-0123456789.eE".indexOf(texto.charAt(pos)) >= 0) {
            pos++;
        }
        if (ini == pos) {
            throw new RuntimeException("JSON: se esperaba un numero en la posicion " + pos);
        }
        return Double.valueOf(texto.substring(ini, pos));
    }

    private Boolean booleano() {
        if (texto.startsWith("true", pos)) {
            pos += 4;
            return Boolean.TRUE;
        }
        if (texto.startsWith("false", pos)) {
            pos += 5;
            return Boolean.FALSE;
        }
        throw new RuntimeException("JSON: se esperaba true o false");
    }

    private Object nulo() {
        if (texto.startsWith("null", pos)) {
            pos += 4;
            return null;
        }
        throw new RuntimeException("JSON: se esperaba null");
    }

    // --- Ayudas ----------------------------------------------------------

    private void saltarEspacios() {
        while (pos < texto.length() && Character.isWhitespace(texto.charAt(pos))) {
            pos++;
        }
    }

    private char mirar() {
        if (pos >= texto.length()) {
            throw new RuntimeException("JSON: se corto el texto");
        }
        return texto.charAt(pos);
    }

    private void esperar(char c) {
        saltarEspacios();
        if (mirar() != c) {
            throw new RuntimeException("JSON: se esperaba '" + c + "' y vino '" + mirar()
                                       + "' en la posicion " + pos);
        }
        pos++;
    }
}
