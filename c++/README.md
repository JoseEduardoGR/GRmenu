<div align="center">

# GRmenu (C++)

**Menús de navegación por teclado para terminal, en modo TTY crudo**

Flechas arriba/abajo para moverte · `Enter` para elegir · `q` para salir

[![License: MIT](https://img.shields.io/github/license/JoseEduardoGR/GRmenu)](LICENSE)

</div>

> ⚠️ Requiere una terminal real (TTY) en Linux o macOS. No funciona en streams no interactivos, porque usa `termios.h` para leer teclas en modo crudo.

---

## 📦 Instalación

Es una librería **header-only**: no hay nada que compilar ni linkear aparte. Copiá `GRmenu.h` a tu proyecto e incluilo:

```cpp
#include "GRmenu.h"
```

<sub>Requiere C++17 y un compilador con headers POSIX (`termios.h`, `unistd.h`) — Linux o macOS.</sub>

---

## 🚀 Uso rápido

```cpp
#include "GRmenu.h"
#include <cstdio>

void opcion_uno() { std::puts("elegiste uno"); }
void opcion_dos() { std::puts("elegiste dos"); }

int main() {
    GRmenu menu({GRMENU_ACTION(opcion_uno), GRMENU_ACTION(opcion_dos)}, "Mi menu", 19);
    menu.styleConfig().setBorder("yellow");
    menu.styleConfig().setOptions("green");
    menu.draw();
}
```

```bash
g++ -std=c++17 main.cpp -o main
```

A diferencia de Python/Ruby, C++ no puede leer el nombre de una función en tiempo de ejecución, así que cada opción necesita su nombre explícito. La macro `GRMENU_ACTION(fn)` te ahorra escribirlo dos veces — expande a `GRmenu::Option{"fn", fn}`. También podés armar las opciones a mano:

```cpp
GRmenu menu({
    {"Opción uno", opcion_uno},
    {"Opción dos", []{ std::puts("una lambda también funciona"); }},
}, "Mi menu");
```

---

## 🕹️ Controles

| Tecla       | Acción                    |
|-------------|---------------------------|
| `↑`         | Mover selección arriba    |
| `↓`         | Mover selección abajo     |
| `Enter`     | Ejecutar opción seleccionada |
| `q`         | Salir del menú             |

---

## 🎨 Personalización

### Colores (`styleConfig()`)

`level` 1 es el tono normal y 2 el brillante.

```cpp
menu.styleConfig().setBorder("cyan");        // color del borde
menu.styleConfig().setOptions("white");      // color de las opciones no seleccionadas
menu.styleConfig().setFocus("green", 2);     // color de la opción resaltada
```

Para fijar los valores por defecto de las instancias que crees después:

```cpp
GRmenu::defaultStyle().setBorder("cyan");
```

Colores disponibles: `black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`.

### Estilos de borde (`style`)

El tercer argumento del constructor acepta un número que define cómo se dibuja el marco del menú:

| `style` | Vista previa | `style` | Vista previa |
|:---:|:---|:---:|:---|
| 1  | `#===#` | 11 | `░░░░░` |
| 2  | `┌───┐` | 12 | `█████` |
| 3  | `╔═══╗` | 13 | `*****` |
| 4  | `┏━━━┓` | 14 | `+++++` |
| 5  | `╒═══╕` | 15 | `=====` |
| 6  | `╓───╖` | 16 | `~~~~~` |
| 7  | `╭───╮` | 17 | `-----` |
| 8  | `▛▀▀▀▜` | 18 | `◆◆◆◆◆` |
| 9  | `▓▓▓▓▓` | 19 | `●●●●●` *(default)* |
| 10 | `▒▒▒▒▒` | 20 | `★★★★★` |

### Ancho del menú

`draw` acepta el ancho mínimo del cuadro (se expande automáticamente si el título o las opciones son más largos):

```cpp
menu.draw(30);
```

---

## 📖 Referencia de la API

### `GRmenu(std::vector<Option> options, std::string title = "", int style = 19)`

| Parámetro   | Tipo                     | Descripción                                      |
|-------------|--------------------------|-----------------------------------------------------|
| `options`   | `std::vector<GRmenu::Option>` | Opciones a mostrar, en orden (`{nombre, acción}`). |
| `title`     | `std::string`            | Título mostrado en la cabecera del menú.          |
| `style`     | `int`                    | Número de estilo de borde (ver tabla arriba).     |

### `GRmenu::Option`

```cpp
struct Option {
    std::string name;
    std::function<void()> action;
};
```

### `void draw(int size_max = 20)`

Dibuja el menú y bloquea el hilo hasta que el usuario elige una opción (`Enter`) o sale (`q`).

### `styleConfig()`

| Método                                   | Descripción                              |
|--------------------------------------------|-------------------------------------------|
| `styleConfig().setBorder(color, level = 1)` | Color del marco del menú.               |
| `styleConfig().setOptions(color, level = 1)`| Color de las opciones sin seleccionar.  |
| `styleConfig().setFocus(color, level = 2)`  | Color de la opción resaltada.           |

`GRmenu::defaultStyle()` expone los mismos métodos a nivel estático, para fijar los valores por defecto de instancias futuras.

---

## 🤝 Contribuir

Las contribuciones son bienvenidas. Podés abrir un [issue](https://github.com/JoseEduardoGR/GRmenu/issues) o enviar un pull request.

## 📄 Licencia

Distribuido bajo licencia [MIT](LICENSE).

<div align="center">

Hecho por [grcode](https://github.com/JoseEduardoGR)

</div>
