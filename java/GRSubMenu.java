// ===========================================================================
//  GRSubMenu - lista de opciones anidada.
//
//  Se pone directo como una fila mas del menu que lo contiene. Cuando esa
//  fila queda resaltada, su panel se dibuja solo a la derecha; flecha
//  derecha (o Enter) mete el foco adentro, flecha izquierda lo saca.
//
//  No tiene titulo, banner ni subtitulo propios, y los colores los hereda
//  de GRmenu.SetStyle (son globales). El borde tambien: si no le pasas
//  style, usa el del panel que lo contiene, en cascada.
// ===========================================================================

class GRSubMenu extends Nodo {

    // El menu principal cuenta como nivel 1: menu < sub < sub < sub
    static final int MAX_DEPTH = 4;

    GRSubMenu(String nombre, Item[] items) {
        this(nombre, items, null, 10, false);
    }

    GRSubMenu(String nombre, Item[] items, Integer style) {
        this(nombre, items, style, 10, false);
    }

    GRSubMenu(String nombre, Item[] items, Integer style, Integer maxShowOptions, boolean searchable) {
        this.nombre = nombre;
        this.items = items;
        this.style = style;
        this.maxShowOptions = maxShowOptions;
        this.searchable = searchable;
    }
}
