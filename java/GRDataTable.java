import java.util.ArrayList;
import java.util.List;
import java.util.Map;

// ===========================================================================
//  GRDataTable - un GRmenu cuyas filas se dibujan en columnas alineadas.
//
//  Cada opcion se crea con celdas en vez de un nombre suelto:
//
//      new Opcion(new String[]{ "Ana", "31", "Cordoba" }, accion)
//
//  Una opcion normal (con nombre suelto) tambien vale: se dibuja como una
//  fila comun, sin partir en columnas.
// ===========================================================================

class GRDataTable extends GRmenu {

    GRDataTable(Item[] items, String[] columns) throws Exception {
        this(items, columns, null, "", 19, "", "", 3, null, true, null, 10, false, null);
    }

    GRDataTable(Item[] items, String[] columns, char[] colAlign, String title) throws Exception {
        this(items, columns, colAlign, title, 19, "", "", 3, null, true, null, 10, false, null);
    }

    GRDataTable(Item[] items, String[] columns, char[] colAlign, String title, int style,
                String banner, String subtitle, int bannerStyle, Boolean divider,
                boolean center, Integer font, Integer maxShowOptions,
                boolean searchable, String animate) throws Exception {

        super(items, title, style, banner, subtitle, bannerStyle, divider, center,
              font, maxShowOptions, searchable, animate);

        if (colAlign != null && colAlign.length != columns.length) {
            throw new IllegalArgumentException(
                "colAlign debe tener la misma cantidad de elementos que columns");
        }
        raiz.columns = columns;
        raiz.colAlign = colAlign != null ? colAlign : alineacionPorDefecto(columns.length);
    }

    static char[] alineacionPorDefecto(int n) {
        char[] a = new char[n];
        for (int i = 0; i < n; i++) {
            a[i] = 'l';
        }
        return a;
    }

    // Submenu con sus propias columnas.
    static GRSubMenu SubTable(String nombre, Item[] items, String[] columns, char[] colAlign) {
        if (colAlign != null && colAlign.length != columns.length) {
            throw new IllegalArgumentException(
                "colAlign debe tener la misma cantidad de elementos que columns");
        }
        GRSubMenu sub = new GRSubMenu(nombre, items);
        sub.columns = columns;
        sub.colAlign = colAlign != null ? colAlign : alineacionPorDefecto(columns.length);
        return sub;
    }

    static GRSubMenu SubTable(String nombre, Item[] items, String[] columns) {
        return SubTable(nombre, items, columns, null);
    }

    static String pad(String texto, int ancho, char alineacion) {
        if (alineacion == 'r') {
            return der(texto, ancho);
        }
        if (alineacion == 'c') {
            return centrado(texto, ancho);
        }
        return izq(texto, ancho);
    }

    @Override
    Panel renderOptionPanel(Nodo node, int sizeMax, int estilo, boolean focused) {
        String[] columns = node.columns;
        if (columns == null || columns.length == 0) {
            return super.renderOptionPanel(node, sizeMax, estilo, focused);
        }
        char[] align = node.colAlign != null ? node.colAlign : alineacionPorDefecto(columns.length);

        // Celdas de cada fila (null = fila comun, sin columnas).
        List<String[]> rowsCells = new ArrayList<>();
        for (Item it : node.items) {
            String[] celdas = it.celdas();
            if (celdas == null) {
                rowsCells.add(null);
            } else {
                String[] fijas = new String[columns.length];
                for (int j = 0; j < columns.length; j++) {
                    fijas[j] = j < celdas.length ? celdas[j] : "";
                }
                rowsCells.add(fijas);
            }
        }

        int[] colWidths = new int[columns.length];
        for (int j = 0; j < columns.length; j++) {
            colWidths[j] = columns[j].length();
        }
        for (String[] celdas : rowsCells) {
            if (celdas == null) {
                continue;
            }
            for (int j = 0; j < columns.length; j++) {
                colWidths[j] = Math.max(colWidths[j], celdas[j].length());
            }
        }

        String sep = " │ ";
        StringBuilder cabecera = new StringBuilder();
        for (int j = 0; j < columns.length; j++) {
            if (j > 0) {
                cabecera.append(sep);
            }
            cabecera.append(pad(columns[j], colWidths[j], align[j]));
        }
        String headerLine = cabecera.toString();

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

        int width = Math.max(sizeMax, headerLine.length() + 8);
        for (int i = 0; i < rowsCells.size(); i++) {
            if (rowsCells.get(i) == null) {
                width = Math.max(width, node.items[i].nombre().length() + 8);
            }
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
            lines.add(vL + " " + pintar(izq(headerLine, width - 4), tc) + " " + vR);
            targets.add(null);
            lines.add(pintarAnim(b.get("v") + linea + b.get("v"), bc, lines.size(), 0));
            targets.add(null);
            if (window.isEmpty()) {
                lines.add(vL + " " + pintar(izq("(sin coincidencias)", width - 4), oc) + " " + vR);
                targets.add(null);
            }
            for (int i : window) {
                String texto = filaTexto(node, rowsCells.get(i), i, colWidths, align, sep);
                if (marcas.contains(i)) {
                    Color color = node.index == i ? (focused ? fc : oc) : oc;
                    lines.add(vL + " " + pintar("[x] " + izq(texto, width - 8), color) + " " + vR);
                } else if (node.index == i) {
                    lines.add(vL + "  " + pintar(">" + izq(texto, width - 6), focused ? fc : oc) + " " + vR);
                } else {
                    lines.add(vL + " " + pintar("> " + izq(texto, width - 6), oc) + " " + vR);
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
            lines.add(lado + " " + pintar(izq(headerLine, width - 4), tc) + " " + lado);
            targets.add(null);
            lines.add(barra);
            targets.add(null);
            if (window.isEmpty()) {
                lines.add(lado + " " + pintar(izq("(sin coincidencias)", width - 4), oc) + " " + lado);
                targets.add(null);
            }
            for (int i : window) {
                String texto = filaTexto(node, rowsCells.get(i), i, colWidths, align, sep);
                Color color = node.index == i ? (focused ? fc : oc) : oc;
                String contenido = marcas.contains(i) ? "[x] " + texto : texto;
                lines.add(lado + " " + pintar(izq(contenido, width - 4), color) + " " + lado);
                targets.add(i);
            }
            lines.add(barra);
            targets.add(null);
        }

        agregarPie(node, lines, targets, width, truncated, filtered, total, marcas, dc);
        return new Panel(node, width, lines, targets);
    }

    private String filaTexto(Nodo node, String[] celdas, int i,
                             int[] colWidths, char[] align, String sep) {
        if (celdas == null) {
            return node.items[i].nombre();
        }
        StringBuilder sb = new StringBuilder();
        for (int j = 0; j < celdas.length; j++) {
            if (j > 0) {
                sb.append(sep);
            }
            sb.append(pad(celdas[j], colWidths[j], align[j]));
        }
        return sb.toString();
    }
}
