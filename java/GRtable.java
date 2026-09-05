import java.util.ArrayList;
import java.util.List;
import java.util.Map;

// ===========================================================================
//  GRtable - una grilla de dos dimensiones que se recorre con las cuatro
//  flechas, en vez de una lista vertical.
//
//  Cada celda es una Opcion o null (hueco). Las flechas saltan los huecos.
// ===========================================================================

class GRtable extends GRmenu {

    Item[][] grid;
    String[] columns;
    char[] colAlign;
    Integer maxShowRows;

    int row;
    int col;

    private List<int[]> cellRegions = new ArrayList<>();

    GRtable(Item[][] grid) throws Exception {
        this(grid, null, null, null, "", 19, "", "", 3, null, true, null, null);
    }

    GRtable(Item[][] grid, String[] columns, String title) throws Exception {
        this(grid, columns, null, null, title, 19, "", "", 3, null, true, null, null);
    }

    GRtable(Item[][] grid, String[] columns, char[] colAlign, Integer maxShowRows,
            String title, int style, String banner, String subtitle, int bannerStyle,
            Boolean divider, boolean center, Integer font, String animate) throws Exception {

        super(new Item[0], title, style, banner, subtitle, bannerStyle, divider, center,
              font, null, false, animate);

        int ncols = 0;
        for (Item[] fila : grid) {
            ncols = Math.max(ncols, fila.length);
        }
        if (columns != null) {
            ncols = Math.max(ncols, columns.length);
        }
        if (colAlign != null && columns != null && colAlign.length != columns.length) {
            throw new IllegalArgumentException(
                "colAlign debe tener la misma cantidad de elementos que columns");
        }

        // Rellena las filas cortas con huecos para que todas midan igual.
        this.grid = new Item[grid.length][ncols];
        for (int r = 0; r < grid.length; r++) {
            for (int c = 0; c < ncols; c++) {
                this.grid[r][c] = c < grid[r].length ? grid[r][c] : null;
            }
        }
        this.columns = columns;
        this.colAlign = colAlign != null ? colAlign : GRDataTable.alineacionPorDefecto(ncols);
        this.maxShowRows = maxShowRows;

        irACeldaMasCercana();
        // El tamaño de la terminal se recalcula aca: cuando lo hizo el
        // constructor de arriba, la grilla todavia no existia.
        asegurarTamanoTerminal();
    }

    private void irACeldaMasCercana() {
        for (int r = 0; r < grid.length; r++) {
            for (int c = 0; c < grid[r].length; c++) {
                if (grid[r][c] != null) {
                    row = r;
                    col = c;
                    return;
                }
            }
        }
    }

    private void mover(int dRow, int dCol) {
        if (grid.length == 0 || grid[0].length == 0) {
            return;
        }
        if (dRow != 0) {
            int nrows = grid.length;
            int r = row;
            for (int i = 0; i < nrows; i++) {
                r = ((r + dRow) % nrows + nrows) % nrows;
                if (grid[r][col] != null) {
                    row = r;
                    return;
                }
            }
        } else {
            int ncols = grid[row].length;
            int c = col;
            for (int i = 0; i < ncols; i++) {
                c = ((c + dCol) % ncols + ncols) % ncols;
                if (grid[row][c] != null) {
                    col = c;
                    return;
                }
            }
        }
    }

    private void ajustarScrollFilas() {
        Integer limit = maxShowRows;
        int total = grid.length;
        if (limit == null || limit <= 0 || limit >= total) {
            raiz.scroll = 0;
            return;
        }
        if (row < raiz.scroll) {
            raiz.scroll = row;
        } else if (row >= raiz.scroll + limit) {
            raiz.scroll = row - limit + 1;
        }
        raiz.scroll = Math.max(0, Math.min(raiz.scroll, total - limit));
    }

    private int[] anchoColumnas() {
        int ncols = grid.length > 0 ? grid[0].length : (columns != null ? columns.length : 0);
        int[] widths = new int[ncols];
        for (int j = 0; j < ncols; j++) {
            widths[j] = columns != null && j < columns.length ? columns[j].length() : 0;
        }
        for (Item[] fila : grid) {
            for (int j = 0; j < fila.length; j++) {
                if (fila[j] != null) {
                    widths[j] = Math.max(widths[j], fila[j].nombre().length());
                }
            }
        }
        return widths;
    }

