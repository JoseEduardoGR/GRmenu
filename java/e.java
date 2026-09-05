// ===========================================================================
//  e.java - ejemplo de uso de GRmenu 4.0.0
//
//  Se corre con:  java e.java
//  (desde la carpeta java/, para que encuentre ../data/*.json)
//
//  Teclas:
//     flechas arriba/abajo   moverse
//     flecha derecha         entrar a un submenu
//     flecha izquierda       volver
//     Enter                  ejecutar
//     espacio                marcar (Enter ejecuta todas las marcadas)
//     /                      buscar
//     t                      ver el codigo de la opcion
//     q                      salir
//     mouse                  click y hover tambien andan
// ===========================================================================

class e {

    public static void main(String[] args) throws Exception {

        // --- Colores (el SetStyle de Python) -----------------------------
        GRmenu.SetStyle.Border("magenta", 2);
        GRmenu.SetStyle.Options("white", 1);
        GRmenu.SetStyle.Focus("yellow", 2);
        GRmenu.SetStyle.Title("cyan", 2);
        GRmenu.SetStyle.Banner("magenta", 2);
        GRmenu.SetStyle.Subtitle("cyan", 2);

        // La pantalla de bienvenida: sin esto sale el logo de GRmenu.
        GRmenu.SetStyle.Welcome("Bienvenido. Apreta cualquier tecla.");

        // --- Submenu -----------------------------------------------------
        //
        //  Un GRSubMenu se pone como una fila mas. Cuando esa fila queda
        //  resaltada, su panel aparece solo a la derecha.
        Item[] colores = {
            new Opcion("Rojo",  () -> System.out.println("Elegiste rojo")),
            new Opcion("Verde", () -> System.out.println("Elegiste verde")),
            new Opcion("Azul",  () -> System.out.println("Elegiste azul")),
        };

        // --- Opciones del menu principal ---------------------------------
        //
        //  El "() -> ..." es una lambda: la forma corta de escribir un
        //  objeto que implementa Accion. Estas dos lineas son lo mismo:
        //
        //      new Opcion("Hola", () -> System.out.println("hola"))
        //      new Opcion("Hola", new Saludar())    // con la clase de abajo
        Item[] opciones = {
            new Opcion("Saludar", new Saludar(), "Imprime un saludo"),

            new Opcion("Tabla del 7", () -> {
                for (int i = 1; i <= 10; i++) {
                    System.out.println("7 x " + i + " = " + (7 * i));
                }
            }, "Del 1 al 10").conCodigo(
                "for (int i = 1; i <= 10; i++) {\n"
              + "    System.out.println(\"7 x \" + i + \" = \" + (7 * i));\n"
              + "}"),

            new Opcion("Contar hasta 5", () -> {
                for (int i = 1; i <= 5; i++) {
                    System.out.println(i);
                }
            }, "Se puede marcar con espacio"),

            new GRSubMenu("Colores", colores),

            new Opcion("Fecha", () -> System.out.println(new java.util.Date())),
            new Opcion("Ruta actual", () -> System.out.println(System.getProperty("user.dir"))),
            new Opcion("Salir", () -> System.out.println("Chau.")),
        };

        // --- El menu -----------------------------------------------------
        GRmenu menu = new GRmenu(
            opciones,
            "Menu principal",   // title
            7,                  // style: 7 = recuadro redondeado
            "GRMENU",           // banner en arte ASCII
            "Port a Java de la version 4.0.0",  // subtitle
            3,                  // bannerStyle
            null,               // divider: null = automatico
            true,               // center
            1,                  // font (1 al 10)
            10,                 // maxShowOptions
            true,               // searchable: habilita "/"
            null                // animate: null, "linear", "fade", "diagonal", "rgb"
        );

        menu.draw();
    }
}


// La misma opcion "Saludar", escrita con una clase en vez de una lambda.
class Saludar implements Accion {

    public void ejecutar() {
        System.out.println("Hola, GRmenu 4.0.0 en Java.");
    }
}
