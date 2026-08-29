<div align="center">

# GRmenu (Ruby)

**Menús de navegación por teclado para terminal, en modo TTY crudo**

Flechas arriba/abajo para moverte · `Enter` para elegir · `q` para salir

[![License: MIT](https://img.shields.io/github/license/JoseEduardoGR/GRmenu)](LICENSE)

</div>

> ⚠️ Requiere una terminal real (TTY) en Linux o macOS. No funciona en streams no interactivos, porque usa `IO#raw`/`IO#getch` para leer teclas en modo crudo.

---

## 📦 Instalación

Todavía no está publicada en RubyGems. Por ahora, se usa directo desde el archivo:

```ruby
require_relative "GRmenu"
```

<sub>Requiere Ruby ≥ 2.6.</sub>

---

## 🚀 Uso rápido

```ruby
require_relative "GRmenu"

def opcion_uno
  puts "elegiste uno"
end

def opcion_dos
  puts "elegiste dos"
end

menu = GRmenu.new([method(:opcion_uno), method(:opcion_dos)], title: "Mi menu", style: 19)
menu.style_config.border("yellow")
menu.style_config.options("green")
menu.draw
```

Cada elemento del array es un `Method`, `Proc`, `Symbol` o cualquier objeto invocable; su nombre se usa como texto de la opción, y al presionar `Enter` sobre ella, se ejecuta.

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

### Colores (`style_config`)

Cada instancia tiene su propio `style_config` (alias `SetStyle`) para personalizar cada zona por separado. `level: 1` es el tono normal y `level: 2` el brillante.

```ruby
menu.style_config.border("cyan")          # color del borde
menu.style_config.options("white")        # color de las opciones no seleccionadas
menu.style_config.focus("green", 2)       # color de la opción resaltada
```

También se pueden fijar valores por defecto para toda la clase, antes de crear instancias:

```ruby
GRmenu::SetStyle.border("cyan")
GRmenu::SetStyle.options("white")
GRmenu::SetStyle.focus("green", 2)
```

Colores disponibles: `black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`.

### Estilos de borde (`style:`)

El parámetro `style:` acepta un número que define cómo se dibuja el marco del menú:

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

```ruby
menu = GRmenu.new([opcion_uno, opcion_dos].map { |m| method(m) }, title: "Mi menu", style: 7)  # bordes redondeados
```

### Ancho del menú

`draw` acepta `size_max:`, el ancho mínimo en caracteres del cuadro (se expande automáticamente si el título o las opciones son más largos):

```ruby
menu.draw(size_max: 30)
```

---

## 📖 Referencia de la API

### `GRmenu.new(functions, title: "", style: 19)`

| Parámetro   | Tipo              | Descripción                                      |
|-------------|-------------------|---------------------------------------------------|
| `functions` | `Array`           | Acciones a mostrar como opciones, en orden (`Method`, `Proc`, `Symbol`, etc). |
| `title:`    | `String`          | Título mostrado en la cabecera del menú.          |
| `style:`    | `Integer`         | Número de estilo de borde (ver tabla arriba).     |

### `#draw(size_max: 20)`

Dibuja el menú y bloquea el hilo hasta que el usuario elige una opción (`Enter`) o sale (`q`).

### `#style_config` (alias `SetStyle`)

| Método                                  | Descripción                              |
|-------------------------------------------|-------------------------------------------|
| `style_config.border(color, level = 1)`   | Color del marco del menú.               |
| `style_config.options(color, level = 1)`  | Color de las opciones sin seleccionar.  |
| `style_config.focus(color, level = 2)`    | Color de la opción resaltada.           |

Los mismos métodos existen a nivel de clase (`GRmenu::SetStyle.border`, etc.) para fijar los valores por defecto de las instancias que se creen después.

---

## 🤝 Contribuir

Las contribuciones son bienvenidas. Podés abrir un [issue](https://github.com/JoseEduardoGR/GRmenu/issues) o enviar un pull request.

## 📄 Licencia

Distribuido bajo licencia [MIT](LICENSE).

<div align="center">

Hecho por [grcode](https://github.com/JoseEduardoGR)

</div>
