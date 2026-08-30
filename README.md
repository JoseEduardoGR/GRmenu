<div align="center">

# GRmenu

**Suite TUI y Menus Interactivos para Terminal en Modo TTY Crudo**

Soporte completo para Ruby (v3.0) y Python (v0.2), con Banners ASCII 3D, seleccion multiple con checkboxes, sliders en tiempo real, visor de imagenes ANSI TrueColor, modo RGB animado a 30 FPS, modales nativos, buscador en vivo, cuadriculas 2D y barras de progreso sin dependencias externas.

| Ruby (Gema) | Python (PyPI) |
|:---:|:---:|
| [![Gem Version](https://img.shields.io/gem/v/grmenu)](https://rubygems.org/gems/grmenu) [![Gem Downloads](https://img.shields.io/gem/dt/grmenu)](https://rubygems.org/gems/grmenu) | [![PyPI version](https://img.shields.io/pypi/v/grmenu?color=blue&label=PyPI)](https://pypi.org/project/grmenu/) [![PyPI Downloads](https://static.pepy.tech/personalized-badge/grmenu?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=MAGENTA&left_text=downloads)](https://pepy.tech/projects/grmenu) |
| [![Ruby](https://img.shields.io/badge/ruby-%3E%3D%202.6-red.svg)](https://www.ruby-lang.org) | [![Python versions](https://img.shields.io/pypi/pyversions/grmenu)](https://pypi.org/project/grmenu/) |

[![License: MIT](https://img.shields.io/github/license/JoseEduardoGR/GRmenu)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-blue)](https://github.com/JoseEduardoGR/GRmenu)

![Demo de GRmenu](python/assets/demo.gif)

</div>

---

## Caracteristicas Principales

- **Navegacion intuitiva por teclado:** arriba/abajo con salto continuo (*Snake wrap*), `Enter` para ejecutar, `q` para salir.
- **Modo RGB Chroma Wave Animado (30 FPS, 0 Lag):** degradados fluidos en tiempo real para marcos, titulos, banners, opciones, barras de progreso y cursores sin retraso de CPU.
- **Seleccion Multiple con Checkboxes (`GRmenu.checkbox`):** lista interactiva con casillas `[X]` / `[ ]` (`Espacio`, marcar todos con `a`, ninguno con `n`, invertir con `i`).
- **Control Deslizante Interactivo (`GRmenu.slider` / `range`):** barra de nivel ajustable en tiempo real con flechas (`← / →`) para valores numericos y unidades.
- **Visor de Imagenes ANSI TrueColor de 24 bits (`GRmenu.image`):** decodifica y muestra fotos PNG, JPEG, JPG, WEBP, GIF y BMP con micro-pixeles y proporciones exactas.
- **Buscador en Vivo Instantaneo (`search: true`):** filtrado interactivo en tiempo real mientras el usuario escribe caracteres.
- **Cuadricula 2D / Multi-Columna (`columns: 2+`):** navegacion con las 4 flechas de direccion (`↑`, `↓`, `←`, `→`).
- **Modales y Dialogos Nativos (`confirm` e `input`):** cuadros emergentes para preguntas Si / No y entradas de texto con cursor o modo contrasena (`****`).
- **10 Fuentes ASCII 3D para Banners:** fuentes tridimensionales (ANSI Shadow, Slant, Doom, Graffiti, Modular, Wire, Block, Stars, etc.).
- **Auto-Paginacion y Scroll Fluido:** ventana deslizante con indicadores automaticos (`▲ (+N arriba)` / `▼ (+M abajo)`).
- **Descripciones y Tooltips Dinamicos:** muestra informacion explicativa al pie del marco para la opcion enfocada.
- **Spinners y Barras de Progreso:** helpers nativos `GRmenu.spinner` y `GRmenu.progress` dentro de recuadros con estetica integrada.
- **20 Estilos de Borde:** desde ASCII clasico hasta caracteres Unicode dobles, curvas redondeadas, sombreados y bloques.
- **100% Multiplataforma:** compatible con Linux, macOS y Windows Terminal.
- **Cero dependencias externas:** utiliza unicamente la libreria estandar (`io/console` en Ruby, `termios`/`tty` en Python).

---

## Instalacion

### Ruby (RubyGems)

```bash
gem install grmenu
```

O en tu `Gemfile`:

```ruby
gem 'grmenu', '~> 3.0'
```

### Python (PyPI)

```bash
pip install grmenu
```

---

## Uso Rapido

### Ruby

```ruby
require 'GRmenu'

def iniciar_servidor
  puts Color.bright_green("-> Servidor iniciado en puerto 3000...")
  GRmenu.continue
end

def ver_estado
  puts Color.bright_cyan("-> Estado: Operativo y estable")
  GRmenu.continue
end

menu = GRmenu.new(
  [
    ["Iniciar Servidor Web", method(:iniciar_servidor), "Lanza el proceso Puma en background"],
    ["Ver Estado del Sistema", method(:ver_estado), "Muestra metricas de CPU y memoria"]
  ],
  banner: "DEV OPS",
  title: "Panel Principal",
  search: true,
  style: 3
)

menu.set_style.banner("rgb")
menu.set_style.title("rgb")
menu.set_style.border("rgb")
menu.set_style.focus("rgb")
menu.draw
```

### Python

```python
from GRmenu import GRmenu

def opcion_uno():
    print("Elegiste uno")

def opcion_dos():
    print("Elegiste dos")

menu = GRmenu(
    [opcion_uno, opcion_dos],
    title="Mi Menu",
    style=19
)

menu.SetStyle.Border("yellow")
menu.SetStyle.Options("white")
menu.SetStyle.Focus("green", 2)
menu.draw()
```

---

## Nuevas Funcionalidades en Ruby (v3.0)

### 1. Seleccion Multiple con Checkboxes (`GRmenu.checkbox`)

```ruby
paquetes = [
  ["Servidor Nginx Web", true, "Proxy inverso de alta velocidad"],
  ["Base de Datos PostgreSQL", true, "Motor relacional principal"],
  ["Memoria Cache Redis", false, "Almacen en memoria"],
  ["Monitor Prometheus", false, "Metricas del cluster"]
]

seleccionados = GRmenu.checkbox(
  paquetes,
  title: "Instalador de Paquetes",
  subtitle: "Espacio: Marcar | a: Todos | n: Ninguno | i: Invertir | Enter: Confirmar",
  color: "rgb",
  style: 3
)

puts "Componentes seleccionados: #{seleccionados.length}"
```

---

### 2. Control Deslizante en Tiempo Real (`GRmenu.slider`)

```ruby
ram = GRmenu.slider(
  "Asignar Memoria RAM para Servidor",
  min: 1,
  max: 64,
  step: 1,
  default: 16,
  unit: "GB",
  color: "rgb",
  style: 3
)

puts "Memoria configurada: #{ram} GB"
```

---

### 3. Renderizado Universal de Imagenes en Terminal (`GRmenu.image`)

```ruby
# 1. Renderizado directo en consola
GRmenu.image("kali-dragon.png", width: 60, color: "rgb", style: 3)

# 2. Como cabecera en un menu interactivo
sub = GRmenu.new(
  [:opcion1, :opcion2],
  image: "fondo.jpeg",
  image_width: 44,
  title: "Galeria de Wallpapers"
)
sub.draw
```

---

### 4. Modales Nativos de Confirmacion y Texto (`confirm` / `input`)

```ruby
# Cuadro interactivo para entrada de texto
usuario = GRmenu.input("Ingresa tu nombre de usuario:", default: "admin", color: "rgb")

# Dialogo emergente Si / No
if GRmenu.confirm("Deseas activar privilegios para #{usuario}?", default: true, color: "rgb")
  puts Color.bright_green("-> Privilegios otorgados.")
end
```

---

### 5. Barra de Progreso y Spinner con Modo RGB

```ruby
# Barra de progreso con estado dinamico
GRmenu.progress(100, title: "Descargando Actualizacion", color: "rgb") do |bar|
  10.times do |i|
    sleep 0.1
    bar.advance(10, status: "Bloque #{i + 1}/10 procesado...")
  end
end

# Spinner animado para tareas en segundo plano
GRmenu.spinner("Verificando integridad del sistema...", color: "rgb") do
  sleep 1.2
end
```

---

## Ejemplo Completo de Uso (Ruby `e.rb`)

A continuacion se muestra el archivo [`ruby/e.rb`](ruby/e.rb) que incluye todos los componentes interactivos de la libreria:

```ruby
# frozen_string_literal: true

require "GRmenu"

def iniciar_servidor
  GRmenu.clear_screen
  puts Color.bright_green("-> Servidor iniciado en el puerto 3000.")
  GRmenu.continue
end

def demo_seleccion_multiple
  GRmenu.clear_screen
  paquetes = [
    ["Servidor Nginx Web", true, "Proxy inverso de alto rendimiento"],
    ["Motor PostgreSQL 16", true, "Base de datos relacional robusta"],
    ["Cache Redis 7.2", false, "Almacen clave-valor en memoria"],
    ["Visualizador Grafana", true, "Dashboards de analitica en tiempo real"]
  ]

  seleccionados = GRmenu.checkbox(paquetes, title: "Instalador de Paquetes", color: "rgb")
  GRmenu.clear_screen
  puts Color.bright_green("-> Paquetes seleccionados: #{seleccionados.length}")
  GRmenu.continue
end

def demo_slider_interactivo
  GRmenu.clear_screen
  ram = GRmenu.slider("Asignar Memoria RAM", min: 1, max: 64, default: 16, unit: "GB", color: "rgb")
  GRmenu.clear_screen
  puts Color.bright_green("-> Memoria configurada: #{ram} GB.")
  GRmenu.continue
end

def main
  menu = GRmenu.new(
    [
      method(:iniciar_servidor),
      ["Seleccion Multiple (Checkbox)", method(:demo_seleccion_multiple)],
      ["Control Deslizante (Slider)", method(:demo_slider_interactivo)],
      ["Salir", -> { exit(0) }]
    ],
    banner: "GRMENU",
    title: "Panel de Control v3.0",
    subtitle: "Consola de Administracion TTY\nUsa las flechas y Enter",
    style: 3,
    banner_style: 3
  )

  menu.set_style.banner("rgb")
  menu.set_style.title("rgb")
  menu.set_style.border("rgb")
  menu.set_style.focus("rgb")
  menu.draw(size_max: 42)
end

loop { main }
```

---

## Ejemplo Completo en Python

![Demo de GRmenu en Python](python/assets/demo.gif)

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

## 10 Fuentes ASCII 3D para Banners (`font: 1..10`)

| ID | Nombre de Fuente | Muestra Visual |
|:--:|:-----------------|:---------------|
| `1` | **ANSI Shadow 3D** *(Default)* | `██████╗  ██╗  ██╗` |
| `2` | **Slant 3D** | `    ____        __  __` |
| `3` | **Doom / Standard 3D** | `   ____      _   _` |
| `4` | **Graffiti Shadow 3D** | `  ,---.      ,--. ,--.` |
| `5` | **Small Slant / Mini 3D** | `   ___     _ _` |
| `6` | **Modular Pipe 3D** | `   _____    _____` |
| `7` | **Bubble / Round Gothic** | `    ____     _  _` |
| `8` | **Double-Line Wire 3D** | `  ╔═════╗  ║     ║` |
| `9` | **Solid Fat 3D Block** | `  ██████▄  ██   ██` |
| `10`| **Arcade Stars Matrix** | `  ★★★★   ★   ★` |

---

## 20 Estilos de Marco y Bordes (`style: 1..20`)

| ID | Muestra | ID | Muestra | ID | Muestra | ID | Muestra |
|:--:|:--------|:--:|:--------|:--:|:--------|:--:|:--------|
| `1` | `#####` | `6` | `╓───╖` | `11`| `░░░░░` | `16`| `~~~~~` |
| `2` | `┌───┐` | `7` | `╭───╮` | `12`| `█████` | `17`| `-----` |
| `3` | `╔═══╗` *(Doble)* | `8` | `▛▀▀▀▜` | `13`| `*****` | `18`| `◆◆◆◆◆` |
| `4` | `┏━━━┓` *(Gruesa)*| `9` | `▓▓▓▓▓` | `14`| `+++++` | `19`| `●○○○●` *(Opciones)* |
| `5` | `╒═══╕` | `10`| `▒▒▒▒▒` | `15`| `=====` | `20`| `★☆☆☆★` *(Estrellas)* |

---

## Paleta de Colores y Modulo `Color`

```ruby
# 1. Modo Arcoiris Chroma Dinamico
puts Color.rgb("Texto degradado en onda multicolor continua")

# 2. Metodos directos por color
puts Color.bright_green("Texto verde brillante")
puts Color.bright_cyan("Cian brillante")
puts Color.bright_magenta("Magenta brillante")
puts Color.bright_yellow("Texto amarillo brillante")
puts Color.orange("Texto naranja")
puts Color.purple("Texto morado")
puts Color.pink("Texto rosa")
puts Color.gray("Texto gris")
```

Colores soportados: `black`, `gray`, `red`, `green`, `yellow`, `blue`, `magenta`, `purple`, `pink`, `cyan`, `aqua`, `orange`, `white`.

---

## Referencia de la API

### Ruby

#### `GRmenu.new(functions, **opciones)`

| Parametro | Tipo | Default | Descripcion |
|:----------|:-----|:--------|:------------|
| `functions` | `Array` | *Requerido* | Opciones (`Method`, `Symbol`, `["Nombre", accion, tooltip]`, `Proc`). |
| `title:` | `String` | `""` | Titulo en la cabecera del marco de opciones. |
| `banner:` | `String` | `""` | Texto gigante a renderizar en arte ASCII 3D arriba del menu. |
| `subtitle:` | `String` | `""` | Subtitulo descriptivo (soporta multiples lineas con `\n`). |
| `search:` | `Boolean` | `false` | Activa buscador instantaneo interactivo mientras se escribe. |
| `columns:` | `Integer` | `1` | Cantidad de columnas para navegacion en cuadricula 2D. |
| `page_size:` | `Integer` | `auto` | Numero maximo de opciones visibles antes de auto-scroll. |
| `style:` | `Integer` | `19` | Estilo de marco para las opciones (1 al 20). |
| `banner_style:` | `Integer` | `3` | Estilo de marco para el banner (1 al 20). |
| `font:` | `Integer` | `1` | Fuente ASCII 3D del banner (1 al 10). |
| `image:` | `String` | `nil` | Ruta a imagen de cabecera (PNG/JPG/WEBP/GIF/BMP). |
| `image_width:` | `Integer` | `40` | Ancho en columnas de terminal para la imagen. |
| `divider:` | `Boolean/Int` | `true` | Lineas divisorias a la par del ancho del banner. |
| `center:` | `Boolean` | `true` | Centrado simetrico automatico del menu y subtitulo. |

#### `menu.set_style`

| Metodo | Argumentos | Descripcion |
|:-------|:-----------|:------------|
| `banner(color, level=2)` | `(String, Integer)` | Color del banner ASCII 3D (soporta `"rgb"`). |
| `title(color, level=2)` | `(String, Integer)` | Color del titulo del marco (soporta `"rgb"`). |
| `subtitle(color, level=1)` | `(String, Integer)` | Color del subtitulo (soporta `"rgb"`). |
| `divider(color, level=1)` | `(String, Integer)` | Color de las lineas divisorias (soporta `"rgb"`). |
| `border(color, level=1)` | `(String, Integer)` | Color del marco de opciones (soporta `"rgb"`). |
| `options(color, level=1)` | `(String, Integer)` | Color de opciones no activas (soporta `"rgb"`). |
| `focus(color, level=2)` | `(String, Integer)` | Color de la opcion resaltada (soporta `"rgb"`). |
| `font(font_id)` | `(Integer 1..10)` | Fuente tipografica del banner. |

---

### Python

#### `GRmenu(functions, title="", style=19)`

| Parametro | Tipo | Descripcion |
|:----------|:-----|:------------|
| `functions` | `list[Callable]` | Funciones a mostrar como opciones, en orden. |
| `title` | `str` | Titulo mostrado en la cabecera del menu. |
| `style` | `int` | Numero de estilo de borde (1 al 20). |

#### `menu.SetStyle`

| Metodo | Descripcion |
|:-------|:------------|
| `SetStyle.Border(color, level=1)` | Color del marco del menu. |
| `SetStyle.Options(color, level=1)`| Color de las opciones sin seleccionar. |
| `SetStyle.Focus(color, level=2)` | Color de la opcion resaltada. |

#### `menu.draw(size_max=20)`

Dibuja el menu interactivo y ejecuta la funcion seleccionada al pulsar `Enter`.

---

## Contribuir

Las contribuciones son bienvenidas. Puedes abrir un [issue](https://github.com/JoseEduardoGR/GRmenu/issues) o enviar un pull request.

---

## Licencia

Distribuido bajo licencia [MIT](LICENSE).

<div align="center">

Hecho por [grcode](https://github.com/JoseEduardoGR)

</div>
