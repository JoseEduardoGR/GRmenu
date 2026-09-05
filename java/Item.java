// ===========================================================================
//  Item - cualquier cosa que pueda aparecer como fila del menu.
//
//  Solo hay dos: una Opcion (ejecuta algo) o un GRSubMenu (abre otro panel).
//  Python no necesitaba esto porque acepta cualquier cosa en la lista; Java
//  necesita un tipo comun para poder guardarlos juntos en un arreglo.
// ===========================================================================

abstract class Item {

    // Texto que se muestra en la fila.
    abstract String nombre();

    // Texto chico que aparece abajo del recuadro cuando la fila esta
    // seleccionada. Vacio = no se dibuja nada.
    String descripcion() {
        return "";
    }

    // Celdas de la fila cuando el menu es un GRDataTable. null = fila comun.
    String[] celdas() {
        return null;
    }
}