    @Override
    int[] estimarTamano() {
        if (grid == null) {
            return super.estimarTamano();
        }
        int[] colW = anchoColumnas();
        int contentW = 0;
        for (int w : colW) {
            contentW += w;
        }
        contentW += 2 * Math.max(0, colW.length - 1);

        int width = Math.max(20, contentW + 8);
        if (!raiz.title.isEmpty()) {
            width = Math.max(width, raiz.title.length() + 4);
        }
        int limite = maxShowRows == null ? grid.length : maxShowRows;
        int visibles = Math.min(grid.length, limite);
        int height = 2 + (raiz.title.isEmpty() ? 0 : 1) + (columns != null ? 2 : 0) + visibles + 2;

        if (!banner.isEmpty()) {
            List<String> rows = buildAsciiLines(banner, 999, SetStyle.font);
            if (rows != null) {
                int max = 0;
                for (String r : rows) {
                    max = Math.max(max, r.length());
                }
                width = Math.max(width, max + 6);
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

    // Devuelve {width, lines, regionesRelativas}
    private Object[] renderGrid(int estilo, int sizeMax) {
        int[] colW = anchoColumnas();
        int ncols = colW.length;

        Color bc = SetStyle.border;
        Color oc = SetStyle.options;
        Color fc = SetStyle.focus;
        Color tc = SetStyle.title;
        Color dc = SetStyle.description;
        Map<String, String> b = borde(estilo);

        String sep = "  ";
        int[] colStarts = new int[ncols];
        int pos = 0;
        for (int j = 0; j < ncols; j++) {
            colStarts[j] = pos;
            pos += colW[j] + sep.length();
        }
        int contentW = Math.max(0, pos - sep.length());
        int width = Math.max(sizeMax, contentW + 8);
        if (!raiz.title.isEmpty()) {
            width = Math.max(width, raiz.title.length() + 4);
        }

        Integer limit = maxShowRows;
        int total = grid.length;
        boolean truncated = limit != null && limit > 0 && limit < total;
        ajustarScrollFilas();

        List<Integer> window = new ArrayList<>();
        if (truncated) {
            for (int r = raiz.scroll; r < Math.min(raiz.scroll + limit, total); r++) {
                window.add(r);
            }
        } else {
            for (int r = 0; r < total; r++) {
                window.add(r);
            }
        }

        String headerLine = null;
        if (columns != null) {
            StringBuilder sb = new StringBuilder();
            for (int j = 0; j < ncols; j++) {
                if (j > 0) {
                    sb.append(sep);
                }
                String h = j < columns.length ? columns[j] : "";
                sb.append(GRDataTable.pad(h, colW[j], colAlign[j]));
            }
            headerLine = sb.toString();
        }

        List<String> lines = new ArrayList<>();
        List<int[]> regiones = new ArrayList<>();

        String vL;
        String vR;
        String linea = null;
        if (b != null) {
            linea = hline(b.get("h"), width - 2);
            vL = pintarAnim(b.get("v"), bc);
            vR = pintarAnim(b.get("v"), bc, 0, width - 1);
            lines.add(pintarAnim(b.get("tl") + linea + b.get("tr"), bc, 0, 0));
            if (!raiz.title.isEmpty()) {
                lines.add(vL + " " + pintarAnim(centrado(raiz.title, width - 4), tc, lines.size(), 0) + " " + vR);
                lines.add(pintarAnim(b.get("v") + linea + b.get("v"), bc, lines.size(), 0));
            }
            if (headerLine != null) {
                lines.add(vL + " " + pintar(izq(headerLine, width - 4), tc) + " " + vR);
                lines.add(pintarAnim(b.get("v") + linea + b.get("v"), bc, lines.size(), 0));
            }
            if (ncols == 0) {
                lines.add(vL + " " + pintar(izq("(tabla vacia)", width - 4), oc) + " " + vR);
            }
        } else {
            String simbolo = "#";
            vL = pintar(simbolo, bc);
            vR = vL;
            String barra = pintar(simbolo.repeat(width), bc);
            lines.add(barra);
            if (!raiz.title.isEmpty()) {
                lines.add(vL + " " + pintar(centrado(raiz.title, width - 4), tc) + " " + vR);
                lines.add(barra);
            }
            if (headerLine != null) {
                lines.add(vL + " " + pintar(izq(headerLine, width - 4), tc) + " " + vR);
                lines.add(barra);
            }
            if (ncols == 0) {
                lines.add(vL + " " + pintar(izq("(tabla vacia)", width - 4), oc) + " " + vR);
            }
        }

        for (int r : window) {
            StringBuilder sb = new StringBuilder();
            int visibleLen = 0;
            for (int j = 0; j < grid[r].length; j++) {
                Item cell = grid[r][j];
                String texto = GRDataTable.pad(cell == null ? "" : cell.nombre(), colW[j], colAlign[j]);
                if (j > 0) {
                    sb.append(sep);
                    visibleLen += sep.length();
                }
                visibleLen += texto.length();
                if (cell == null) {
                    sb.append(texto);
                    continue;
                }
                boolean selected = r == row && j == col;
                sb.append(pintar(texto, selected ? fc : oc));
                regiones.add(new int[]{ lines.size(), colStarts[j], colStarts[j] + colW[j], r, j });
            }
            String fill = " ".repeat(Math.max(0, width - 4 - visibleLen));
            lines.add(vL + " " + sb + fill + " " + vR);
        }

        if (b != null) {
            lines.add(pintarAnim(b.get("bl") + linea + b.get("br"), bc, lines.size(), 0));
        } else {
            lines.add(pintar("#".repeat(width), bc));
        }

        if (truncated) {
            lines.add(pintar(der((row + 1) + " de " + total, width), dc));
        }
        Item current = grid.length > 0 && grid[row].length > 0 ? grid[row][col] : null;
        String desc = current == null ? "" : current.descripcion();
        if (desc != null && !desc.isEmpty()) {
            lines.add(pintar(der(desc, width), dc));
        }

        return new Object[]{ width, lines, regiones };
    }

    @Override
    @SuppressWarnings("unchecked")
    void drawLoop(int sizeMax) throws Exception {
        boolean firstKey = true;
        boolean firstFrame = true;

        while (true) {
            int key = firstKey ? leerTecla() : leerTeclaOTick();
            firstKey = false;

            if (key == CLICK && ultimoClick() != null && !cellRegions.isEmpty()) {
                int[] c = ultimoClick();
                for (int[] r : cellRegions) {
                    if (c[1] >= r[0] && c[1] < r[1] && c[0] >= r[2] && c[0] < r[3]) {
                        row = r[4];
                        col = r[5];
                        key = ENTER;
                        break;
                    }
                }
            } else if (key == HOVER && ultimoHover() != null && !cellRegions.isEmpty()) {
                int[] c = ultimoHover();
                boolean changed = false;
                for (int[] r : cellRegions) {
                    if (c[1] >= r[0] && c[1] < r[1] && c[0] >= r[2] && c[0] < r[3]) {
                        if (r[4] != row || r[5] != col) {
                            row = r[4];
                            col = r[5];
                            changed = true;
                        }
                        break;
                    }
                }
                if (!changed) {
                    continue;
                }
            }

            if (key == CTRL_C || key == FIN || key == 'q') {
                break;
            }

            if (key == ARRIBA)         mover(-1, 0);
            else if (key == ABAJO)     mover(1, 0);
            else if (key == IZQUIERDA) mover(0, -1);
            else if (key == DERECHA)   mover(0, 1);

            if (firstFrame) {
                System.out.print(LIMPIAR);
                firstFrame = false;
            } else {
                System.out.print(INICIO);
            }

            int cols = anchoTerminal();
            Object[] render = renderGrid(style, sizeMax);
            int width = (Integer) render[0];
            List<String> lines = (List<String>) render[1];
            List<int[]> relativas = (List<int[]>) render[2];

            int[] cabecera = imprimirBannerSubtitulo(cols, width);
            int printedRows = cabecera[0];
            int ref = cabecera[1];

            String outerPad = (center && ref > width) ? " ".repeat((ref - width) / 2) : "";
            int panelCol = outerPad.length() + 1;

            for (String line : lines) {
                p(outerPad + line);
            }

            List<int[]> absolutas = new ArrayList<>();
            for (int[] r : relativas) {
                absolutas.add(new int[]{
                    printedRows + r[0] + 1, printedRows + r[0] + 2,
                    panelCol + 2 + r[1], panelCol + 2 + r[2],
                    r[3], r[4] });
            }
            cellRegions = absolutas;

            System.out.print(BORRAR_ABAJO);
            System.out.flush();

            if (key == ENTER) {
                Item current = grid.length > 0 && grid[row].length > 0 ? grid[row][col] : null;
                if (current instanceof Opcion) {
                    restaurarTerminal();
                    System.out.println(LIMPIAR);
                    ((Opcion) current).ejecutar();
                    break;
                }
            }
        }
    }
}
