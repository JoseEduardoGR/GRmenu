<div align="center">

# GRmenu

**Menús de navegación por teclado para terminal, en modo TTY crudo**

Flechas arriba/abajo para moverte · `Enter` para elegir · `q` para salir

[![Gem Version](https://badge.fury.io/rb/grmenu.svg)](https://badge.fury.io/rb/grmenu)
[![PyPI version](https://img.shields.io/pypi/v/grmenu?color=blue&label=PyPI)](https://pypi.org/project/grmenu/)
[![Ruby](https://img.shields.io/badge/ruby-%3E%3D%202.6-red.svg)](https://www.ruby-lang.org)
[![Python versions](https://img.shields.io/pypi/pyversions/grmenu)](https://pypi.org/project/grmenu/)
[![License: MIT](https://img.shields.io/github/license/JoseEduardoGR/GRmenu)](LICENSE)
[![GitHub last commit](https://img.shields.io/github/last-commit/JoseEduardoGR/GRmenu)](https://github.com/JoseEduardoGR/GRmenu/commits/main)
[![GitHub stars](https://img.shields.io/github/stars/JoseEduardoGR/GRmenu?style=social)](https://github.com/JoseEduardoGR/GRmenu/stargazers)

</div>

---

## ✨ Características

- 🎮 **Navegación con flechas** — arriba/abajo para moverte, `Enter` para ejecutar, `q` para salir
- 🎨 **20 estilos de borde** — desde ASCII clásico hasta caracteres Unicode y bloques
- 🌈 **Colores personalizables** — borde, opciones y foco por separado, con 8 colores en 2 tonos cada uno
- 📦 **Cero dependencias externas** — solo la librería estándar (`io/console` en Ruby, `termios`/`tty` en Python)
- 💎 **Ruby & Python** — disponible como gema de Ruby (`grmenu`) y como paquete pip de Python (`grmenu`)
- 🐧 **Linux / macOS** — funciona en cualquier terminal POSIX

> ⚠️ Requiere una terminal real (TTY) en Linux o macOS. En Ruby utiliza `io/console` en modo crudo (`raw`) y en Python `termios`/`tty` para capturar pulsaciones de teclas en tiempo real.

---

## 📦 Instalación

### Ruby (RubyGems)

```bash
gem install grmenu
```

O en tu `Gemfile`:

```ruby
gem 'grmenu'
```

### Python (PyPI)

```bash
pip install grmenu
```

---

## 🚀 Uso rápido

### 💎 Ruby

```ruby
require 'GRmenu'

def opcion_uno
  puts "elegiste uno"
end

def opcion_dos
  puts "elegiste dos"
end

menu = GRmenu.new(
  [method(:opcion_uno), method(:opcion_dos)],
  title: "Mi menu",
  style: 19
)

menu.set_style.border("yellow")
menu.set_style.options("green")
menu.draw
```

Cada elemento de la lista puede ser un `Method` (`method(:mi_metodo)`), un `Proc` / `lambda` (`-> { ... }`), un arreglo `["Nombre", callable]` o un `Symbol` (`:mi_metodo`). Al presionar `Enter`, esa acción se ejecuta.

### 🐍 Python

```python
from GRmenu import GRmenu

def opcion_uno():
    print("elegiste uno")

def opcion_dos():
    print("elegiste dos")

menu = GRmenu(
    [opcion_uno, opcion_dos],
    title="Mi menu",
    style=19
)

menu.SetStyle.Border("yellow")
menu.SetStyle.Options("green")
menu.draw()
```

Cada elemento de la lista es una función; el **nombre de la función** se usa como texto de la opción, y al presionar `Enter` sobre ella, esa función se ejecuta.

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

### Colores (`SetStyle` / `set_style`)

Cada zona del menú se personaliza por separado. `level=1` (o `1`) es el tono normal y `level=2` (o `2`) el brillante.

#### En Ruby:
```ruby
menu.set_style.border("cyan")        # color del borde
menu.set_style.options("white")      # color de las opciones no seleccionadas
menu.set_style.focus("green", 2)     # color de la opción resaltada (brillante)
```

#### En Python:
```python
menu.SetStyle.Border("cyan")        # color del borde
menu.SetStyle.Options("white")      # color de las opciones no seleccionadas
menu.SetStyle.Focus("green", 2)     # color de la opción resaltada (brillante)
```

Colores disponibles: `black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`.

### Estilos de borde (`style`)

El parámetro `style` acepta un número (1 al 20) que define cómo se dibuja el marco del menú:

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
# Ruby
menu = GRmenu.new([method(:opcion_uno), method(:opcion_dos)], title: "Mi menu", style: 7)  # bordes redondeados
```

```python
# Python
menu = GRmenu([opcion_uno, opcion_dos], title="Mi menu", style=7)  # bordes redondeados
```

### Ancho del menú

`draw()` acepta `size_max`, el ancho mínimo en caracteres del cuadro (se expande automáticamente si el título o las opciones son más largos):

```ruby
# Ruby
menu.draw(size_max: 30)
```

```python
# Python
menu.draw(size_max=30)
```

---

## 📖 Referencia de la API

### 💎 Ruby

#### `GRmenu.new(functions, title: "", style: 19)`

| Parámetro   | Tipo                                  | Descripción                                      |
|-------------|---------------------------------------|---------------------------------------------------|
| `functions` | `Array<Method, Proc, Symbol, Array>`  | Métodos, procs o lambdas a mostrar como opciones. |
| `title`     | `String` (opcional)                   | Título mostrado en la cabecera del menú.          |
| `style`     | `Integer` (opcional)                  | Número de estilo de borde (ver tabla arriba).     |

#### `menu.draw(size_max: 20)`

Dibuja el menú interactivo y bloquea el hilo hasta que el usuario elige una opción (`Enter`) o sale (`q`).

#### `menu.set_style`

| Método                              | Descripción                              |
|-------------------------------------|-------------------------------------------|
| `set_style.border(color, level=1)`  | Color del marco del menú.                 |
| `set_style.options(color, level=1)` | Color de las opciones sin seleccionar.    |
| `set_style.focus(color, level=2)`   | Color de la opción resaltada.             |

*(Nota: también se admiten los alias `menu.SetStyle.Border(...)`, `menu.SetStyle.Options(...)`, `menu.SetStyle.Focus(...)`)*.

---

### 🐍 Python

#### `GRmenu(functions, title="", style=19)`

| Parámetro   | Tipo             | Descripción                                      |
|-------------|------------------|---------------------------------------------------|
| `functions` | `list[Callable]` | Funciones a mostrar como opciones, en orden.      |
| `title`     | `str`            | Título mostrado en la cabecera del menú.          |
| `style`     | `int`            | Número de estilo de borde (ver tabla arriba).     |

#### `menu.draw(size_max=20)`

Dibuja el menú y bloquea el hilo hasta que el usuario elige una opción (`Enter`) o sale (`q`).

#### `menu.SetStyle`

| Método                          | Descripción                              |
|----------------------------------|-------------------------------------------|
| `SetStyle.Border(color, level=1)` | Color del marco del menú.                 |
| `SetStyle.Options(color, level=1)`| Color de las opciones sin seleccionar.    |
| `SetStyle.Focus(color, level=2)`  | Color de la opción resaltada.             |

---

## 🧩 Ejemplos completos

### 💎 Ejemplo completo en Ruby

```ruby
require 'GRmenu'

def saludar
  puts "¡Hola desde Ruby!"
end

def salir_app
  puts "Hasta luego 👋"
end

def acerca_de
  puts "GRmenu v0.1.4 — menú TTY para terminal"
end

menu = GRmenu.new(
  [
    method(:saludar),
    method(:acerca_de),
    ["Personalizado", -> { puts "Opción con bloque lambda" }],
    method(:salir_app)
  ],
  title: "GRmenu Demo (Ruby)",
  style: 7
)

menu.set_style.border("magenta")
menu.set_style.options("white")
menu.set_style.focus("cyan", 2)
menu.draw(size_max: 28)
```

---

### 🐍 Ejemplo completo en Python

```python
from GRmenu import GRmenu

def saludar():
    print("¡Hola desde Python!")

def salir_app():
    print("Hasta luego 👋")

def acerca_de():
    print("GRmenu v0.1.4 — menú TTY para terminal")

def personalizado():
    print("Opción personalizada en Python")

menu = GRmenu(
    [
        saludar,
        acerca_de,
        personalizado,
        salir_app
    ],
    title="GRmenu Demo (Python)",
    style=7
)

menu.SetStyle.Border("magenta")
menu.SetStyle.Options("white")
menu.SetStyle.Focus("cyan", 2)
menu.draw(size_max=28)
```

---

## 🤝 Contribuir

Las contribuciones son bienvenidas. Podés abrir un [issue](https://github.com/JoseEduardoGR/GRmenu/issues) o enviar un pull request.

---

## 📄 Licencia

Distribuido bajo licencia [MIT](LICENSE).

---

<div align="center">

Hecho por [grcode](https://github.com/JoseEduardoGR)

</div>
