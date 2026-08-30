<div align="center">

# GRmenu (Ruby)

**Menús interactivos por teclado para terminal en modo TTY crudo, con soporte para Banners ASCII 3D, barras de progreso, spinners animados, tooltips dinámicos, estilos y colores personalizados**

Flechas arriba/abajo para moverte · `Enter` para elegir · `q` para salir

[![Gem Version](https://badge.fury.io/rb/grmenu.svg)](https://badge.fury.io/rb/grmenu)
[![License: MIT](https://img.shields.io/github/license/JoseEduardoGR/GRmenu)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-blue)](https://github.com/JoseEduardoGR/GRmenu)

</div>

---

## ✨ Características

- 🎮 **Navegación con flechas** — arriba/abajo para moverte, `Enter` para ejecutar, `q` para salir.
- 🔤 **10 Fuentes ASCII 3D para Banners** — fuentes tridimensionales (ANSI Shadow, Slant, Doom, Graffiti, Modular, Wire, Block, Stars, etc.).
- 📜 **Auto-Paginación y Scroll Fluido** — calcula la altura de la terminal y crea una ventana deslizante con indicadores automáticos (`▲ (+N arriba)` / `▼ (+M abajo)`).
- 💡 **Descripciones y Tooltips Dinámicos** — muestra información explicativa en la parte inferior del recuadro al enfocar cada opción.
- ⏳ **Spinners y Barras de Progreso** — helpers nativos `GRmenu.spinner` y `GRmenu.progress` dentro de recuadros con la misma estética visual.
- 🎨 **20 estilos de borde** — desde ASCII clásico hasta caracteres Unicode dobles, curvas redondeadas y bloques outline.
- 🌈 **Paleta de colores completa** — personalización individual de marco, título, banner, subtítulo, divisores, opciones y foco activo con 2 niveles de brillo.
- 📐 **Centrado simétrico automático** — alinea y centra automáticamente subtítulos y menús de opciones respecto al ancho de banners grandes.
- 🛠️ **Helpers nativos en modo crudo** — `clear_screen`, `continue`, `banner`, `spinner`, `progress`, `div` y `help`.
- 💻 **100% Multiplataforma** — compatible con Linux, macOS y Windows (PowerShell, CMD, Windows Terminal, VS Code).
- 📦 **Cero dependencias externas** — utiliza únicamente la librería estándar `io/console` y `json`.

---

## 📦 Instalación

```bash
gem install grmenu
```

O si trabajás con el archivo directamente en tu proyecto:

```ruby
require "GRmenu"
```

<sub>Requiere Ruby ≥ 2.6.</sub>

---

## 💡 Cómo se pasan las opciones y todos los parámetros

`GRmenu` permite pasar métodos directos, símbolos, arreglos con nombres personalizados, bloques lambda/procs y **descripciones explicativas (tooltips)**:

```ruby
menu = GRmenu.new(
  [
    method(:iniciar_servidor),                                       # 1. Method (auto-capitaliza: "Iniciar Servidor")
    :crear_respaldo,                                                 # 2. Symbol (auto-capitaliza: "Crear Respaldo")
    ["Métricas del Sistema", method(:ver_metricas)],                 # 3. Array ["Nombre Personalizado", acción]
    ["Crear Backup", method(:respaldo), "Genera dump SQL de la BD"], # 4. Con Tooltip descriptivo al pie del marco
    ["Ejecutar Lambda", -> { puts Color.pink("Lambda!"); GRmenu.continue }, "Bloque anónimo Proc/Lambda"],
    ["Probar Banner Helper", method(:prueba_banner_rapido)],         # 5. Helper GRmenu.banner
    ["Ver Ayuda y Referencia", method(:ver_ayuda_completa)],         # 6. Helper GRmenu.help
    method(:salir)                                                   # 7. Salir
  ],
  banner: "DEV OPS",                                                 # Texto gigante en arte ASCII 3D
  title: "Panel de Control",                                         # Título en el marco de opciones
  subtitle: "Consola de Administración\nUsa las flechas y Enter",    # Subtítulo (soporta saltos de línea \n)
  font: 1,                                                           # Fuente del banner (1 al 10, default 1: ANSI Shadow 3D)
  style: 7,                                                          # Estilo de marco de opciones (1 al 20, ej: 7=redondeado, 3=doble)
  banner_style: 3,                                                   # Estilo de marco del banner (1 al 20, ej: 3=doble línea)
  divider: true,                                                     # Líneas divisorias a la par del banner (true, false o número)
  center: true,                                                      # Centrado automático del menú y subtítulo respecto al banner
  page_size: 8                                                       # (Opcional) Límite visible para auto-scroll y paginación
)
```

---

## 🌟 Ejemplo Completo de Uso (`e.rb`)

A continuación se muestra el archivo de ejemplo completo [`e.rb`](e.rb) con acciones, helpers de carga (`spinner` / `progress`), paginación, configuración de estilos, fuentes y colores:

```ruby
# frozen_string_literal: true

require "GRmenu"

# 1. Definición de acciones/métodos
def iniciar_servidor
  GRmenu.clear_screen
  # Helper Spinner: ejecuta un bloque mientras anima un spinner en tiempo real
  GRmenu.spinner("Iniciando servicios del clúster...", color: "cyan") do
    sleep 1.2
  end
  puts Color.bright_green("\n-> Servidor iniciado correctamente en http://localhost:3000")
  GRmenu.continue
end

def crear_respaldo
  GRmenu.clear_screen
  tablas = ["usuarios", "ventas", "productos", "facturas", "logs", "configuracion"]
  
  # Helper Progress: barra de progreso porcentual interactiva dentro de recuadro
  GRmenu.progress(tablas.length, title: "Generando Respaldo SQL", color: "magenta", style: 3) do |bar|
    tablas.each_with_index do |tabla, i|
      sleep 0.25
      bar.advance(1, status: "Exportando tabla: #{tabla} (#{i + 1}/#{tablas.length})")
    end
  end

  puts Color.bright_cyan("\n-> Respaldo guardado con éxito en: ./backup_#{Time.now.strftime('%Y%m%d')}.sql")
  GRmenu.continue
end

def ver_metricas
  GRmenu.clear_screen
  GRmenu.div(50, "magenta", 2, "═")
  puts Color.bright_yellow("           MÉTRICAS DEL SISTEMA EN VIVO")
  GRmenu.div(50, "magenta", 2, "═")
  puts "  #{Color.cyan("CPU:")}     #{Color.bright_green("[████░░░░░░░░░░░░] 24%")} (8 Cores)"
  puts "  #{Color.cyan("RAM:")}     #{Color.bright_green("[████████░░░░░░░░] 48%")} (7.8 GB / 16 GB)"
  puts "  #{Color.cyan("Red:")}     #{Color.bright_white("↑ 1.2 MB/s  ↓ 4.8 MB/s")}"
  puts "  #{Color.cyan("Estado:")}  #{Color.bright_green("● OPERATIVO")}"
  GRmenu.div(50, "magenta", 2, "═")
  GRmenu.continue
end

def prueba_banner_rapido
  GRmenu.clear_screen
  GRmenu.banner("OK", 0, color: "green", level: 2, style: 3, font: 1)
  GRmenu.div(40, "green", 1, "═")
  puts Color.green("  Prueba de Banner completada con éxito.")
  GRmenu.div(40, "green", 1, "═")
  GRmenu.continue
end

def prueba_paginacion
  GRmenu.clear_screen
  opciones_largas = (1..25).map do |n|
    ["Elemento del Sistema ##{n}", -> {
      GRmenu.clear_screen
      puts Color.bright_cyan("-> Has seleccionado el Elemento ##{n}")
      GRmenu.continue
    }, "Descripción detallada del registro ##{n} en la base de datos"]
  end

  sub_menu = GRmenu.new(
    opciones_largas,
    title: "Lista con Auto-Paginación",
    subtitle: "Navega con ↑ / ↓ para ver el desplazamiento suave",
    style: 7,
    page_size: 7
  )
  sub_menu.draw(size_max: 42)
end

def ver_ayuda_completa
  GRmenu.clear_screen
  GRmenu.help
  GRmenu.continue
end

def salir
  GRmenu.clear_screen
  puts Color.bright_yellow("¡Sesión finalizada con éxito!")
  exit(0)
end

# 2. Instanciación del menú con TODOS los parámetros disponibles
def main
  menu = GRmenu.new(
    [
      ["Iniciar Servidor",        method(:iniciar_servidor),      "Arranca los servicios HTTP y WebSocket en segundo plano"],
      ["Crear Respaldo",          method(:crear_respaldo),        "Genera un dump SQL completo con barra de progreso"],
      ["Métricas del Sistema",    method(:ver_metricas),          "Muestra el uso de CPU, RAM y red en tiempo real"],
      ["Lista Paginada (25 ítems)", method(:prueba_paginacion),   "Prueba la paginación y auto-scroll con 25 elementos"],
      ["Ejecutar Lambda",         -> { puts Color.pink("¡Lambda!"); GRmenu.continue }, "Ejecuta un bloque anónimo Proc/Lambda"],
      ["Probar Banner Helper",    method(:prueba_banner_rapido),  "Muestra un banner ASCII 3D con colores"],
      ["Ver Ayuda y Referencia",  method(:ver_ayuda_completa),    "Abre la guía de comandos y referencias de la gema"],
      ["Salir",                   method(:salir),                 "Cierra el programa de forma segura"]
    ],
    banner: " gr codE ",
    title: "Panel de Control",
    subtitle: "Consola de Administración TTY\nUsa ↑ / ↓ para navegar y Enter para seleccionar",
    style: 3,
    banner_style: 3,
    divider: true,
    center: true
  )

  # 3. Configuración completa de colores y estilos
  menu.set_style.font(1)             # 1 = ANSI Shadow 3D
  menu.set_style.banner("cyan", 2)   # Color del banner ASCII
  menu.set_style.title("yellow", 2)  # Color del título del recuadro
  menu.set_style.subtitle("white", 1)# Color del subtítulo
  menu.set_style.divider("blue", 1)  # Color de las líneas divisorias
  menu.set_style.border("yellow", 1) # Color del borde del marco de opciones
  menu.set_style.options("white", 1) # Color de opciones no seleccionadas
  menu.set_style.focus("green", 2)   # Color y brillo de la opción resaltada

  # 4. Dibujar y lanzar el menú interactivo
  menu.draw(size_max: 44)
end

main
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

# 3. Spinner animado en tiempo real mientras corre un bloque
GRmenu.spinner("Conectando al clúster...", color: "green") do
  hacer_tarea_pesada()
end

# 4. Barra de progreso porcentual dentro de un recuadro estilizado
GRmenu.progress(10, title: "Exportando Datos", color: "cyan") do |bar|
  10.times { |i| bar.advance(1, status: "Paso #{i + 1}/10") }
end

# 5. Línea divisoria horizontal adaptable
GRmenu.div(60, "blue")

# 6. Pausa de consola que espera una sola tecla en modo TTY crudo
GRmenu.continue("Presiona cualquier tecla para continuar...")

# 7. Guía interactiva en consola
GRmenu.help
```

---

## 📖 Referencia de la API

### `GRmenu.new(functions, ...)`

| Parámetro        | Tipo       | Descripción |
|------------------|------------|-------------|
| `functions`      | `Array`    | Opciones a mostrar (`Method`, `Symbol`, `Array ["Nombre", acción, "Descripción"]`, `Proc`/`lambda`). |
| `banner:`        | `String`   | Texto gigante a renderizar en arte ASCII 3D arriba del menú. |
| `title:`         | `String`   | Título en la cabecera del marco de opciones. |
| `subtitle:`      | `String`   | Subtítulo o descripción (soporta múltiples líneas con `\n`). |
| `font:`          | `Integer`  | Fuente ASCII 3D del banner (1 al 10, default 1). |
| `style:`         | `Integer`  | Estilo de marco para las opciones (1 al 20, default 19). |
| `banner_style:`  | `Integer`  | Estilo de marco para el banner (1 al 20, default 3). |
| `divider:`       | `Boolean`  | Dibuja líneas divisorias a la par del ancho del banner. |
| `center:`        | `Boolean`  | Centra simétricamente el subtítulo y menú de opciones (default `true`). |
| `page_size:`     | `Integer`  | (Opcional) Número máximo de opciones visibles en pantalla para auto-paginación. |

### `GRmenu.spinner(message, color: "cyan", &block)`

Ejecuta un bloque en segundo plano mientras dibuja una animación giratoria y muestra `✔ Mensaje ¡Listo!` al terminar.

### `GRmenu.progress(total, title:, color:, style:, &block)`

Crea una barra de progreso porcentual dentro de un recuadro estilizado. El bloque recibe el objeto `bar` con los métodos `bar.advance(n, status:)` y `bar.set(valor, status:)`.

### `menu.set_style`

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

### `menu.draw(size_max: 20)`

Inicia el menú interactivo con navegación por teclado y bloquea el hilo hasta que el usuario elige una opción (`Enter`) o sale (`q`).

---

## 🤝 Contribuir

Las contribuciones son bienvenidas. Podés abrir un [issue](https://github.com/JoseEduardoGR/GRmenu/issues) o enviar un pull request.

---

## 📄 Licencia

Distribuido bajo licencia [MIT](LICENSE).

<div align="center">

Hecho por [grcode](https://github.com/JoseEduardoGR)

</div>
