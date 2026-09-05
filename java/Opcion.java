// ===========================================================================
//  Opcion - una fila del menu que ejecuta algo.
//
//  Equivale a los tres formatos que aceptaba la lista de Python:
//      funcion                       -> new Opcion("Nombre", accion)
//      (nombre, funcion)             -> new Opcion("Nombre", accion)
//      (nombre, funcion, desc)       -> new Opcion("Nombre", accion, desc)
//      ((celda, celda), funcion)     -> new Opcion(celdas, accion)   [tablas]
// ===========================================================================

class Opcion extends Item {

    final String nombre;
    final Accion accion;
    final String descripcion;
    final String[] celdas;

    // Codigo fuente a mostrar con la tecla 't'. Java no puede sacarlo solo
    // (ver GRmenu.fuente), asi que si lo querres se pasa a mano.
    String codigo;

    Opcion(String nombre, Accion accion) {
        this(nombre, accion, "", null);
    }

    Opcion(String nombre, Accion accion, String descripcion) {
        this(nombre, accion, descripcion, null);
    }

    // Fila de tabla: las celdas arman el nombre uniendolas con " | ".
    Opcion(String[] celdas, Accion accion) {
        this(String.join(" | ", celdas), accion, "", celdas);
    }

    Opcion(String[] celdas, Accion accion, String descripcion) {
        this(String.join(" | ", celdas), accion, descripcion, celdas);
    }

    private Opcion(String nombre, Accion accion, String descripcion, String[] celdas) {
        this.nombre = nombre;
        this.accion = accion;
        this.descripcion = descripcion == null ? "" : descripcion;
        this.celdas = celdas;
    }

    // Encadenable: new Opcion(...).conCodigo("...")
    Opcion conCodigo(String codigo) {
        this.codigo = codigo;
        return this;
    }

    @Override
    String nombre() {
        return nombre;
    }

    @Override
    String descripcion() {
        return descripcion;
    }

    @Override
    String[] celdas() {
        return celdas;
    }

    void ejecutar() {
        if (accion != null) {
            accion.ejecutar();
        }
    }
}
