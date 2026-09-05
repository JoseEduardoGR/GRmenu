// ===========================================================================
//  Nodo - un panel de opciones con su estado propio.
//
//  En Python esto no existia como clase: GRmenu y GRSubMenu simplemente
//  tenian los mismos atributos y el codigo los trataba igual (duck typing).
//  Java necesita que compartan un tipo, asi que el estado comun vive aca:
//  el menu raiz y cada submenu son Nodos.
// ===========================================================================

class Nodo extends Item {

    Item[] items;                 // las filas de este panel
    String nombre = "";           // texto de la fila que lo abre (submenus)
    String title = "";            // titulo dentro del recuadro
    Integer style;                // null = hereda el del panel padre
    Integer maxShowOptions = 10;  // null = sin limite (muestra todas)
    boolean searchable;           // habilita el modo busqueda con "/"

    int index;                    // fila seleccionada
    int scroll;                   // primera fila visible cuando hay scroll
    boolean searchActive;
    String searchQuery = "";

    // Solo GRDataTable las usa.
    String[] columns;
    char[] colAlign;

    @Override
    String nombre() {
        return nombre;
    }

    Item actual() {
        if (items == null || items.length == 0) {
            return null;
        }
        int i = Math.max(0, Math.min(index, items.length - 1));
        return items[i];
    }
}
