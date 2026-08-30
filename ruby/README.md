# GRmenu (Ruby) v3.0

**Suite TUI Profesional y Ligera para la Creacion de Interfaces de Linea de Comandos en Terminales TTY.**

Menus interactivos por teclado, seleccion multiple con casillas de verificacion, controles deslizantes en tiempo real, renderizado de imagenes ANSI TrueColor de 24 bits, modo cromatico RGB animado a 30 FPS, modales nativos de confirmacion y texto, buscador instantaneo en vivo, cuadriculas bidimensionales, barras de progreso y banners 3D sin dependencias externas.

[![Gem Version](https://badge.fury.io/rb/grmenu.svg)](https://badge.fury.io/rb/grmenu)
[![License: MIT](https://img.shields.io/github/license/JoseEduardoGR/GRmenu)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-blue)](https://github.com/JoseEduardoGR/GRmenu)
[![Ruby](https://img.shields.io/badge/ruby-%3E%3D%202.6-red.svg)](https://www.ruby-lang.org)

---

## Tabla de Contenidos

1. [Por que elegir GRmenu?](#-por-que-elegir-grmenu)
2. [Instalacion y Requisitos](#-instalacion-y-requisitos)
3. [Inicio Rapido en 10 Segundos](#-inicio-rapido-en-10-segundos)
4. [Guia de Componentes y Caracteristicas](#-guia-de-componentes-y-caracteristicas)
   - [1. Menu Interactivo Principal (Buscador, Grid 2D y Paginacion)](#1-menu-interactivo-principal)
   - [2. Seleccion Multiple con Checkboxes (GRmenu.checkbox)](#2-seleccion-multiple-con-checkboxes)
   - [3. Control Deslizante Interactivo (GRmenu.slider)](#3-control-deslizante-interactivo)
   - [4. Renderizado Universal de Imagenes (GRmenu.image)](#4-renderizado-universal-de-imagenes)
   - [5. Modales Nativos de Confirmacion y Entrada (confirm e input)](#5-modales-nativos-de-confirmacion-y-entrada)
   - [6. Modo RGB Chroma Wave Animado a 30 FPS](#6-modo-rgb-chroma-wave-animado)
   - [7. Barra de Progreso y Spinner de Carga](#7-barra-de-progreso-y-spinner-de-carga)
   - [8. Banners 3D y Lineas Divisorias](#8-banners-3d-y-lineas-divisorias)
   - [9. Modulo Independiente de Color (Color / C)](#9-modulo-independiente-de-color)
5. [Catalogo Visual de Fuentes 3D (1 al 10)](#-catalogo-visual-de-fuentes-3d)
6. [Catalogo Visual de Marcos y Bordes (1 al 20)](#-catalogo-visual-de-marcos-y-bordes)
7. [Referencia Exhaustiva de la API](#-referencia-exhaustiva-de-la-api)
8. [Mapa de Controles y Teclado](#-mapa-de-controles-y-teclado)
9. [Recetas y Casos de Uso del Mundo Real](#-recetas-y-casos-de-uso-del-mundo-real)
10. [Licencia](#-licencia)

---

## Por que elegir GRmenu?

- **Cero Dependencias Externas:** Funciona exclusivamente con la libreria estandar de Ruby (`io/console`, `json`, `zlib`), sin gemas pesadas ni binarios nativos requeridos.
- **Modo TTY Crudo Instantaneo:** Control milimetrico de la consola sin parpadeo de pantalla y con captura instantanea de eventos de teclado (0 ms de latencia).
- **Animaciones Sin Lag a 30 FPS:** Motor de renderizado reactivo no bloqueante basado en `IO.select` que permite efectos visuales dinamicos continuos sin saturar la CPU ni bloquear la entrada del usuario.
- **Multiplataforma Real:** Totalmente compatible con Linux, macOS y Windows (Windows Terminal, PowerShell, CMD y VS Code Terminal).
- **Diseno Modular y Expresivo:** Desde un simple menu de 3 lineas hasta complejas suites de instalacion, paneles DevOps o herramientas de configuracion.

---

## Instalacion y Requisitos

Requiere **Ruby >= 2.6.0**.

### Via RubyGems

```bash
gem install grmenu
```

### Via Gemfile

```ruby
gem 'grmenu', '~> 3.0'
```

### Requerimiento directo en scripts

```ruby
require 'GRmenu'
```

---

## Inicio Rapido en 10 Segundos

Crea un archivo llamado `app.rb` y ejecuta `ruby app.rb`:

```ruby
require 'GRmenu'

def iniciar_servicio
  GRmenu.clear_screen
  puts Color.bright_green("-> Servicio iniciado exitosamente en http://localhost:3000")
  GRmenu.continue
end

def ver_estado
  GRmenu.clear_screen
  puts Color.bright_cyan("-> Estado: Servidor Operativo | Memoria: 45 MB | Conexiones: 12")
  GRmenu.continue
end

menu = GRmenu.new(
  [
    ["Iniciar Servicio", method(:iniciar_servicio), "Lanza el worker en segundo plano"],
    ["Ver Estado", method(:ver_estado), "Muestra metricas de memoria y conexion"],
    ["Salir", -> { exit(0) }, "Finaliza la ejecucion"]
  ],
  title: "Panel de Control",
  banner: "MI APP",
  style: 3
)

menu.draw
```

---

## Guia de Componentes y Caracteristicas

### 1. Menu Interactivo Principal

El constructor `GRmenu.new` proporciona una experiencia interactiva completa con navegacion continua, paginacion automatica, buscador en vivo y organizacion en cuadricula 2D.

```text
╔═══════════════════════════════════════════╗
║             Panel de Control              ║
║═══════════════════════════════════════════║
║ Buscar: serv█                             ║
║═══════════════════════════════════════════║
║ > [X] Servidor Web Nginx                  ║
║   [ ] Servidor Base de Datos Postgres     ║
║───────────────────────────────────────────║
║ * Proxy inverso HTTP de alto rendimiento  ║
╚═══════════════════════════════════════════╝
```

#### Formatos de Opciones Aceptados

Puedes combinar cualquiera de los siguientes formatos en el array de opciones:

```ruby
menu = GRmenu.new(
  [
    # 1. Method directo (auto-formatea y capitaliza el nombre)
    method(:iniciar_servidor),

    # 2. Symbol (invoca el metodo global o del contexto)
    :crear_respaldo,

    # 3. Arreglo [Etiqueta, Accion]
    ["Lanzar Proceso", method(:lanzar)],

    # 4. Arreglo con Tooltip [Etiqueta, Accion, Descripcion]
    ["Limpieza de Cache", method(:limpiar), "Vacia los temporales en disco"],

    # 5. Bloque anonimo Proc o Lambda
    ["Accion Rapida", -> { puts "Ejecutado!"; GRmenu.continue }, "Ejecuta bloque inline"],

    # 6. Hash explicito
    { name: "Configuracion", action: method(:config), desc: "Ajustes del sistema" }
  ],
  title: "Consola de Administracion",
  banner: "SISTEMA",
  search: true,      # Activa buscador interactivo en vivo
  columns: 2,        # Cuadricula de 2 columnas con flechas izquierda/derecha
  page_size: 6,      # Paginacion con auto-scroll
  style: 3
)

menu.draw(size_max: 44)
```

---

### 2. Seleccion Multiple con Checkboxes

Permite al usuario seleccionar multiples elementos simultaneamente mediante casillas de verificacion interactivas `[X]` / `[ ]`.

```text
╔══════════════════ Instalador de Paquetes ══════════════════╗
║ [X] Servidor Nginx Web                                     ║
║ [X] Base de Datos PostgreSQL 16                            ║
║ [ ] Almacen de Cache Redis 7.2                             ║
║ [X] Monitor Prometheus                                     ║
║────────────────────────────────────────────────────────────║
║ Espacio: Marcar | a: Todos | n: Ninguno | Enter: Confirmar ║
╚════════════════════════════════════════════════════════════╝
```

#### Codigo de Ejemplo:

```ruby
paquetes = [
  ["Servidor Nginx Web", true, "Proxy inverso de alta velocidad"],
  ["Base de Datos PostgreSQL 16", true, "Motor de datos principal"],
  ["Almacen de Cache Redis 7.2", false, "Cache en memoria RAM"],
  ["Monitor Prometheus", true, "Metricas y alertas"]
]

seleccionados = GRmenu.checkbox(
  paquetes,
  title: "Instalador de Paquetes",
  color: "rgb",
  style: 3
)

puts "Elementos seleccionados: #{seleccionados.length}"
seleccionados.each do |elem|
  nombre = elem.is_a?(Array) ? elem[0] : elem
  puts " - [X] #{nombre}"
end
```

**Teclas de Control en Checkbox:**
- `Espacio`: Alterna entre marcado `[X]` y desmarcado `[ ]`.
- `a` / `A`: Marca todos los elementos (*Select All*).
- `n` / `N`: Desmarca todos los elementos (*Deselect All*).
- `i` / `I`: Invierte la seleccion actual.
- `Enter`: Confirma y devuelve el arreglo de elementos seleccionados.
- `q` / `Esc`: Cancela y devuelve un arreglo vacio `[]`.

---

### 3. Control Deslizante Interactivo

Permite seleccionar numericamente un valor o porcentaje dentro de un rango mediante una barra horizontal en tiempo real.

```text
╔══════════════ Asignar Memoria RAM ══════════════╗
║ [████████████████████░░░░░░░░░░] 16 GB          ║
║                                                 ║
║ ← / → Ajustar paso | ↑ / ↓ Salto x5 | Enter OK  ║
╚═════════════════════════════════════════════════╝
```

#### Codigo de Ejemplo:

```ruby
ram = GRmenu.slider(
  "Asignar Memoria RAM",
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

**Teclas de Control en Slider:**
- `←` / `→` o `h` / `l`: Ajusta el valor paso a paso (`step`).
- `↑` / `↓` o `k` / `j`: Salto rapido de 5 pasos.
- `Enter`: Guarda y retorna el numero exacto (`Integer` o `Float`).
- `q` / `Esc`: Cancela y retorna el valor por defecto.

---

### 4. Renderizado Universal de Imagenes

Decodifica y renderiza cualquier formato de imagen (PNG, JPEG, JPG, WEBP, GIF, BMP) con micro-pixeles ANSI TrueColor de 24 bits y escalado proporcional exacto.

#### Renderizado Directo en Consola:

```ruby
# Renderiza una imagen centrada dentro de un marco estilizado
GRmenu.image("fondo.jpg", width: 60, color: "rgb", style: 3)
```

#### Como Cabecera Superior en un Menu:

```ruby
menu = GRmenu.new(
  [
    ["Escanear Red", method(:escanear)],
    ["Ver Reporte", method(:reporte)],
    ["Salir", -> { exit(0) }]
  ],
  image: "logo.png",
  image_width: 44,
  title: "Security Toolset",
  style: 3
)

menu.draw
```

---

### 5. Modales Nativos de Confirmacion y Entrada

Cuadros de dialogo emergentes bloqueantes que capturan respuestas del usuario de forma directa y visual.

#### Modal de Confirmacion (`GRmenu.confirm`):

```ruby
# Dialogo interactivo Si / No con seleccion por flechas y teclado
if GRmenu.confirm("Deseas aplicar los cambios en produccion?", default: true, color: "rgb", style: 3)
  puts Color.bright_green("-> Cambios aplicados con exito.")
else
  puts Color.bright_red("-> Operacion cancelada.")
end
```

#### Cuadro de Entrada de Texto (`GRmenu.input`):

```ruby
# Entrada interactiva con cursor en vivo
nombre = GRmenu.input("Ingresa tu nombre de usuario:", default: "admin", color: "rgb", style: 3)

# Modo password para claves secretas (oculta caracteres con asteriscos)
token = GRmenu.input("Ingresa tu API Token:", password: true, color: "magenta", style: 7)
```

---

### 6. Modo RGB Chroma Wave Animado

Puedes activar el modo de color animado pasando `"rgb"`, `"rainbow"` o `"chroma"` a cualquier componente visual. El motor genera una onda sinusoidal horizontal que fluye suavemente a 30 FPS en segundo plano sin producir retraso en el teclado.

```ruby
menu = GRmenu.new(opciones, banner: "CHROMA", title: "RGB Wave Panel")

menu.set_style.banner("rgb")    # Letras 3D en degradado continuo
menu.set_style.title("rgb")     # Titulo de cabecera en RGB
menu.set_style.border("rgb")    # Marco exterior multicolor
menu.set_style.divider("rgb")   # Lineas divisorias animadas
menu.set_style.focus("rgb")     # Cursor enfocado pulsando en RGB
menu.set_style.options("rgb")   # Texto de opciones en tono suave

menu.draw
```

---

### 7. Barra de Progreso y Spinner de Carga

#### Barra de Progreso (`GRmenu.progress`):

```ruby
GRmenu.progress(100, title: "Descargando Actualizacion", color: "rgb", style: 3) do |bar|
  10.times do |i|
    sleep 0.1
    bar.advance(10, status: "Procesando bloque #{i + 1} de 10...")
  end
end
```

#### Spinner Animado (`GRmenu.spinner`):

```ruby
resultado = GRmenu.spinner("Conectando con el cluster remoto...", color: "rgb") do
  # Simula tarea pesada
  sleep 1.5
  "Conexion Establecida"
end

puts Color.bright_green("-> #{resultado}")
```

---

### 8. Banners 3D y Lineas Divisorias

```ruby
# Imprime un banner en arte ASCII 3D con retardo opcional de animacion
GRmenu.banner("ADMIN", 0, color: "rgb", style: 3, font: 1)

# Imprime una linea divisoria horizontal con ajuste automatico al ancho de terminal
GRmenu.div(60, "rgb", 1, "═")
```

---

### 9. Modulo Independiente de Color

El modulo `Color` (o su alias `C`) permite pintar cadenas de texto directamente con secuencias ANSI y TrueColor:

```ruby
# Modo Arcoiris RGB Dinamico
puts Color.rgb("Texto degradado en onda horizontal multicolor")

# Metodos directos por color (Nivel 1 Normal / Nivel 2 Brillante)
puts Color.bright_green("Verde brillante")
puts Color.bright_cyan("Cian brillante")
puts Color.bright_magenta("Magenta brillante")
puts Color.bright_yellow("Amarillo brillante")
puts Color.bright_red("Rojo brillante")
puts Color.orange("Naranja")
puts Color.purple("Morado")
puts Color.pink("Rosa")
puts Color.gray("Gris")
puts Color.white("Blanco")

# Atajos ultra-cortos de 1 o 2 letras
puts Color.g("Verde")
puts Color.cy("Cian")
puts Color.r("Rojo")
puts Color.y("Amarillo")
puts Color.w("Blanco")
puts Color.gr("Gris")
```

---

## Catalogo Visual de Fuentes 3D

Configura la tipografia mediante el parametro `font: 1..10`:

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

## Catalogo Visual de Marcos y Bordes

Configura el diseno del marco mediante el parametro `style: 1..20`:

| ID | Muestra | ID | Muestra | ID | Muestra | ID | Muestra |
|:--:|:--------|:--:|:--------|:--:|:--------|:--:|:--------|
| `1` | `#####` (Hash) | `6` | `╓───╖` (Mixto) | `11`| `░░░░░` (Sombra suave) | `16`| `~~~~~` (Ondas) |
| `2` | `┌───┐` (Simple) | `7` | `╭───╮` (Curvas) | `12`| `█████` (Bloque) | `17`| `-----` (Guion) |
| `3` | `╔═══╗` (Doble) | `8` | `▛▀▀▀▜` (Outline) | `13`| `*****` (Asterisco) | `18`| `◆◆◆◆◆` (Rombos) |
| `4` | `┏━━━┓` (Gruesa) | `9` | `▓▓▓▓▓` (Sombra oscura) | `14`| `+++++` (Cruces) | `19`| `●○○○●` (Circulos) |
| `5` | `╒═══╕` (Mixto) | `10`| `▒▒▒▒▒` (Sombra media) | `15`| `=====` (Doble simple) | `20`| `★☆☆☆★` (Estrellas) |

---

## Referencia Exhaustiva de la API

### Constructor `GRmenu.new(functions, **opciones)`

| Parametro | Tipo | Valor por Defecto | Descripcion |
|:----------|:-----|:------------------|:------------|
| `functions` | `Array` | *Obligatorio* | Lista de metodos, simbolos, arrays `[nombre, accion, tooltip]`, procs o hashes. |
| `title:` | `String` | `""` | Titulo centrado en la cabecera del marco de opciones. |
| `banner:` | `String` | `""` | Texto convertido a arte ASCII 3D superior. |
| `subtitle:` | `String` | `""` | Descripcion o subtitulo (soporta saltos de linea `\n`). |
| `search:` | `Boolean` | `false` | Activa el buscador instantaneo mientras se escribe. |
| `columns:` | `Integer` | `1` | Cantidad de columnas para distribucion en cuadricula 2D. |
| `page_size:` | `Integer` | `auto` | Maximo de filas visibles antes de activar desplazamiento con scroll. |
| `style:` | `Integer` | `19` | Estilo de marco para las opciones (1 al 20). |
| `banner_style:` | `Integer` | `3` | Estilo de marco para el banner 3D (1 al 20). |
| `font:` | `Integer` | `1` | Fuente tipografica del banner ASCII (1 al 10). |
| `image:` | `String` | `nil` | Ruta al archivo de imagen de cabecera (PNG/JPG/WEBP/GIF/BMP). |
| `image_width:` | `Integer` | `40` | Ancho en columnas para el renderizado de la imagen. |
| `divider:` | `Boolean/Int` | `true` | Lineas divisorias horizontales ajustadas al marco. |
| `center:` | `Boolean` | `true` | Centrado horizontal simetrico automatico. |

### Metodos de Estilo `menu.set_style`

| Metodo | Argumentos | Descripcion |
|:-------|:-----------|:------------|
| `banner(color, level=2)` | `(String, Integer)` | Color del banner ASCII (soporta `"rgb"`). |
| `title(color, level=2)` | `(String, Integer)` | Color del titulo del recuadro (soporta `"rgb"`). |
| `subtitle(color, level=1)` | `(String, Integer)` | Color del texto del subtitulo (soporta `"rgb"`). |
| `divider(color, level=1)` | `(String, Integer)` | Color de las lineas divisorias (soporta `"rgb"`). |
| `border(color, level=1)` | `(String, Integer)` | Color del marco de opciones (soporta `"rgb"`). |
| `options(color, level=1)` | `(String, Integer)` | Color de las opciones inactivas (soporta `"rgb"`). |
| `focus(color, level=2)` | `(String, Integer)` | Color del cursor y opcion activa (soporta `"rgb"`). |
| `font(font_id)` | `(Integer 1..10)` | Cambia la fuente tipografica del banner. |

### Metodos Estaticos y Modales

| Metodo | Firma | Retorno |
|:-------|:------|:--------|
| `GRmenu.checkbox` | `(items, title:, color:, style:, page_size:, preselected:)` | `Array` con los elementos marcados. |
| `GRmenu.slider` | `(prompt, min:, max:, step:, default:, unit:, color:, style:)` | `Numeric` con el valor seleccionado. |
| `GRmenu.confirm` | `(pregunta, default: true, color: "cyan", style: 3)` | `Boolean` (`true` para Si, `false` para No). |
| `GRmenu.input` | `(prompt, default: "", password: false, color: "cyan", style: 3)` | `String` ingresado por el usuario. |
| `GRmenu.image` | `(filepath, width: 40, height: nil, style: 3, color: "cyan")` | Dibuja la imagen en la terminal. |
| `GRmenu.progress` | `(total = 100, title: nil, color: "cyan", style: 3, &bloque)` | Ejecuta el bloque con la barra de progreso. |
| `GRmenu.spinner` | `(mensaje = "...", color: "cyan", delay: 0.08, &bloque)` | Ejecuta el bloque mostrando un spinner animado. |
| `GRmenu.banner` | `(texto, delay = 0, color: "magenta", style: 3, font: 1)` | Imprime texto en arte ASCII 3D. |
| `GRmenu.div` | `(long = nil, color = "blue", level = 1, char = "─")` | Imprime una linea divisoria en la consola. |
| `GRmenu.clear_screen`| `()` (Alias: `GRmenu.clr`) | Limpia la pantalla y el scrollback al instante. |
| `GRmenu.continue` | `(texto = "Presiona cualquier tecla...")` | Pausa la ejecucion hasta presionar una tecla. |
| `GRmenu.help` | `()` | Muestra la guia interactiva de documentacion en consola. |

---

## Mapa de Controles y Teclado

| Tecla / Combinacion | Contexto | Accion Realizada |
|:--------------------|:---------|:-----------------|
| `↑` (Arriba) / `k`  | Menus / Checkbox | Mueve el foco hacia arriba (con salto continuo *Snake* en extremos). |
| `↓` (Abajo) / `j`   | Menus / Checkbox | Mueve el foco hacia abajo. |
| `←` / `→`           | Grid 2D  | Salta de columna a la izquierda o derecha. |
| `Espacio`           | Checkbox | Marca o desmarca la casilla del elemento actual `[X]` / `[ ]`. |
| `a` / `A`           | Checkbox | Marca todos los elementos (*Select All*). |
| `n` / `N`           | Checkbox | Desmarca todos los elementos (*Deselect All*). |
| `i` / `I`           | Checkbox | Invierte la seleccion de todos los elementos. |
| `←` / `→` o `h` / `l`| Slider  | Ajusta el valor numerico en un incremento (`step`). |
| `↑` / `↓` o `k` / `j`| Slider  | Salto rapido de 5 pasos en el valor numerico. |
| `Enter`             | Global   | Ejecuta la accion seleccionada o confirma el formulario. |
| `q` / `Esc`         | Global   | Sale del menu o cancela la operacion actual. |
| `Backspace`         | Buscador / Input | Borra el ultimo caracter ingresado. |
| `Ctrl+U`            | Buscador / Input | Limpia todo el texto ingresado. |

---

## Recetas y Casos de Uso del Mundo Real

### Asistente de Instalacion de Servidores

```ruby
require 'GRmenu'

GRmenu.clear_screen
GRmenu.banner("SETUP", 0, color: "rgb", style: 3, font: 1)

nombre = GRmenu.input("Nombre del proyecto:", default: "mi-app", color: "rgb")
puerto = GRmenu.slider("Puerto HTTP:", min: 3000, max: 9000, step: 100, default: 8080, color: "rgb")

modulos = [
  ["Proxy Nginx", true, "Servidor web frontal"],
  ["Base PostgreSQL", true, "Base de datos relacional"],
  ["Redis Cache", false, "Acelerador de sesiones"]
]
seleccion = GRmenu.checkbox(modulos, title: "Selecciona Modulos", color: "rgb")

if GRmenu.confirm("Deseas comenzar la instalacion ahora?", default: true, color: "rgb")
  GRmenu.progress(100, title: "Instalando Componentes", color: "rgb") do |bar|
    seleccion.each_with_index do |item, idx|
      sleep 0.4
      bar.advance(100 / seleccion.length, status: "Configurando #{item[0]}...")
    end
  end
  puts Color.bright_green("\n-> Instalacion de '#{nombre}' completada en el puerto #{puerto}!")
end
GRmenu.continue
```

---

## Licencia

Distribuido bajo licencia **MIT**. Consulta [`LICENSE`](LICENSE) para mas detalles.

Desarrollado con precision por **[grcode](https://github.com/JoseEduardoGR)**

