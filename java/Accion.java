// ===========================================================================
//  Accion - lo que hace una opcion cuando le das Enter.
//
//  En Python las opciones eran funciones sueltas guardadas en una lista.
//  Java no deja guardar una funcion como valor: necesita un objeto. Esta
//  interfaz es ese objeto.
//
//  Como tiene un solo metodo, se puede escribir de dos formas:
//
//      class Saludar implements Accion {
//          public void ejecutar() { System.out.println("hola"); }
//      }
//
//      () -> System.out.println("hola")     // lambda, lo mismo mas corto
// ===========================================================================

interface Accion {
    void ejecutar();
}
