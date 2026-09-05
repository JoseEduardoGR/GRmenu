// ===========================================================================
//  e.java - ejemplo de uso de GRmenu 1.0.0
//
//  Se corre con:  java e.java
//  Java compila solo el GRmenu.java de al lado.
// ===========================================================================

class e {

    public static void main(String[] args) throws Exception {

        // Colores del menu (el SetStyle de Python).
        GRmenu.setBorde("magenta", 2);
        GRmenu.setOpcion("cyan", 1);
        GRmenu.setFoco("yellow", 2);

        // En Python era una lista de funciones. Aca es un arreglo de
        // objetos que cumplen la interfaz GRmenu.Opcion.
        GRmenu.Opcion[] opciones = new GRmenu.Opcion[]{
            new Saludar(),
            new Tabla(),
            new Contar(),
            new Salir()
        };

        // titulo = "Mi menu", estilo 7 = recuadro redondeado.
        GRmenu menu = new GRmenu(opciones, "Mi menu", 7);
        menu.draw(20);
    }
}


// ===========================================================================
//  Las opciones: cada una dice como se llama y que hace con Enter.
// ===========================================================================

class Saludar implements GRmenu.Opcion {

    public String nombre() {
        return "Saludar";
    }

    public void ejecutar() {
        System.out.println("Hola, GRmenu en Java.");
    }
}


class Tabla implements GRmenu.Opcion {

    public String nombre() {
        return "Tabla del 7";
    }

    public void ejecutar() {
        for (int i = 1; i <= 10; i++) {
            System.out.println("7 x " + i + " = " + (7 * i));
        }
    }
}


class Contar implements GRmenu.Opcion {

    public String nombre() {
        return "Contar hasta 5";
    }

    public void ejecutar() {
        for (int i = 1; i <= 5; i++) {
            System.out.println(i);
        }
    }
}


class Salir implements GRmenu.Opcion {

    public String nombre() {
        return "Salir";
    }

    public void ejecutar() {
        System.out.println("Chau.");
    }
}
