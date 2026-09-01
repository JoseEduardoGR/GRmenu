# GRmenu (Ruby) v4.0

**Suite TUI Profesional y Ligera para la Creacion de Interfaces de Linea de Comandos en Terminales TTY.**

Menus interactivos por teclado, tablas con ordenamiento y busqueda en vivo, seleccion multiple con casillas de verificacion, controles deslizantes en tiempo real, renderizado de imagenes ANSI TrueColor de 24 bits, sistema de temas estilo CSS `.gr`, iluminacion dinamica a 30 FPS en vivo, colores hexadecimales directos, modales nativos de confirmacion y texto, buscador instantaneo en vivo, cuadriculas bidimensionales, barras de progreso y banners 3D sin dependencias externas.

[![Gem Version](https://badge.fury.io/rb/grmenu.svg)](https://badge.fury.io/rb/grmenu)
[![License: MIT](https://img.shields.io/github/license/JoseEduardoGR/GRmenu)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-blue)](https://github.com/JoseEduardoGR/GRmenu)
[![Ruby](https://img.shields.io/badge/ruby-%3E%3D%202.6-red.svg)](https://www.ruby-lang.org)

![Demo de GRmenu en Ruby](assets/demo.png)

---

## Tabla de Contenidos

1. [Por que elegir GRmenu?](#por-que-elegir-grmenu)
2. [Instalacion y Requisitos](#instalacion-y-requisitos)
3. [Inicio Rapido en 10 Segundos](#inicio-rapido-en-10-segundos)
4. [Guia de Componentes y Caracteristicas](#guia-de-componentes-y-caracteristicas)
   - [1. Menu Interactivo Principal (Buscador, Grid 2D y Paginacion)](#1-menu-interactivo-principal)
   - [2. Sistema de Temas .gr y CSS para TUI](#2-sistema-de-temas-gr-y-css-para-tui)
   - [3. Exportacion de Temas desde Terminal / CLI](#3-exportacion-de-temas-desde-terminal--cli)
   - [4. CSS Inline en el Codigo (<<-GR)](#4-css-inline-en-el-codigo--gr)
   - [5. Tablas Interactivas con Buscador y Ordenamiento (GRmenu.table)](#5-tablas-interactivas-con-buscador-y-ordenamiento)
   - [6. Tarjetas y Alertas Estilizadas (GRmenu.card y GRmenu.alert)](#6-tarjetas-y-alertas-estilizadas)
   - [7. Colores Hexadecimales TrueColor y Catalogo de 90+ Colores](#7-colores-hexadecimales-truecolor-y-catalogo-de-90-colores)
   - [8. Iluminacion Dinamica Living Neon a 30 FPS](#8-iluminacion-dinamica-living-neon-a-30-fps)
   - [9. Seleccion Multiple con Checkboxes (GRmenu.checkbox)](#9-seleccion-multiple-con-checkboxes)
   - [10. Control Deslizante Interactivo (GRmenu.slider)](#10-control-deslizante-interactivo)
   - [11. Modales Nativos de Confirmacion y Entrada (confirm e input)](#11-modales-nativos-de-confirmacion-y-entrada)
   - [12. Renderizado Universal de Imagenes (GRmenu.image)](#12-renderizado-universal-de-imagenes)
   - [13. Barra de Progreso y Spinner de Carga](#13-barra-de-progreso-y-spinner-de-carga)
   - [14. Banners 3D y Modulo de Color (Color / C)](#14-banners-3d-y-modulo-de-color)
5. [Ejemplo Completo en Ruby (e.rb)](#ejemplo-completo-en-ruby-erb)
6. [Catalogo Visual de Fuentes 3D (1 al 10)](#catalogo-visual-de-fuentes-3d)
7. [Catalogo Visual de Marcos y Bordes (1 al 20)](#catalogo-visual-de-marcos-y-bordes)
8. [Referencia Exhaustiva de la API](#referencia-exhaustiva-de-la-api)
9. [Mapa de Controles y Teclado](#mapa-de-controles-y-teclado)
10. [Licencia](#licencia)

---

## Por que elegir GRmenu?

- **Cero Dependencias Externas:** Funciona exclusivamente con la libreria estandar de Ruby (`io/console`, `json`, `zlib`), sin gemas pesadas ni binarios nativos requeridos.
- **Sistema de Temas CSS (.gr):** Diseña la estetica de tu consola como si fuera una hoja de estilos web con bloques `<<menu`, `<<table`, `<<card`, `<<slider`, etc.
- **Colores Hexadecimales Directos:** Soporta `#FF0055`, `#00F5FF`, `#0FF` en cualquier componente con TrueColor de 24 bits nativo.
- **Animaciones Living Neon a 30 FPS:** Olas de luz senoidal continuas y destello de incandescencia en marcos y banners sin producir retraso en el teclado.
- **Exportacion Instantanea CLI:** Convierte la configuracion visual de cualquier script a un archivo de tema `.gr` reutilizable con la bandera `-theme`.
- **Modo TTY Crudo Instantaneo:** Control milimetrico de la consola sin parpadeo de pantalla y con captura instantanea de eventos de teclado (0 ms de latencia).
- **Multiplataforma Real:** Totalmente compatible con Linux, macOS y Windows (Windows Terminal, PowerShell, CMD y VS Code Terminal).

---

## Instalacion y Requisitos

Requiere **Ruby >= 2.6.0**.

### Via RubyGems

```bash
gem install grmenu
```

### Via Gemfile

```ruby
gem 'grmenu', '~> 4.0'
```

### Requerimiento directo en scripts

Puedes requerirlo tanto en minusculas como con la sintaxis tradicional:

```ruby
require 'grmenu'  # o require 'GRmenu'
```

---

## Inicio Rapido en 10 Segundos

Crea un archivo llamado `app.rb` y ejecuta `ruby app.rb`:

```ruby
require 'grmenu'

# Cargar un tema predefinido con estetica neon
GRmenu.theme(:neon_red)

def saludar
  GRmenu.alert(:success, "Bienvenido a GRmenu v4.0!")
end

def ver_tabla
  headers = ["ID", "SERVICIO", "ESTADO"]
  filas = [
    ["01", "API Gateway", "Operativo"],
    ["02", "Postgres DB", "Operativo"],
    ["03", "Redis Cache", "En espera"]
  ]
  GRmenu.table(headers: headers, rows: filas, title: "Monitor de Servidores", search: true)
end

menu = GRmenu.new(
  [
    ["Saludar", method(:saludar), "Muestra un mensaje emergente"],
    ["Ver Infraestructura", method(:ver_tabla), "Tabla interactiva con buscador en vivo"],
    ["Salir", -> { exit(0) }, "Finaliza la ejecucion"]
  ],
  title: "Panel de Control",
  banner: "DEMO",
  style: 3,
  animate: "diagonal"
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

### 2. Sistema de Temas .gr y CSS para TUI

GRmenu incluye un motor de temas declarativos en archivos `.gr` con sintaxis limpia tipo CSS.

#### Cargar Temas Integrados:
```ruby
GRmenu.theme(:neon_red)    # Rojos electricos incandescentes y foco amarillo
GRmenu.theme(:cyberpunk)   # Neones cian, amarillo y efecto Chroma
GRmenu.theme(:matrix)      # Verde fosforescente terminal hacker
GRmenu.theme(:dracula)     # Morados, fucsias y cian
GRmenu.theme(:nord)        # Azules articos y paleta fria
GRmenu.theme(:monokai)     # Amarillos, verdes y magentas
GRmenu.theme(:sunset)      # Atardecer calido en rojos, naranjas y dorados
```

#### Crear tu propio Archivo de Tema (`mi_tema.gr`):
```gr
GRmenu::config<-1->

@theme:: "Neon Tokyo"
@author:: "TuNombre"
@version:: "1.0"

<<menu
  style:: 3
  banner_style:: 3
  font:: 1
  animate:: diagonal
  desc_prefix:: ->
  center:: true
  border:: #FF0055
  title:: #00F5FF
  focus:: gold:2
  options:: white:1
  banner:: #FF0055
  subtitle:: #A6E3A1
  divider:: #FF0055
>>

<<table
  style:: 3
  header_color:: #00F5FF
  border_color:: #FF0055
  selected_row:: gold:2
  row_color:: white:1
  zebra_striping:: true
>>

<<card
  style:: 7
  border_color:: #FF0055
  title_color:: #00F5FF
  content_color:: white:1
>>

<<slider
  style:: 3
  color:: #FF0055
  fill_char:: █
  empty_char:: ░
>>

<<checkbox
  style:: 3
  color:: #FF0055
  checked_mark:: [X]
  unchecked_mark:: [ ]
>>
```

Para aplicarlo a todo tu sistema:
```ruby
GRmenu.import_config("mi_tema.gr")
```

---

### 3. Exportacion de Temas desde Terminal / CLI

Puedes extraer y exportar el tema configurado en cualquier script de Ruby directamente a un archivo `.gr`:

#### Mediante banderas de linea de comandos:
```bash
# Exporta el tema del script con nombre automatico:
ruby mi_app.rb -theme

# Exporta a un archivo de salida especifico:
ruby mi_app.rb -theme -o salida_tema.gr
```

#### De forma programatica en Ruby:
```ruby
# Extrae el tema de un script sin ejecutar bucles interactivos:
GRmenu.export_from_file("mi_app.rb", "tema_extraido.gr")

# Exporta el tema de una instancia existente:
menu.export_theme("mi_tema.gr")
```

---

### 4. CSS Inline en el Codigo (`<<-GR`)

Puedes inyectar bloques de estilo tipo `<style>` directamente en tu script sin crear archivos `.gr` adicionales:

```ruby
menu = GRmenu.new(opciones, title: "App con CSS")

menu.style(<<-GR)
<<menu
  style:: 3
  animate:: diagonal
  border:: #FF0055:1
  title:: #00F5FF:2
  focus:: gold:2
  banner:: neon_crimson:2
  subtitle:: #A6E3A1:1
>>
GR

menu.draw
```

---

### 5. Tablas Interactivas con Buscador y Ordenamiento

Visualiza y navega colecciones de datos tabulares con buscador instantaneo, ordenamiento por columnas con la tecla `s`, paginacion y proteccion anti-desbordes:

```text
╔════════════════ Monitor de Infraestructura ════════════════╗
║ Buscar: gate█                                              ║
║════════════════════════════════════════════════════════════║
║ ID    │ SERVICIO         │ ESTADO        │ LATENCIA        ║
║───────┼──────────────────┼───────────────┼─────────────────║
║ > 01  │ API Gateway      │ Operativo     │ 12ms            ║
║────────────────────────────────────────────────────────────║
║ ↑/↓ Mover | s Ordenar | / Buscar | Enter Seleccionar       ║
╚════════════════════════════════════════════════════════════╝
```

```ruby
headers = ["ID", "SERVICIO", "ESTADO", "LATENCIA"]
filas = [
  ["01", "API Gateway", "Operativo", "12ms"],
  ["02", "PostgreSQL Primary", "Operativo", "2ms"],
  ["03", "Redis Cache", "Operativo", "1ms"],
  ["04", "Workers Celery", "Ocupado", "45ms"],
  ["05", "ElasticSearch", "Operativo", "8ms"]
]

seleccion = GRmenu.table(
  headers: headers,
  rows: filas,
  title: "Monitor de Infraestructura",
  search: true,    # Buscador en vivo
  sort: true,      # Ordena por columnas con la tecla 's'
  page_size: 5,
  style: 3
)

if seleccion
  puts "Fila elegida: #{seleccion.join(' | ')}"
end
```

---

### 6. Tarjetas y Alertas Estilizadas

Cuadros informativos con division de parrafos (*word-wrapping*) automatico y soporte completo para colores TrueColor y Neón:

```ruby
# Alertas con iconos y colores contextuales
GRmenu.alert(:success, "Conexion establecida con el servidor.")
GRmenu.alert(:warning, "Memoria RAM al 85%.")
GRmenu.alert(:error, "Fallo en la peticion al cluster.")
GRmenu.alert(:info, "Actualizacion disponible.")

# Tarjeta informativa con bordes y colores personalizados
GRmenu.card(
  title: "Metricas de Produccion",
  content: "Peticiones/seg: 18,400 req/s\nLatencia p99: 11.4 ms\nSalud del cluster: 100%",
  border_color: "#FF0055",
  title_color: "#00F5FF",
  content_color: "gold",
  style: 7
)
```

---

### 7. Colores Hexadecimales TrueColor y Catalogo de 90+ Colores

El motor soporta **colores hexadecimales directos de 24 bits** (`#RRGGBB` o formato corto `#RGB`), ademas de un catalogo de 90+ colores pre-calibrados con version normal y version neón:

```ruby
# 1. En codigo con encadenamiento fluido (chaining):
menu.set_style.border("#FF0055").title("#00F5FF").focus("gold")

# 2. Con codigos de 3 digitos:
menu.set_style.border("#0FF")

# 3. Directamente con el helper de Color:
puts Color.hex("#A6E3A1", "Verde menta suave")
puts Color.gold("Texto Dorado")
puts Color.neon_emerald("Esmeralda Neon")
puts Color.crimson("Rojo Carmesi")
```

#### Familias de Colores Destacadas:
- **Metales y Joyas:** `gold` / `neon_gold`, `silver` / `neon_silver`, `platinum` / `neon_platinum`, `ruby` / `neon_ruby`, `emerald` / `neon_emerald`, `sapphire` / `neon_sapphire`.
- **Fuego y Tierra:** `crimson` / `neon_crimson`, `scarlet` / `neon_scarlet`, `coral` / `neon_coral`, `amber` / `neon_amber`.
- **Naturaleza y Pasteles:** `lime` / `neon_lime`, `mint` / `neon_mint`, `peach` / `neon_peach`, `lavender` / `neon_lavender`, `mauve` / `neon_mauve`.
- **Ciberpunk y Monitores:** `neon_red`, `neon_cyan`, `neon_pink`, `matrix` / `neon_matrix`, `charcoal`.

---

### 8. Iluminacion Dinamica Living Neon a 30 FPS

Al configurar `animate: "diagonal"`, `"linear"` o `"fade"`, el motor no se queda estatico: proyecta una ola de luz senoidal continua en tiempo real a 30 FPS que barre los marcos y los banners con destellos de incandescencia (*glow*), sin introducir ningun lag al pulsar teclas:

```ruby
menu = GRmenu.new(
  opciones,
  banner: "THEMES",
  title: "Efecto Neon Vivo",
  style: 3,
  animate: "diagonal" # "diagonal", "linear", "fade" o "rgb"
)
menu.set_style.border("neon_red").banner("neon_red").focus("neon_yellow")
menu.draw
```

---

### 9. Seleccion Multiple con Checkboxes

Permite al usuario seleccionar multiples elementos simultaneamente mediante casillas de verificacion interactivas `[X]` / `[ ]`.

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
  color: "neon_cyan",
  style: 3
)
```

**Teclas de Control:**
- `Espacio`: Alterna marcado `[X]` / `[ ]`.
- `a`: Seleccionar todos.
- `n`: Deseleccionar todos.
- `i`: Invertir seleccion.
- `Enter`: Confirmar seleccion.

---

### 10. Control Deslizante Interactivo

Permite seleccionar numericamente un valor o porcentaje dentro de un rango mediante una barra horizontal en tiempo real.

```ruby
ram = GRmenu.slider(
  "Asignar Memoria RAM",
  min: 1,
  max: 64,
  step: 1,
  default: 16,
  unit: "GB",
  color: "gold",
  style: 3
)
```

---

### 11. Modales Nativos de Confirmacion y Entrada

```ruby
# Modal Si / No con flechas
if GRmenu.confirm("Deseas aplicar los cambios en produccion?", color: "neon_green", style: 3)
  puts "Aplicando..."
end

# Cuadro de entrada de texto con cursor en vivo
nombre = GRmenu.input("Ingresa tu nombre de usuario:", default: "admin", color: "neon_cyan", style: 3)

# Modo password para ocultar claves
token = GRmenu.input("Ingresa tu API Token:", password: true, color: "neon_pink", style: 7)
```

---

### 12. Renderizado Universal de Imagenes

Decodifica y renderiza cualquier formato de imagen (PNG, JPEG, JPG, WEBP, GIF, BMP) con micro-pixeles ANSI TrueColor de 24 bits:

```ruby
GRmenu.image("wallpaper.jpg", width: 60, color: "neon_cyan", style: 3)
```

---

### 13. Barra de Progreso y Spinner de Carga

```ruby
# Barra de progreso
GRmenu.progress(100, title: "Descargando Actualizacion", color: "neon_yellow", style: 3) do |bar|
  10.times do |i|
    sleep 0.1
    bar.advance(10, status: "Procesando bloque #{i + 1} de 10...")
  end
end

# Spinner animado en segundo plano
resultado = GRmenu.spinner("Conectando con el cluster remoto...", color: "neon_cyan") do
  sleep 1.2
  "OK"
end
```

---

### 14. Banners 3D y Modulo de Color

```ruby
# Banner ASCII 3D
GRmenu.banner("ADMIN", 0, color: "neon_red", style: 3, font: 1)

# Modulo Color / C
puts Color.rgb("Texto degradado arcoiris continuo")
puts Color.hex("#FF0055", "Texto en Rojo Carmesi")
puts Color.gold("Texto en Dorado")
puts Color.neon_cyan("Texto en Cian Neon")
```

---

## Ejemplo Completo en Ruby (`e.rb`)

Puedes ejecutar el archivo de laboratorio interactivo completo:

```bash
ruby ruby/e.rb
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
| `animate:` | `String/Bool`| `false` | Efecto de iluminacion ("diagonal", "linear", "fade", "rgb"). |
| `desc_prefix:` | `String` | `"[i]"` | Prefijo visual para el tooltip de ayuda. |
| `divider:` | `Boolean/Int` | `true` | Lineas divisorias horizontales ajustadas al marco. |
| `center:` | `Boolean` | `true` | Centrado horizontal simetrico automatico. |

### Metodos Estaticos y Componentes

| Metodo | Firma | Retorno |
|:-------|:------|:--------|
| `GRmenu.theme` | `(nombre_o_simbolo)` | Carga un tema `.gr` predefinido para todo el sistema. |
| `GRmenu.import_config` | `(ruta_archivo_gr)` | Carga un archivo de tema `.gr` personalizado. |
| `GRmenu.export_from_file`| `(script_origen, archivo_gr)` | Extrae el tema de un script sin correr bucles. |
| `GRmenu.style` | `(texto_css_gr)` | Inyecta estilos CSS inline globalmente. |
| `GRmenu.table` | `(headers:, rows:, title:, search:, sort:, page_size:)` | Muestra tabla interactiva y devuelve fila elegida. |
| `GRmenu.card` | `(title:, content:, style:, color:, border_color:, title_color:)` | Muestra tarjeta con auto-wrap. |
| `GRmenu.alert` | `(tipo, mensaje, title:, style:, color:)` | Muestra alerta emergente estilizada. |
| `GRmenu.checkbox` | `(items, title:, color:, style:, preselected:)` | Devuelve array con items marcados. |
| `GRmenu.slider` | `(prompt, min:, max:, step:, default:, unit:, color:)` | Devuelve valor numerico seleccionado. |
| `GRmenu.confirm` | `(pregunta, default: true, color:, style:)` | Devuelve booleano (`true`/`false`). |
| `GRmenu.input` | `(prompt, default: "", password: false, color:)` | Devuelve string ingresado. |
| `GRmenu.image` | `(filepath, width:, style:, color:)` | Renderiza imagen en TrueColor 24-bit. |
| `GRmenu.progress` | `(total = 100, title:, color:, style:, &bloque)` | Barra de progreso con bloque. |
| `GRmenu.spinner` | `(mensaje, color:, delay:, &bloque)` | Spinner animado no bloqueante. |
| `GRmenu.banner` | `(texto, delay = 0, color:, style:, font:)` | Imprime banner ASCII 3D. |
| `GRmenu.help` | `()` | Muestra guia de documentacion en consola. |

---

## Mapa de Controles y Teclado

| Tecla / Combinacion | Contexto | Accion Realizada |
|:--------------------|:---------|:-----------------|
| `↑` (Arriba) / `k`  | Menus / Tablas / Checkbox | Mueve el foco hacia arriba (con salto continuo *Snake* en extremos). |
| `↓` (Abajo) / `j`   | Menus / Tablas / Checkbox | Mueve el foco hacia abajo. |
| `←` / `→`           | Grid 2D  | Salta de columna a la izquierda o derecha. |
| `s` / `S`           | Tablas   | Ordena la tabla por la columna actual alternando ASC/DESC. |
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

## Licencia

Distribuido bajo licencia **MIT**. Consulta [`LICENSE`](LICENSE) para mas detalles.

Desarrollado con precision por **[grcode](https://github.com/JoseEduardoGR)**
