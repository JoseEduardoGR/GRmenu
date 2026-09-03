# GRmenu (Ruby) v4.0.1

**Suite TUI Profesional y Ligera para la Creación de Interfaces de Línea de Comandos en Terminales TTY.**

Menús interactivos por teclado y ratón (ANSI SGR 1006), submenús laterales en cascada (hasta 3 niveles: *Sub del Sub*), menús por pestañas multitarea (`GRmenu.tabs`), rediseño de entrada de datos (`GRmenu.input`), tablas con ordenamiento y búsqueda en vivo, selección múltiple con casillas de verificación, controles deslizantes en tiempo real, renderizado de imágenes ANSI TrueColor de 24 bits, sistema de temas estilo CSS `.gr`, iluminación dinámica Living Neon a 30 FPS en vivo, colores hexadecimales directos (`#RRGGBB`), modales nativos de confirmación y texto, buscador instantáneo en vivo, cuadrículas bidimensionales, barras de progreso y banners 3D sin dependencias externas.

[![Gem Version](https://badge.fury.io/rb/grmenu.svg)](https://badge.fury.io/rb/grmenu)
[![License: MIT](https://img.shields.io/github/license/JoseEduardoGR/GRmenu)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-blue)](https://github.com/JoseEduardoGR/GRmenu)
[![Ruby](https://img.shields.io/badge/ruby-%3E%3D%202.6-red.svg)](https://www.ruby-lang.org)

![Demo de GRmenu en Ruby](assets/demo.png)

---

## Tabla de Contenidos

1. [Por qué elegir GRmenu?](#por-qué-elegir-grmenu)
2. [Instalación y Requisitos](#instalación-y-requisitos)
3. [Inicio Rápido en 10 Segundos](#inicio-rápido-en-10-segundos)
4. [Guía Exhaustiva de Componentes y Características](#guía-exhaustiva-de-componentes-y-características)
   - [1. Menú Interactivo Principal (Buscador, Grid 2D y Paginación)](#1-menú-interactivo-principal)
   - [2. Submenús en Cascada de hasta 3 Niveles (Sub del Sub)](#2-submenús-en-cascada-de-hasta-3-niveles-sub-del-sub)
   - [3. Menú por Pestañas Multitarea (GRmenu.tabs)](#3-menú-por-pestañas-multitarea-grmenutabs)
   - [4. Soporte Completo de Ratón (mouse: true)](#4-soporte-completo-de-ratón-mouse-true)
   - [5. Rediseño de Entrada de Datos (GRmenu.input)](#5-rediseño-de-entrada-de-datos-grmenuinput)
   - [6. Selector Múltiple con Checkboxes (GRmenu.checkbox)](#6-selector-múltiple-con-checkboxes-grmenucheckbox)
   - [7. Control Deslizante en Tiempo Real (GRmenu.slider)](#7-control-deslizante-en-tiempo-real-grmenuslider)
   - [8. Diálogos Nativos de Confirmación (GRmenu.confirm)](#8-diálogos-nativos-de-confirmación-grmenuconfirm)
   - [9. Tablas Interactivas con Buscador y Ordenamiento (GRmenu.table)](#9-tablas-interactivas-con-buscador-y-ordenamiento-grmenutable)
   - [10. Tarjetas Estilizadas y Alertas (GRmenu.card y GRmenu.alert)](#10-tarjetas-estilizadas-y-alertas-grmenucard-y-grmenualert)
   - [11. Renderizado Universal de Imágenes en Terminal (GRmenu.image)](#11-renderizado-universal-de-imágenes-en-terminal-grmenuimage)
   - [12. Barras de Progreso y Spinners de Carga](#12-barras-de-progreso-y-spinners-de-carga)
   - [13. Iluminación Dinámica Living Neon a 30 FPS](#13-iluminación-dinámica-living-neon-a-30-fps)
   - [14. Banners ASCII 3D y Módulo de Color (Color / C)](#14-banners-ascii-3d-y-módulo-de-color)
   - [15. Sistema de Temas .gr y CSS para TUI](#15-sistema-de-temas-gr-y-css-para-tui)
   - [16. Exportación de Temas desde Terminal / CLI (-theme)](#16-exportación-de-temas-desde-terminal--cli--theme)
   - [17. CSS Inline en el Código (<<-GR)](#17-css-inline-en-el-código--gr)
5. [Laboratorio de Nuevas Funcionalidades (ruby/eaja.rb y ruby/e.rb)](#laboratorio-de-nuevas-funcionalidades)
6. [Catálogo Visual de Fuentes 3D (1 al 10)](#catálogo-visual-de-fuentes-3d)
7. [Catálogo Visual de Marcos y Bordes (1 al 20)](#catálogo-visual-de-marcos-y-bordes)
8. [Referencia Exhaustiva de la API de Ruby](#referencia-exhaustiva-de-la-api-de-ruby)
9. [Mapa de Controles: Teclado y Ratón](#mapa-de-controles-teclado-y-ratón)
10. [Licencia](#licencia)

---

## Por qué elegir GRmenu?

- **Cero Dependencias Externas:** Funciona exclusivamente con la biblioteca estándar de Ruby (`io/console`, `json`, `zlib`, `open3`), sin gemas externas ni extensiones en C compiladas.
- **Soporte de Ratón ANSI SGR 1006:** Interactúa directamente con clics en opciones, pestañas, cajas de submenús, flechas de paginación y rueda de desplazamiento vertical (*Scroll Wheel*) activando `mouse: true`.
- **Submenús en Cascada de hasta 3 Niveles:** Despliega paneles anidados conectados mediante puentes dobles `──` (`Box 0 ── Box 1 ── Box 2`) con un motor responsivo que desliza la vista automáticamente si el terminal es estrecho.
- **Pestañas Multitarea (`GRmenu.tabs`):** Organiza interfaces complejas en paneles horizontales alternables con `Tab`, `Shift+Tab` o clic del ratón.
- **Sistema de Temas CSS (.gr):** Diseña la estética visual de tu consola como si fuera una hoja de estilos web con bloques `<<menu`, `<<submenu`, `<<tabs`, `<<input`, `<<table`, `<<card`, `<<slider` y `<<checkbox`.
- **Firmas Flexibles en Todos los Widgets:** Acepta tanto llamadas clásicas posicionales como llamadas por palabra clave (`title:`, `headers:`, `rows:`, `pause: false`).
- **Colores Hexadecimales Directos:** Soporta valores `#FF0055`, `#00F5FF`, `#0FF` en cualquier marco, texto o banner con TrueColor de 24 bits nativo.
- **Animaciones Living Neon a 30 FPS:** Olas de luz senoidal continuas y destellos de incandescencia en tiempo real sin introducir retraso en el teclado.
- **Modo TTY Crudo Instantáneo:** Control milimétrico de la consola sin parpadeo de pantalla y con captura instantánea de eventos de teclado (0 ms de latencia).
- **Multiplataforma Real:** Totalmente compatible con Linux, macOS y Windows (Windows Terminal, PowerShell, CMD y terminal de VS Code).

---

## Instalación y Requisitos

Requiere **Ruby >= 2.6.0**.

### Vía RubyGems

```bash
gem install grmenu
```

### Vía Gemfile

```ruby
gem 'grmenu', '~> 4.0'
```

### Requerimiento en scripts de Ruby

```ruby
require 'grmenu'
```

---

## Inicio Rápido en 10 Segundos

Crea un archivo llamado `app.rb` y ejecútalo con `ruby app.rb`:

```ruby
require 'grmenu'

# Cargar un tema integrado con estética neón
GRmenu.theme(:neon_red)

def saludar
  GRmenu.alert(:success, "Bienvenido a GRmenu v4.0.1!")
end

def ver_tabla
  headers = ["ID", "SERVICIO", "ESTADO"]
  filas = [
    ["01", "API Gateway", "Operativo"],
    ["02", "Postgres DB", "Operativo"],
    ["03", "Redis Cache", "En espera"]
  ]
  GRmenu.table(headers, filas, title: "Monitor de Servidores", search: true)
end

menu = GRmenu.new(
  [
    ["Saludar", method(:saludar), "Muestra un mensaje emergente"],
    ["Ver Infraestructura", method(:ver_tabla), "Tabla interactiva con buscador en vivo"],
    ["Salir", -> { exit(0) }, "Finaliza la ejecución"]
  ],
  title: "Panel de Control",
  banner: "DEMO",
  style: 3,
  mouse: true,
  animate: "diagonal"
)

menu.draw
```

---

## Guía Exhaustiva de Componentes y Características

### 1. Menú Interactivo Principal

El constructor `GRmenu.new` proporciona una experiencia interactiva completa con navegación continua (*snake loop*), paginación automática, buscador en vivo y distribución en cuadrículas 2D.

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
    # 1. Method directo (formatea y capitaliza el nombre automáticamente)
    method(:iniciar_servidor),

    # 2. Symbol (invoca el método del contexto)
    :crear_respaldo,

    # 3. Arreglo [Etiqueta, Acción]
    ["Lanzar Proceso", method(:lanzar)],

    # 4. Arreglo con Tooltip [Etiqueta, Acción, Descripción]
    ["Limpieza de Caché", method(:limpiar), "Vacía los temporales en disco"],

    # 5. Bloque anónimo Proc o Lambda
    ["Acción Rápida", -> { puts "Ejecutado!"; GRmenu.continue }, "Ejecuta bloque inline"],

    # 6. Hash explícito
    { name: "Configuración", action: method(:config), desc: "Ajustes del sistema" },

    # 7. Submenús anidados en cascada (hasta 3 niveles)
    ["Servicios", [
      ["Servidores Web", [
        ["Iniciar NGINX", -> { puts "Iniciando NGINX..." }],
        ["Reiniciar Apache", -> { puts "Reiniciando Apache..." }]
      ]],
      ["Bases de Datos", [
        ["PostgreSQL", -> { puts "Iniciando Postgres..." }],
        ["Redis", -> { puts "Limpiando Redis..." }]
      ]]
    ], "Administración de servicios por niveles"]
  ],
  title: "Consola de Administración",
  banner: "SISTEMA",
  search: true,      # Activa buscador interactivo en vivo
  columns: 1,        # Cuadrícula de columnas (soporta 2+ con navegación 2D)
  page_size: 6,      # Paginación con auto-scroll
  mouse: true,       # Soporte de ratón (clic y rueda de scroll)
  style: 3
)

menu.draw(size_max: 44)
```

---

### 2. Submenús en Cascada de hasta 3 Niveles (*Sub del Sub*)

GRmenu permite anidar opciones hasta **3 niveles de profundidad** (*Menú Original $\to$ Submenú 1 $\to$ Sub del Sub*).

```text
╔══════════════════════╗  ╔════════════════════╗  ╔════════════════════╗
║ > Servicios       ▶  ║──║     Servicios      ║  ║   Servidores Web   ║
║   Ajustes            ║  ║════════════════════║  ║════════════════════║
╚══════════════════════╝  ║ > Servidores Web ▶ ║──║ > Iniciar NGINX    ║
                          ║   Bases de Datos ▶ ║  ║   Reiniciar Apache ║
                          ╚════════════════════╝  ╚════════════════════╝
```

* **Detección Automática:** Cualquier opción cuyo segundo elemento sea un arreglo de opciones recibe automáticamente el indicador `▶`.
* **Puentes Dobles `──`:** Conectan las cajas visualmente a la altura exacta de la opción seleccionada.
* **Diseño Responsivo:** Si la consola no es lo suficientemente ancha para mostrar las 3 cajas simultáneamente, el visor se desliza suavemente mostrando `Sub 1 ── Sub 2` o la caja activa sin deformar la interfaz ni desbordar la pantalla.
* **Controles por Teclado:**
  - `→` (Derecha): Despliega el submenú del siguiente nivel.
  - `←` (Izquierda) o `Esc`: Cierra el nivel actual y regresa al nivel padre.
  - `↑ / ↓`: Navega cíclicamente dentro de la caja activa.
  - `Enter`: Despliega submenú o ejecuta la acción final si es una hoja del árbol.
* **Controles por Ratón (`mouse: true`):**
  - Clic sobre cualquier caja enfoca ese nivel y esa opción.
  - Segundo clic o clic sobre la opción activa ejecuta la acción.
  - La rueda de scroll funciona dinámicamente sobre la caja que tiene el foco.

---

### 3. Menú por Pestañas Multitarea (`GRmenu.tabs`)

Permite organizar interfaces complejas en paneles horizontales independientes:

```text
              [ Servidores ]     Bases de Datos     Configuración  

╔══════════════════════════════════════════════════════════════════╗
║ > Iniciar API Gateway                                            ║
║   Supervisar Worker Celery                                       ║
╚══════════════════════════════════════════════════════════════════╝
```

```ruby
tabs_data = {
  "Servidores" => [
    ["API Gateway", -> { GRmenu.card("Gateway", "Puerto 8080 activo", pause: false); sleep 1.2 }],
    ["Worker Celery", -> { GRmenu.card("Worker", "42 tareas en cola", pause: false); sleep 1.2 }]
  ],
  "Bases de Datos" => [
    ["PostgreSQL", -> { GRmenu.card("Postgres", "Conexiones: 12/100", pause: false); sleep 1.2 }],
    ["Redis Cache", -> { GRmenu.card("Redis", "Memoria: 14 MB", pause: false); sleep 1.2 }]
  ],
  "Configuración" => [
    ["Cambiar Tema Neon", -> { GRmenu.theme(:cyberpunk) }]
  ]
}

tabs_menu = GRmenu.tabs(
  tabs_data,
  title: "Consola de Administración Multitarea",
  style: 3,
  mouse: true
)

tabs_menu.draw
```

* **Atajos de Teclado:** Pulsa `Tab` para avanzar a la siguiente pestaña o `Shift+Tab` para retroceder.
* **Soporte de Ratón:** Haz clic directamente sobre el nombre de cualquier pestaña para cambiar a ella al instante.

---

### 4. Soporte Completo de Ratón (`mouse: true`)

Al activar `mouse: true` en el constructor o en el CSS (`<<menu mouse:: true >>`), GRmenu activa el protocolo estándar **ANSI SGR 1006**:

* **Clic Izquierdo:**
  - En opciones: Un clic enfoca la opción; un segundo clic la ejecuta.
  - En pestañas: Cambia inmediatamente a la pestaña pulsada.
  - En submenús: Despliega y enfoca el submenú correspondiente.
  - En flechas de paginación (`▲` / `▼`): Sube o baja de página.
* **Rueda de Desplazamiento (*Scroll Wheel*):**
  - Mueve el foco hacia arriba (`wheel up`) o hacia abajo (`wheel down`) dentro del menú o panel activo de forma ultra-fluida.

---

### 5. Rediseño de Entrada de Datos (`GRmenu.input`)

El método `GRmenu.input` cuenta con marco visual integrado, título superior centrado, etiqueta interior y soporte para contraseñas:

```text
╔══════════════ Ingresa tu Configuración ══════════════╗
║                                                      ║
║ URL del Servidor:  http://localhost:8080█            ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
```

```ruby
# Entrada con valor pre-cargado editable
servidor = GRmenu.input(
  title: "Ingresa tu Configuración",
  label: "URL del Servidor:",
  default: "http://localhost:8080",
  style: 3,
  border_color: "neon_cyan",
  title_color: "neon_yellow",
  label_color: "white"
)

# Entrada segura con modo password (oculta caracteres con asteriscos)
token = GRmenu.input(
  title: "Autenticación Segura",
  label: "Token Secreto:",
  password: true,
  style: 3,
  border_color: "neon_red"
)

# Uso rápido posicional
nombre = GRmenu.input("Ingresa tu Nombre:", default: "admin")
```

* **Controles:** Escritura normal, `Backspace` para borrar, `Ctrl+U` para limpiar toda la línea y `Enter` para confirmar.

---

### 6. Selector Múltiple con Checkboxes (`GRmenu.checkbox`)

Permite seleccionar múltiples elementos simultáneamente mediante casillas interactivas `[X]` / `[ ]`:

```ruby
paquetes = [
  ["Servidor Nginx Web", true, "Proxy inverso de alta velocidad"],
  ["Base de Datos PostgreSQL 16", true, "Motor de datos principal"],
  ["Almacén de Caché Redis 7.2", false, "Caché en memoria RAM"],
  ["Monitor Prometheus", true, "Métricas y alertas"]
]

seleccionados = GRmenu.checkbox(
  paquetes,
  title: "Instalador de Paquetes",
  color: "neon_cyan",
  style: 3
)

puts "Seleccionados: #{seleccionados.inspect}"
```

* **Teclas de Control:**
  - `Espacio`: Alterna marcado `[X]` / `[ ]`.
  - `a`: Selecciona todos (*Select All*).
  - `n`: Deselecciona todos (*Deselect All*).
  - `i`: Invierte la selección.
  - `Enter`: Confirma y devuelve la lista de elementos marcados.

---

### 7. Control Deslizante en Tiempo Real (`GRmenu.slider`)

Permite seleccionar numéricamente un valor dentro de un rango mediante una barra horizontal en tiempo real:

```ruby
ram = GRmenu.slider(
  "Asignar Memoria RAM:",
  min: 1,
  max: 64,
  step: 1,
  default: 16,
  unit: "GB",
  color: "gold",
  style: 3
)
```

* **Teclas:** `← / →` ajusta de 1 en 1 (`step`), `↑ / ↓` realiza saltos rápidos de 5 pasos, `Enter` confirma.

---

### 8. Diálogos Nativos de Confirmación (`GRmenu.confirm`)

Cuadros emergentes Si / No con botones activos interactivos:

```ruby
if GRmenu.confirm("¿Deseas aplicar los cambios en producción?", default: true, color: "neon_green", style: 3)
  puts "Aplicando..."
end
```

* **Teclas:** `← / →` para alternar entre `[ Sí ]` y `[ No ]`, `Enter` para confirmar.

---

### 9. Tablas Interactivas con Buscador y Ordenamiento (`GRmenu.table`)

Visualiza y navega colecciones de datos tabulares con buscador instantáneo, ordenamiento por columnas con la tecla `s`, paginación y protección anti-desbordes:

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
  ["04", "Workers Celery", "Ocupado", "45ms"]
]

# Llamada posicional
fila = GRmenu.table(headers, filas, style: 3, header_color: "neon_yellow")

# Llamada por palabra clave
fila = GRmenu.table(
  headers: headers,
  rows: filas,
  title: "Monitor de Infraestructura",
  search: true,
  sort: true,
  page_size: 5,
  style: 3
)

if fila
  puts "Fila elegida: #{fila.join(' | ')}"
end
```

---

### 10. Tarjetas Estilizadas y Alertas (`GRmenu.card` y `GRmenu.alert`)

Cuadros informativos con división automática de párrafos (*word-wrapping*) y soporte completo para colores TrueColor y Neón:

```ruby
# Alertas contextuales
GRmenu.alert(:success, "Conexión establecida con el servidor.")
GRmenu.alert(:warning, "Memoria RAM al 85%.", pause: false)
GRmenu.alert(:error, "Fallo al conectar con el cluster.", pause: false)
GRmenu.alert(:info, "Actualización disponible.")

# Tarjeta informativa posicional (ideal para respuestas y logs)
GRmenu.card("NGINX Web Server", "NGINX iniciado en el puerto 80 (PID 1024)", style: 3, border_color: "neon_green", pause: false)

# Tarjeta informativa con keywords
GRmenu.card(
  title: "Métricas de Producción",
  content: "Peticiones/seg: 18,400 req/s\nLatencia p99: 11.4 ms\nSalud del cluster: 100%",
  border_color: "#FF0055",
  title_color: "#00F5FF",
  content_color: "gold",
  style: 7
)
```

---

### 11. Renderizado Universal de Imágenes en Terminal (`GRmenu.image`)

Decodifica y renderiza cualquier formato de imagen (PNG, JPEG, JPG, WEBP, GIF, BMP) con **micro-subpíxeles ANSI TrueColor de 24 bits** usando medios bloques `▀` (2 píxeles verticales por celda, relación de aspecto 1:1) y remuestreo Lanczos:

```ruby
# 1. Renderizado directo en consola
GRmenu.image("assets/logo.png", width: 40, style: 3, color: "neon_cyan", center: true)

# 2. Como cabecera gráfica dentro de un menú interactivo
menu = GRmenu.new(
  opciones,
  image: "assets/banner.png",
  image_width: 44,
  title: "Galería con Imagen"
)
menu.draw
```

---

### 12. Barras de Progreso y Spinners de Carga

```ruby
# Barra de progreso con avance dinámico
GRmenu.progress(100, title: "Descargando Paquetes", color: "neon_yellow", style: 3) do |bar|
  10.times do |i|
    sleep 0.1
    bar.advance(10, status: "Procesando bloque #{i + 1} de 10...")
  end
end

# Spinner animado no bloqueante en hilo secundario
resultado = GRmenu.spinner("Conectando con el cluster remoto...", color: "neon_cyan") do
  sleep 1.2
  "Conexión exitosa"
end
```

---

### 13. Iluminación Dinámica Living Neon a 30 FPS

Al configurar `animate: "diagonal"`, `"linear"`, `"fade"` o `"rgb"`, el motor proyecta una ola de luz senoidal continua en tiempo real a 30 FPS que barre los marcos y los banners con destellos de incandescencia (*glow*), sin introducir retraso en el teclado:

```ruby
menu = GRmenu.new(
  opciones,
  banner: "THEMES",
  title: "Efecto Neón Vivo",
  style: 3,
  animate: "diagonal"
)
menu.set_style.border("neon_red").banner("neon_red").focus("neon_yellow")
menu.draw
```

---

### 14. Banners ASCII 3D y Módulo de Color

```ruby
# Banners en arte ASCII 3D (fuentes del 1 al 10)
GRmenu.banner("ADMIN", 0, color: "neon_red", style: 3, font: 1)

# Módulo Color / C / Colors
puts Color.rgb("Texto degradado en onda arcoíris continua")
puts Color.hex("#FF0055", "Texto en Rojo Carmesí")
puts Color.gold("Texto en Dorado")
puts Color.neon_cyan("Texto en Cian Neón")
puts Color.neon_emerald("Texto en Esmeralda Neón")
```

---

### 15. Sistema de Temas .gr y CSS para TUI

GRmenu incluye un motor de temas declarativos en archivos `.gr` con sintaxis limpia tipo CSS que cubre menús, submenús, pestañas, inputs, tablas, tarjetas, sliders y checkboxes.

#### Cargar Temas Integrados:
```ruby
GRmenu.theme(:neon_red)    # Rojos eléctricos incandescentes y foco amarillo
GRmenu.theme(:cyberpunk)   # Neones cian, amarillo y efecto Chroma
GRmenu.theme(:matrix)      # Verde fosforescente terminal hacker
GRmenu.theme(:dracula)     # Morados, fucsias y cian
GRmenu.theme(:nord)        # Azules árticos y paleta fría
GRmenu.theme(:monokai)     # Amarillos, verdes y magentas
GRmenu.theme(:sunset)      # Atardecer cálido en rojos, naranjas y dorados
```

#### Especificación Completa de un Archivo de Tema (`mi_tema.gr`):
```gr
GRmenu::config<-1->

@theme:: "CyberNeon"
@author:: "GRcode"
@version:: "4.1"

<<menu
  style:: 3
  banner_style:: 3
  font:: 1
  animate:: diagonal
  desc_prefix:: ->
  center:: true
  mouse:: true
  border:: neon_cyan:1
  title:: neon_yellow:2
  focus:: neon_red:2
  options:: white:1
  banner:: neon_magenta:2
  subtitle:: cyan:1
  divider:: blue:1
>>

<<submenu
  style:: 3
  border:: neon_yellow:1
  focus:: neon_cyan:2
  options:: white:1
  title:: neon_yellow:2
  arrow:: neon_cyan:2
>>

<<tabs
  active_tab:: neon_yellow:2
  tab_color:: gray:1
  indicator:: neon_cyan:2
>>

<<input
  style:: 3
  border_color:: neon_cyan:1
  title_color:: neon_yellow:2
  label_color:: white:2
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

### 16. Exportación de Temas desde Terminal / CLI (-theme)

Puedes extraer y exportar el tema configurado en cualquier script de Ruby directamente a un archivo `.gr`:

```bash
# Exporta el tema del script con nombre automático:
ruby mi_app.rb -theme

# Exporta a un archivo de salida específico:
ruby mi_app.rb -theme -o salida_tema.gr
```

De forma programática en Ruby:
```ruby
GRmenu.export_from_file("mi_app.rb", "tema_extraido.gr")
menu.export_theme("mi_tema.gr")
```

---

### 17. CSS Inline en el Código (`<<-GR`)

Puedes inyectar bloques de estilo tipo `<style>` directamente en tu script sin crear archivos `.gr` adicionales:

```ruby
menu = GRmenu.new(opciones, title: "App con CSS", mouse: true)

menu.style(<<-GR)
<<menu
  style:: 3
  mouse:: true
  border:: neon_cyan:1
  title:: neon_yellow:2
  focus:: neon_red:2
>>
<<submenu
  style:: 3
  border:: neon_yellow:1
  focus:: neon_cyan:2
>>
<<tabs
  active_tab:: neon_yellow:2
  tab_color:: gray:1
>>
<<input
  style:: 3
  border_color:: neon_cyan:1
  title_color:: neon_yellow:2
  label_color:: white:2
>>
GR

menu.draw
```

---

## Laboratorio de Nuevas Funcionalidades

Puedes ejecutar el archivo de laboratorio interactivo completo para probar en vivo los submenús de 3 niveles, las pestañas con ratón y el input rediseñado:

```bash
ruby ruby/eaja.rb
```

O el laboratorio general de componentes:

```bash
ruby ruby/e.rb
```

---

## Catálogo Visual de Fuentes 3D

Configura la tipografía mediante el parámetro `font: 1..10`:

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

## Catálogo Visual de Marcos y Bordes

Configura el diseño del marco mediante el parámetro `style: 1..20`:

| ID | Muestra | ID | Muestra | ID | Muestra | ID | Muestra |
|:--:|:--------|:--:|:--------|:--:|:--------|:--:|:--------|
| `1` | `#####` (Hash) | `6` | `╓───╖` (Mixto) | `11`| `░░░░░` (Sombra suave) | `16`| `~~~~~` (Ondas) |
| `2` | `┌───┐` (Simple) | `7` | `╭───╮` (Curvas) | `12`| `█████` (Bloque) | `17`| `-----` (Guion) |
| `3` | `╔═══╗` (Doble) | `8` | `▛▀▀▀▜` (Outline) | `13`| `*****` (Asterisco) | `18`| `◆◆◆◆◆` (Rombos) |
| `4` | `┏━━━┓` (Gruesa) | `9` | `▓▓▓▓▓` (Sombra oscura) | `14`| `+++++` (Cruces) | `19`| `●○○○●` (Círculos) |
| `5` | `╒═══╕` (Mixto) | `10`| `▒▒▒▒▒` (Sombra media) | `15`| `=====` (Doble simple) | `20`| `★☆☆☆★` (Estrellas) |

---

## Referencia Exhaustiva de la API de Ruby

### Constructor `GRmenu.new(functions, **opciones)`

| Parámetro | Tipo | Valor por Defecto | Descripción |
|:----------|:-----|:------------------|:------------|
| `functions` | `Array` | *Obligatorio* | Lista de métodos, símbolos, arrays `[nombre, acción, tooltip]`, submenús anidados o `Proc`. |
| `title:` | `String` | `""` | Título centrado en la cabecera del marco de opciones. |
| `banner:` | `String` | `""` | Texto convertido a arte ASCII 3D arriba del menú. |
| `subtitle:` | `String` | `""` | Descripción o subtítulo (soporta saltos de línea `\n`). |
| `search:` | `Boolean` | `false` | Activa el buscador instantáneo interactivo mientras se escribe. |
| `columns:` | `Integer` | `1` | Cantidad de columnas para navegación en cuadrícula 2D. |
| `page_size:` | `Integer` | `auto` | Número máximo de filas visibles antes de activar auto-scroll. |
| `mouse:` | `Boolean` | `false` | Activa soporte de ratón ANSI SGR 1006 (clic, scroll, submenús). |
| `tabs:` | `Hash` | `nil` | Estructura de pestañas multitarea horizontales. |
| `style:` | `Integer` | `19` | Estilo de marco para las opciones (1 al 20). |
| `banner_style:` | `Integer` | `3` | Estilo de marco para el banner 3D (1 al 20). |
| `font:` | `Integer` | `1` | Fuente tipográfica del banner ASCII (1 al 10). |
| `animate:` | `String/Bool`| `false` | Efecto de iluminación ("diagonal", "linear", "fade", "rgb"). |
| `desc_prefix:` | `String` | `"[i]"` | Prefijo visual para el tooltip de ayuda. |
| `image:` | `String` | `nil` | Ruta a imagen de cabecera (PNG/JPG/WEBP/GIF/BMP). |
| `image_width:` | `Integer` | `40` | Ancho en columnas de terminal para la imagen. |
| `divider:` | `Boolean/Int` | `true` | Líneas divisorias horizontales ajustadas al marco. |
| `center:` | `Boolean` | `true` | Centrado horizontal simétrico automático. |

### Métodos Estáticos y Componentes

| Método | Firma | Retorno |
|:-------|:------|:--------|
| `GRmenu.tabs` | `(tabs_hash, **opciones)` | Crea un menú interactivo dividido por pestañas horizontales. |
| `GRmenu.theme` | `(nombre_o_simbolo)` | Carga un tema `.gr` predefinido para todo el sistema. |
| `GRmenu.import_config` | `(ruta_archivo_gr)` | Carga un archivo de tema `.gr` personalizado. |
| `GRmenu.export_from_file`| `(script_origen, archivo_gr)` | Extrae el tema de un script sin correr bucles. |
| `GRmenu.style` | `(texto_css_gr)` | Inyecta estilos CSS inline globalmente. |
| `GRmenu.table` | `(headers, rows, ...)` | Muestra tabla interactiva con buscador y ordenamiento. |
| `GRmenu.card` | `(title, content, ...)` | Muestra tarjeta con auto-wrap y `pause:` configurable. |
| `GRmenu.alert` | `(tipo, mensaje, ...)` | Muestra alerta emergente contextual. |
| `GRmenu.checkbox` | `(items, ...)` | Devuelve `Array` con elementos marcados (`[X]`). |
| `GRmenu.slider` | `(prompt, ...)` | Devuelve valor numérico seleccionado en barra interactiva. |
| `GRmenu.confirm` | `(pregunta, ...)` | Devuelve booleano (`true`/`false`) con botones interactivos. |
| `GRmenu.input` | `(title: ..., label: ..., ...)` | Entrada de texto rediseñada con marco y cursor `█`. |
| `GRmenu.image` | `(filepath, width:, style:, color:)` | Renderiza imagen en TrueColor 24-bit (Lanczos / Zlib). |
| `GRmenu.progress` | `(total = 100, ... &bloque)` | Barra de progreso dinámica con bloque. |
| `GRmenu.spinner` | `(mensaje, ... &bloque)` | Spinner animado no bloqueante. |
| `GRmenu.banner` | `(texto, delay = 0, ...)` | Imprime banner ASCII 3D. |
| `GRmenu.div` | `(long = nil, color = "blue", ...)` | Imprime línea divisoria horizontal. |
| `GRmenu.clear_screen` | `()` (Alias: `GRmenu.clr`) | Limpia la pantalla y el scrollback. |
| `GRmenu.continue` | `(texto = "Presiona...")` | Pausa hasta pulsar una tecla. |
| `GRmenu.help` | `()` | Muestra guía completa de documentación en consola. |

---

## Mapa de Controles: Teclado y Ratón

| Control | Contexto | Acción Realizada |
|:--------|:---------|:-----------------|
| `↑` (Arriba) / `k`  | Menús / Tablas / Checkbox | Mueve el foco hacia arriba (con salto continuo *Snake* en extremos). |
| `↓` (Abajo) / `j`   | Menús / Tablas / Checkbox | Mueve el foco hacia abajo. |
| `Tab` / `Shift+Tab` | Pestañas (`tabs`) | Cambia a la siguiente o anterior pestaña. |
| `→` (Derecha)       | Submenús / Grid 2D | Abre submenú lateral (hasta 3 niveles) o salta columna en grid 2D. |
| `←` (Izquierda)     | Submenús / Grid 2D | Cierra el submenú lateral actual y regresa al nivel padre. |
| `Clic Izquierdo`    | Ratón (`mouse: true`) | Enfoca la opción; si ya está enfocada, la ejecuta inmediatamente. |
| `Clic en Pestaña`   | Ratón (`mouse: true`) | Salta instantáneamente a la pestaña seleccionada. |
| `Clic en Submenú`   | Ratón (`mouse: true`) | Abre o enfoca la caja del submenú correspondiente. |
| `Rueda de Scroll`   | Ratón (`mouse: true`) | Desplaza el foco arriba o abajo (↑ / ↓) fluidamente en el panel activo. |
| `Clic en ▲ / ▼`     | Ratón (`mouse: true`) | Sube o baja de página en paginación. |
| `s` / `S`           | Tablas   | Ordena la tabla por la columna actual alternando ASC/DESC. |
| `Espacio`           | Checkbox | Marca o desmarca la casilla del elemento actual `[X]` / `[ ]`. |
| `a` / `A`           | Checkbox | Marca todos los elementos (*Select All*). |
| `n` / `N`           | Checkbox | Desmarca todos los elementos (*Deselect All*). |
| `i` / `I`           | Checkbox | Invierte la selección de todos los elementos. |
| `←` / `→` o `h` / `l`| Slider  | Ajusta el valor numérico en un incremento (`step`). |
| `↑` / `↓` o `k` / `j`| Slider  | Salto rápido de 5 pasos en el valor numérico. |
| `Enter`             | Global   | Ejecuta la acción seleccionada o confirma el formulario. |
| `q` / `Esc`         | Global   | Sale del menú o cancela la operación actual. |
| `Backspace`         | Buscador / Input | Borra el último caracter ingresado. |
| `Ctrl+U`            | Buscador / Input | Limpia todo el texto ingresado. |

---

## Licencia

Distribuido bajo licencia **MIT**. Consulta [`LICENSE`](LICENSE) para más detalles.

Desarrollado con precisión por **[grcode](https://github.com/JoseEduardoGR)**
