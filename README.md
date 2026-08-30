<div align="center">

# GRmenu

**Menús interactivos por teclado para terminal en modo TTY crudo, con soporte para Banners ASCII 3D, estilos y colores personalizados**

Flechas arriba/abajo para moverte · `Enter` para elegir · `q` para salir

| 💎 Ruby | 🐍 Python |
|:---:|:---:|
| [![Gem Version](https://img.shields.io/gem/v/grmenu)](https://rubygems.org/gems/grmenu) [![Gem Downloads](https://img.shields.io/gem/dt/grmenu)](https://rubygems.org/gems/grmenu) | [![PyPI version](https://img.shields.io/pypi/v/grmenu?color=blue&label=PyPI)](https://pypi.org/project/grmenu/) [![PyPI Downloads](https://static.pepy.tech/personalized-badge/grmenu?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=MAGENTA&left_text=downloads)](https://pepy.tech/projects/grmenu) |
| [![Ruby](https://img.shields.io/badge/ruby-%3E%3D%202.6-red.svg)](https://www.ruby-lang.org) | [![Python versions](https://img.shields.io/pypi/pyversions/grmenu)](https://pypi.org/project/grmenu/) |

[![License: MIT](https://img.shields.io/github/license/JoseEduardoGR/GRmenu)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS-blue)](https://github.com/JoseEduardoGR/GRmenu)

</div>

---

## ✨ Características

- 🎮 **Navegación con flechas** — arriba/abajo para moverte, `Enter` para ejecutar, `q` para salir.
- 🔤 **10 Fuentes ASCII 3D para Banners** — fuentes tipográficas tridimensionales (ANSI Shadow, Slant, Doom, Graffiti, Modular, Wire, Block, Stars, etc.).
- 🎨 **20 estilos de borde** — desde ASCII clásico hasta caracteres Unicode dobles, curvas redondeadas y bloques.
- 🌈 **Paleta de colores completa** — personalización individual de marco, título, banner, subtítulo, divisores, opciones y foco activo con 2 niveles de brillo.
- 📐 **Centrado simétrico automático** — alinea y centra automáticamente subtítulos y menús de opciones respecto al ancho de banners grandes.
- 🛠️ **Helpers nativos en modo crudo** — `clear_screen`, `continue`, `banner`, `div` y `help` sin subprocesos lentos del sistema.
- 💻 **Multiplataforma POSIX** — compatible con Linux y macOS.
- 📦 **Cero dependencias externas** — utiliza únicamente la librería estándar (`io/console` en Ruby, `termios`/`tty` en Python).

---

## 📦 Instalación

### 💎 Ruby (RubyGems)

```bash
gem install grmenu
```

O en tu `Gemfile`:

```ruby
gem 'grmenu'
```

### 🐍 Python (PyPI)

```bash
pip install grmenu
```

---

## 🚀 Uso rápido

### 💎 Ruby

```ruby
require 'GRmenu'

def iniciar_servidor
  puts "Servidor iniciado en puerto 3000..."
end

def ver_estado
  puts "Estado: Operativo"
end

menu = GRmenu.new(
  [method(:iniciar_servidor), method(:ver_estado)],
  title: "Panel Principal",
  style: 19
)

menu.set_style.border("yellow")
menu.set_style.options("white")
menu.set_style.focus("green", 2)
menu.draw
```

### 🐍 Python

```python
from GRmenu import GRmenu

def opcion_uno():
    print("Elegiste uno")

def opcion_dos():
    print("Elegiste dos")

menu = GRmenu(
    [opcion_uno, opcion_dos],
    title="Mi Menú",
    style=19
)

menu.SetStyle.Border("yellow")
menu.SetStyle.Options("white")
menu.SetStyle.Focus("green", 2)
menu.draw()
```

---

## 💡 Cómo se pasan las opciones y todos los parámetros en Ruby

`GRmenu` permite pasar métodos directos, símbolos, arreglos con nombres personalizados, bloques lambda/procs y helpers. Además, acepta todos los parámetros de configuración visual en la instanciación:

```ruby
menu = GRmenu.new(
  [
    method(:iniciar_servidor),                                       # 1. Method (auto-capitaliza: "Iniciar Servidor")
    :crear_respaldo,                                                 # 2. Symbol (auto-capitaliza: "Crear Respaldo")
    ["Métricas del Sistema", method(:ver_metricas)],                 # 3. Array ["Nombre Personalizado", acción]
    ["Ejecutar Lambda", -> { puts Color.pink("Lambda!"); GRmenu.continue }], # 4. Lambda/Proc
    ["Probar Banner Helper", method(:prueba_banner_rapido)],         # 5. Helper GRmenu.banner
    ["Ver Ayuda y Referencia", method(:ver_ayuda_completa)],         # 6. Helper GRmenu.help
    method(:salir)                                                   # 7. Salir
  ],
  banner: "DEV OPS",                                                 # Texto gigante en arte ASCII 3D
  title: "Panel de Control",                                         # Título en el marco de opciones
  subtitle: "Consola de Administración\nUsa las flechas y Enter",    # Subtítulo (soporta saltos de línea \n)
  font: 1,                                                           # Fuente del banner (1 al 10, por defecto 1: ANSI Shadow 3D)
  style: 7,                                                          # Estilo de marco de opciones (1 al 20, ej: 7=redondeado, 3=doble)
  banner_style: 3,                                                   # Estilo de marco del banner (1 al 20, ej: 3=doble línea)
  divider: true,                                                     # Líneas divisorias a la par del banner (true, false o número)
  center: true                                                       # Centrado automático del menú y subtítulo respecto al banner
)
```

---

## 🌟 Ejemplo Completo de Uso (Ruby `e.rb`)

A continuación se muestra el archivo de ejemplo completo [`ruby/e.rb`](ruby/e.rb) con acciones, helpers, configuración de estilos, fuentes y colores:

```ruby
# frozen_string_literal: true

require "GRmenu"

# 1. Definición de acciones/métodos
def iniciar_servidor
  GRmenu.clear_screen
  puts Color.bright_green("-> Servidor iniciado correctamente en el puerto 3000.")
  GRmenu.continue
end

def crear_respaldo
  GRmenu.clear_screen
  puts Color.bright_cyan("-> Creando respaldo de la base de datos...")
  GRmenu.continue
end

def ver_metricas
  GRmenu.clear_screen
  puts Color.bright_magenta("-> CPU: 12% | RAM: 4.2 GB | Estado: Operativo")
  GRmenu.continue
end

def prueba_banner_rapido
  GRmenu.clear_screen
  # Helper para mostrar un banner estático o animado en cualquier momento
  GRmenu.banner("OK", 0, color: "green", level: 2, style: 3, font: 1)
  GRmenu.div(40, "green", 1, "═")
  puts Color.green("  Prueba completada con éxito.")
  GRmenu.div(40, "green", 1, "═")
  GRmenu.continue
end

def ver_ayuda_completa
  GRmenu.clear_screen
  # Helper interactivo que imprime toda la guía y referencia de GRmenu
  GRmenu.help
  GRmenu.continue
end

def salir
  GRmenu.clear_screen
  puts Color.bright_yellow("¡Sesión finalizada con éxito!")
  exit(0)
end

# 2. Instanciación del menú con TODOS los parámetros disponibles
menu = GRmenu.new(
  [
    method(:iniciar_servidor),                                       # 1. Method (auto-capitaliza: "Iniciar Servidor")
    :crear_respaldo,                                                 # 2. Symbol (auto-capitaliza: "Crear Respaldo")
    ["Métricas del Sistema", method(:ver_metricas)],                 # 3. Array ["Nombre Personalizado", acción]
    ["Ejecutar Lambda", -> { puts Color.pink("Lambda!"); GRmenu.continue }], # 4. Lambda/Proc
    ["Probar Banner Helper", method(:prueba_banner_rapido)],         # 5. Helper GRmenu.banner
    ["Ver Ayuda y Referencia", method(:ver_ayuda_completa)],         # 6. Helper GRmenu.help
    method(:salir)                                                   # 7. Salir
  ],
  banner: "DEV OPS",                                                 # Texto gigante en arte ASCII 3D
  title: "Panel de Control",                                         # Título en el marco de opciones
  subtitle: "Consola de Administración\nUsa las flechas y Enter",    # Subtítulo (soporta saltos de línea \n)
  font: 1,                                                           # Fuente del banner (1 al 10, por defecto 1: ANSI Shadow 3D)
  style: 7,                                                          # Estilo de marco de opciones (1 al 20, ej: 7=redondeado, 3=doble)
  banner_style: 3,                                                   # Estilo de marco del banner (1 al 20, ej: 3=doble línea)
  divider: true,                                                     # Líneas divisorias a la par del banner (true, false o número)
  center: true                                                       # Centrado automático del menú y subtítulo respecto al banner
)

# 3. Configuración completa de colores y estilos (set_style / style_config)
# Colores disponibles: "black", "gray", "red", "green", "yellow", "blue",
#                      "magenta", "purple", "pink", "cyan", "aqua", "orange", "white"
# Niveles de brillo: 1 = normal, 2 = brillante

menu.set_style.font(1)             # 1 = ANSI Shadow 3D, 2 = Slant 3D, 3 = Doom, etc.
menu.set_style.banner("cyan", 2)   # Color del banner ASCII
menu.set_style.title("yellow", 2)  # Color del título del recuadro
menu.set_style.subtitle("white", 1)# Color del subtítulo/descripción
menu.set_style.divider("blue", 1)  # Color de las líneas divisorias
menu.set_style.border("yellow", 1) # Color del borde del marco de opciones
menu.set_style.options("white", 1) # Color de opciones no seleccionadas
menu.set_style.focus("green", 2)   # Color y brillo de la opción resaltada

# 4. Dibujar y lanzar el menú interactivo
# size_max / min_width define el ancho mínimo sugerido para el marco de opciones
menu.draw(size_max: 38)
```

---

## 📖 Guía y Referencia Rápida en Consola (`GRmenu.help`)

Para consultar en cualquier momento la lista de helpers, colores, fuentes, marcos y sintaxis directamente desde la terminal, podés ejecutar:

```ruby
GRmenu.help
```

O desde una instancia:

```ruby
menu.help
```

Salida limpia y estructurada en consola:

```text
╔══════════════════════════════════════════════════════════════╗
║              GRmenu - Guia y Referencia Rapida               ║
║            Navegacion interactiva en terminal TTY            ║
╚══════════════════════════════════════════════════════════════╝

[1] HELPERS NATIVOS EN MODO CRUDO
────────────────────────────────────────────────────────────────
  GRmenu.clear_screen (o GRmenu.clr)
    * Limpia la terminal al instante con secuencias ANSI.
  GRmenu.continue(mensaje)
    * Pausa interactiva: espera una sola tecla en modo TTY crudo.
  GRmenu.banner(texto, delay, color:, level:, style:, font:)
    * Renderiza banner ASCII 3D con marco y animacion opcional.
  GRmenu.div(longitud, color, level, char)
    * Dibuja linea divisoria horizontal adaptable a la consola.
  GRmenu.help
    * Imprime esta guia visual interactiva en consola.
```

---

## 🖥️ Línea de Comandos en Consola (`python -m GRmenu`)

Al instalar con `pip install grmenu` queda disponible el comando `GRmenu` (si no está en el `PATH`, usá `python -m GRmenu`). Es solo informativo — no crea ningún menú:

```bash
python -m GRmenu -h          # ayuda: lista todas las opciones disponibles
python -m GRmenu -a          # guia completa (parametros, estilos, fuentes, colores, metodos)
python -m GRmenu -s          # estilos de marco disponibles (style / banner_style, 1 al 20)
python -m GRmenu -b          # fuentes ASCII del banner disponibles (font, 1 al 10)
python -m GRmenu -d          # explica el parametro divider
python -m GRmenu -e          # genera example.py en el directorio actual
```

Salida limpia y estructurada en consola (`python -m GRmenu -h`):

```text
╔══════════════════════════════════════════════════════════════════════════════╗
║    ██████╗    ██████╗     ███╗   ███╗   ███████╗    ███╗   ██╗   ██╗  ██╗    ║
║   ██╔════╝    ██╔══██╗    ████╗ ████║   ██╔════╝    ████╗  ██║   ██║  ██║    ║
║   ██║  ███╗   ██████╔╝    ██╔████╔██║   █████╗      ██╔██╗ ██║   ██║  ██║    ║
║   ██║   ██║   ██╔══██╗    ██║╚██╔╝██║   ██╔══╝      ██║╚██╗██║   ██║  ██║    ║
║   ╚██████╔╝   ██║  ██║    ██║ ╚═╝ ██║   ███████╗    ██║ ╚████║   ╚█████╔╝    ║
║    ╚═════╝    ╚═╝  ╚═╝    ╚═╝     ╚═╝   ╚══════╝    ╚═╝  ╚═══╝    ╚════╝     ║
╚══════════════════════════════════════════════════════════════════════════════╝
──────────────────────────────────────────────────────────────────
                    Ayuda de linea de comandos                    
──────────────────────────────────────────────────────────────────

usage: GRmenu [-h] [-a] [-s] [-b] [-d] [-e]

GRmenu - libreria de menus interactivos para terminal en modo TTY crudo.

options:
  -h, --help     Muestra esta ayuda.
  -a, --All      Muestra la guia completa (estilos, fuentes, colores,
                 parametros, metodos).
  -s, --Style    Muestra los estilos de marco disponibles (style /
                 banner_style, 1 al 20).
  -b, --Banner   Muestra las fuentes del banner (font, 1 al 10) y sus
                 parametros.
  -d, --Divider  Explica el parametro divider (lineas divisorias del
                 banner/subtitulo).
  -e, --Example  Genera example.py en el directorio actual con un ejemplo
                 completo de la libreria.
```

Sin argumentos (`python -m GRmenu`), muestra lo mismo que `-h`. El resto de las banderas (`-a`, `-s`, `-b`, `-d`) además arrancan con un banner y subtítulo propios, y muestran previews reales generados con los mismos datos que usa la librería (no texto inventado).

---

## 🕹️ Controles

| Tecla       | Acción                    |
|-------------|---------------------------|
| `↑`         | Mover selección arriba    |
| `↓`         | Mover selección abajo     |
| `Enter`     | Ejecutar opción seleccionada |
| `q`         | Salir del menú             |

---

## 🔤 Fuentes ASCII 3D para Banners (`font: 1` al `10`)

Podés elegir entre 10 estilos tipográficos usando `menu.set_style.font(id)` o al instanciar con `font: id`:

| ID | Estilo                   | Muestra (`RUBY`) |
|:--:|--------------------------|------------------|
| **`1`** | **ANSI Shadow 3D (Default)** | `██████╗  ██╗  ██╗  ██████╗  ██╗   ██╗` |
| **`2`** | **Slant 3D (FIGlet)**    | `    ____        __  __        ____      __  __` |
| **`3`** | **Doom / Standard 3D**   | `   ____      _   _     ____     __   __` |
| **`4`** | **Graffiti Shadow 3D**   | `  ,---.      ,--. ,--.  ,---.     ,--.   ,--.` |
| **`5`** | **Small Slant / Mini 3D**| `   ___     _ _      ___     _ _` |
| **`6`** | **Modular Pipe 3D**      | `   _____    _____    _____    _____` |
| **`7`** | **Bubble / Round Gothic**| `    ____     _  _     ____     _  _` |
| **`8`** | **Double-Line Wire 3D**  | `  ╔═════╗  ║     ║  ╔════╗   ║     ║` |
| **`9`** | **Solid Fat 3D Block**   | `  ██████▄  ██   ██  ██████▄  ██   ██` |
| **`10`**| **Arcade Stars Matrix**  | `  ★★★★   ★   ★  ★★★★    ★   ★` |

---

## 🖼️ Estilos de Marco (`style` / `banner_style: 1` al `20`)

| `style` | Vista previa | `style` | Vista previa |
|:---:|:---|:---:|:---|
| 1  | `#===#` | 11 | `░░░░░` |
| 2  | `┌───┐` *(Línea simple)* | 12 | `█████` |
| 3  | `╔═══╗` *(Doble línea - Default banner)* | 13 | `*****` |
| 4  | `┏━━━┓` *(Línea gruesa)* | 14 | `+++++` |
| 5  | `╒═══╕` | 15 | `=====` |
| 6  | `╓───╖` | 16 | `~~~~~` |
| 7  | `╭───╮` *(Curvas redondeadas)* | 17 | `-----` |
| 8  | `▛▀▀▀▜` *(Bloques outline)* | 18 | `◆◆◆◆◆` |
| 9  | `▓▓▓▓▓` | 19 | `●○○○●` *(Círculos - Default opciones)* |
| 10 | `▒▒▒▒▒` | 20 | `★☆☆☆★` *(Estrellas)* |

---

## 🎨 Paleta de Colores y Módulo `Color`

### Métodos de Color directos (`Color` / `C` en Ruby)

```ruby
puts Color.green("Texto en verde")
puts Color.bright_cyan("Cian brillante")
puts Color.yellow("Texto en amarillo")
puts Color.bright_magenta("Magenta brillante")
puts Color.purple("Texto en morado")
puts Color.orange("Texto en naranja")
puts Color.pink("Texto en rosa")
puts Color.gray("Texto en gris")
```

Colores soportados: `black`, `gray`, `red`, `green`, `yellow`, `blue`, `magenta`, `purple`, `pink`, `cyan`, `aqua`, `orange`, `white`.

---

## 🛠️ Helpers Nativos en Modo Crudo

```ruby
# 1. Limpia la pantalla al instante con secuencias ANSI
GRmenu.clear_screen # o GRmenu.clr

# 2. Imprime un banner o logo gigante responsivo
GRmenu.banner("SECURE", 0, color: "magenta", style: 3, font: 1)

# 3. Línea divisoria horizontal adaptable
GRmenu.div(60, "blue")

# 4. Pausa de consola que espera una sola tecla en modo TTY crudo
GRmenu.continue("Presiona cualquier tecla para continuar...")

# 5. Guía interactiva en consola
GRmenu.help
```

---

## 🐍 Ejemplo Completo en Python

```python
from GRmenu import GRmenu

def saludar():
    print("¡Hola desde Python!")

def acerca_de():
    print("GRmenu — Menús interactivos para terminal")

def salir_app():
    print("Hasta luego 👋")
    exit(0)

menu = GRmenu(
    [
        saludar,
        acerca_de,
        salir_app
    ],
    title="GRmenu Demo (Python)",
    style=7
)

menu.SetStyle.Border("magenta")
menu.SetStyle.Options("white")
menu.SetStyle.Focus("cyan", 2)
menu.draw(size_max=32)
```

---

## 📖 Referencia de la API

### 💎 Ruby

#### `GRmenu.new(functions, ...)`

| Parámetro        | Tipo       | Descripción |
|------------------|------------|-------------|
| `functions`      | `Array`    | Opciones a mostrar (`Method`, `Symbol`, `Array ["Nombre", acción]`, `Proc`/`lambda`). |
| `banner:`        | `String`   | Texto gigante a renderizar en arte ASCII 3D arriba del menú. |
| `title:`         | `String`   | Título en la cabecera del marco de opciones. |
| `subtitle:`      | `String`   | Subtítulo o descripción (soporta múltiples líneas con `\n`). |
| `font:`          | `Integer`  | Fuente ASCII 3D del banner (1 al 10, default 1). |
| `style:`         | `Integer`  | Estilo de marco para las opciones (1 al 20, default 19). |
| `banner_style:`  | `Integer`  | Estilo de marco para el banner (1 al 20, default 3). |
| `divider:`       | `Boolean`  | Dibuja líneas divisorias a la par del ancho del banner. |
| `center:`        | `Boolean`  | Centra simétricamente el subtítulo y menú de opciones (default `true`). |

#### `menu.set_style`

| Método                              | Descripción                              |
|-------------------------------------|-------------------------------------------|
| `set_style.font(id)`                | Cambia el tipo de fuente ASCII 3D (1..10). |
| `set_style.banner(color, level=2)`  | Color y brillo del banner ASCII 3D.       |
| `set_style.title(color, level=2)`   | Color y brillo del título del marco.      |
| `set_style.subtitle(color, level=1)`| Color y brillo del subtítulo.             |
| `set_style.divider(color, level=1)` | Color y brillo de las líneas divisorias.  |
| `set_style.border(color, level=1)`  | Color y brillo del marco de opciones.     |
| `set_style.options(color, level=1)` | Color y brillo de opciones no activas.    |
| `set_style.focus(color, level=2)`   | Color y brillo de la opción resaltada.    |

#### `menu.draw(size_max: 20)`

Inicia el menú interactivo con navegación por teclado y bloquea el hilo hasta que el usuario elige una opción (`Enter`) o sale (`q`).

---

### 🐍 Python

#### `GRmenu(functions, title="", style=19)`

| Parámetro   | Tipo             | Descripción                                      |
|-------------|------------------|---------------------------------------------------|
| `functions` | `list[Callable]` | Funciones a mostrar como opciones, en orden.      |
| `title`     | `str`            | Título mostrado en la cabecera del menú.          |
| `style`     | `int`            | Número de estilo de borde (1 al 20).              |

#### `menu.SetStyle`

| Método                          | Descripción                              |
|----------------------------------|-------------------------------------------|
| `SetStyle.Border(color, level=1)` | Color del marco del menú.                 |
| `SetStyle.Options(color, level=1)`| Color de las opciones sin seleccionar.    |
| `SetStyle.Focus(color, level=2)`  | Color de la opción resaltada.             |

#### `menu.draw(size_max=20)`

Dibuja el menú interactivo y ejecuta la función seleccionada al pulsar `Enter`.

---

## 🤝 Contribuir

Las contribuciones son bienvenidas. Podés abrir un [issue](https://github.com/JoseEduardoGR/GRmenu/issues) o enviar un pull request.

---

## 📄 Licencia

Distribuido bajo licencia [MIT](LICENSE).

<div align="center">

Hecho por [grcode](https://github.com/JoseEduardoGR)

</div>
