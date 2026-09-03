# GRmenu (Ruby) v4.0.1

**Suite TUI Profesional y Ligera para la Creacion de Interfaces de Linea de Comandos en Terminales TTY.**

Menus interactivos por teclado y ratón (SGR 1006), submenús laterales en cascada (hasta 3 niveles: *Sub del Sub*), menús por pestañas multitarea (`GRmenu.tabs`), rediseño de entrada de datos (`GRmenu.input`), tablas con ordenamiento y busqueda en vivo, seleccion multiple con casillas de verificacion, controles deslizantes en tiempo real, renderizado de imagenes ANSI TrueColor de 24 bits, sistema de temas estilo CSS `.gr`, iluminacion dinamica Living Neon a 30 FPS en vivo, colores hexadecimales directos (#RRGGBB), modales nativos de confirmacion y texto, buscador instantaneo en vivo, cuadriculas bidimensionales, barras de progreso y banners 3D sin dependencias externas.

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
   - [2. Submenus en Cascada de hasta 3 Niveles (Sub del Sub)](#2-submenus-en-cascada-de-hasta-3-niveles)
   - [3. Menu por Pestanas Multitarea (GRmenu.tabs)](#3-menu-por-pestanas-multitarea-grmenutabs)
   - [4. Soporte Completo de Raton (mouse: true)](#4-soporte-completo-de-raton-mouse-true)
   - [5. Rediseno de Entrada de Datos (GRmenu.input)](#5-rediseno-de-entrada-de-datos-grmenuinput)
   - [6. Sistema de Temas .gr y CSS para TUI (menu, submenu, tabs, input)](#6-sistema-de-temas-gr-y-css-para-tui)
   - [7. Exportacion de Temas desde Terminal / CLI](#7-exportacion-de-temas-desde-terminal--cli)
   - [8. CSS Inline en el Codigo (<<-GR)](#8-css-inline-en-el-codigo--gr)
   - [9. Tablas Interactivas con Buscador y Ordenamiento (GRmenu.table)](#9-tablas-interactivas-con-buscador-y-ordenamiento)
   - [10. Tarjetas y Alertas Estilizadas (GRmenu.card y GRmenu.alert)](#10-tarjetas-y-alertas-estilizadas)
   - [11. Colores Hexadecimales TrueColor y Catalogo de 90+ Colores](#11-colores-hexadecimales-truecolor-y-catalogo-de-90-colores)
   - [12. Iluminacion Dinamica Living Neon a 30 FPS](#12-iluminacion-dinamica-living-neon-a-30-fps)
   - [13. Seleccion Multiple con Checkboxes (GRmenu.checkbox)](#13-seleccion-multiple-con-checkboxes)
   - [14. Control Deslizante Interactivo (GRmenu.slider)](#14-control-deslizante-interactivo)
   - [15. Modales Nativos de Confirmacion (GRmenu.confirm)](#15-modales-nativos-de-confirmacion)
   - [16. Renderizado Universal de Imagenes (GRmenu.image)](#16-renderizado-universal-de-imagenes)
   - [17. Barra de Progreso y Spinner de Carga](#17-barra-de-progreso-y-spinner-de-carga)
   - [18. Banners 3D y Modulo de Color (Color / C)](#18-banners-3d-y-modulo-de-color)
5. [Laboratorio de Nuevas Funcionalidades (eaja.rb y e.rb)](#laboratorio-de-nuevas-funcionalidades)
6. [Catalogo Visual de Fuentes 3D (1 al 10)](#catalogo-visual-de-fuentes-3d)
7. [Catalogo Visual de Marcos y Bordes (1 al 20)](#catalogo-visual-de-marcos-y-bordes)
8. [Referencia Exhaustiva de la API](#referencia-exhaustiva-de-la-api)
9. [Mapa de Controles: Teclado y Raton](#mapa-de-controles-teclado-y-raton)
10. [Licencia](#licencia)

---

## Por que elegir GRmenu?

- **Cero Dependencias Externas:** Funciona exclusivamente con la libreria estandar de Ruby (`io/console`, `json`, `zlib`, `open3`), sin gemas pesadas ni binarios nativos requeridos.
- **Soporte de Raton SGR 1006:** Interactua con clics en opciones, pestanas, submenus, botones de paginacion y rueda de scroll con `mouse: true`.
- **Submenus en Cascada de 3 Niveles:** Conecta hasta 3 cajas laterales (`Box 0 ── Box 1 ── Box 2`) con puentes dobles y ajuste responsivo automatico.
- **Pestanas Multitarea (`GRmenu.tabs`):** Organiza interfaces complejas en paneles horizontales alternables con `Tab`, `Shift+Tab` o clic del raton.
- **Sistema de Temas CSS (.gr):** Diseña la estetica de tu consola como si fuera una hoja de estilos web con bloques `<<menu`, `<<submenu`, `<<tabs`, `<<input`, `<<table`, `<<card`, `<<slider`, etc.
- **Firmas Flexibles:** Todos los widgets aceptan llamadas clasicas posicionales `("Titulo", "Mensaje")` o por palabra clave `(title: "...", content: "...")`.
- **Colores Hexadecimales Directos:** Soporta `#FF0055`, `#00F5FF`, `#0FF` en cualquier componente con TrueColor de 24 bits nativo.
- **Animaciones Living Neon a 30 FPS:** Olas de luz senoidal continuas y destello de incandescencia en marcos y banners sin producir retraso en el teclado.
- **Exportacion Instantanea CLI:** Convierte la configuracion visual de cualquier script a un archivo de tema `.gr` reutilizable con la bandera `-theme`.
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
    ["Salir", -> { exit(0) }, "Finaliza la ejecucion"]
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
    { name: "Configuracion", action: method(:config), desc: "Ajustes del sistema" },

    # 7. Submenus anidados laterales (Hasta 3 niveles: Original -> Sub 1 -> Sub 2)
    ["Servicios", [
      ["Servidores Web", [
        ["Iniciar NGINX", -> { puts "Iniciando NGINX..." }],
        ["Reiniciar Apache", -> { puts "Reiniciando Apache..." }]
      ]],
      ["Bases de Datos", [
        ["PostgreSQL", -> { puts "Iniciando Postgres..." }],
        ["Redis", -> { puts "Limpiando Redis..." }]
      ]]
    ], "Administracion de servicios por niveles"]
  ],
  title: "Consola de Administracion",
  banner: "SISTEMA",
  search: true,      # Activa buscador interactivo en vivo
  columns: 1,        # Cuadricula de columnas
  page_size: 6,      # Paginacion con auto-scroll
  mouse: true,       # Soporte de raton (clic y scroll)
  style: 3
)

menu.draw(size_max: 44)
```

---

### 2. Submenus en Cascada de hasta 3 Niveles

GRmenu permite anidar opciones hasta **3 niveles de profundidad** (*Menú Original $\to$ Submenú 1 $\to$ Sub del Sub*).

```text
╔══════════════════════╗  ╔════════════════════╗  ╔════════════════════╗
║ > Servicios       ▶  ║──║     Servicios      ║  ║   Servidores Web   ║
║   Ajustes            ║  ║════════════════════║  ║════════════════════║
╚══════════════════════╝  ║ > Servidores Web ▶ ║──║ > Iniciar NGINX    ║
                          ║   Bases de Datos ▶ ║  ║   Reiniciar Apache ║
                          ╚════════════════════╝  ╚════════════════════╝
```

* **Deteccion Automatica:** Cualquier elemento que contenga una lista de acciones es marcado automaticamente con la flecha `▶`.
* **Puentes Dobles `──`:** Conectan las cajas visualmente en la fila exacta del elemento padre.
* **Diseno Responsivo:** Si la consola no es lo suficientemente ancha para mostrar las 3 cajas a la vez, el visor se desliza suavemente mostrando `Sub 1 ── Sub 2` o la caja activa sin deformar la interfaz ni desbordar la pantalla.
* **Navegacion por Teclado:**
  - `→` (Derecha): Abre el submenú del siguiente nivel.
  - `←` (Izquierda) o `Esc`: Cierra el nivel actual y regresa al padre.
  - `↑ / ↓`: Navega cíclicamente dentro de la caja con foco activo.
  - `Enter`: Abre submenú o ejecuta la acción final si es una hoja del árbol.
* **Navegacion con Raton (`mouse: true`):**
  - Clic en cualquier caja enfoca ese nivel y esa opción.
  - Segundo clic o clic sobre la opción activa ejecuta la acción.
  - La rueda de scroll funciona dinámicamente sobre la caja que tiene el foco.

---

### 3. Menu por Pestanas Multitarea (`GRmenu.tabs`)

Permite organizar interfaces complejas en paneles independientes divididos por pestañas horizontales superiores:

```text
              [ Servidores ]     Bases de Datos     Configuracion  

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
  "Configuracion" => [
    ["Cambiar Tema", -> { GRmenu.theme(:cyberpunk) }]
  ]
}

tabs_menu = GRmenu.tabs(
  tabs_data,
  title: "Consola de Administracion Multitarea",
  style: 3,
  mouse: true
)

tabs_menu.draw
```

* **Atajos de Teclado:** Pulsa `Tab` para avanzar de pestaña o `Shift+Tab` (`\e[Z`) para retroceder.
* **Soporte de Ratón:** Haz clic directamente sobre el nombre de cualquier pestaña para cambiar a ella al instante.

---

### 4. Soporte Completo de Raton (`mouse: true`)

Al activar `mouse: true` en el constructor o en el CSS (`<<menu mouse:: true >>`), GRmenu activa el protocolo estándar **ANSI SGR 1006**:

* **Clic Izquierdo:**
  - En opciones: Un clic selecciona/enfoca la opción; un segundo clic la ejecuta.
  - En pestañas: Cambia inmediatamente a la pestaña pulsada.
  - En submenús: Despliega y enfoca el submenú correspondiente.
  - En flechas de paginación (`▲` / `▼`): Sube o baja de página.
* **Rueda de Desplazamiento (*Scroll Wheel*):**
  - Mueve el foco hacia arriba (`wheel up`) o hacia abajo (`wheel down`) dentro del menú o panel activo de forma ultra-fluida.

---

### 5. Rediseno de Entrada de Datos (`GRmenu.input`)

El método `GRmenu.input` ha sido completamente rediseñado con marco visual integrado, título superior centrado, etiqueta interior y soporte para contraseñas:

```text
╔══════════════ Ingresa tu Configuracion ══════════════╗
║                                                      ║
║ URL del Servidor:  http://localhost:8080█            ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
```

```ruby
# Entrada con valor pre-cargado
servidor = GRmenu.input(
  title: "Ingresa tu Configuracion",
  label: "URL del Servidor:",
  default: "http://localhost:8080",
  style: 3,
  border_color: "neon_cyan",
  title_color: "neon_yellow",
  label_color: "white"
)

# Entrada segura con modo password (oculta caracteres con asteriscos)
token = GRmenu.input(
  title: "Autenticacion Segura",
  label: "Token Secreto:",
  password: true,
  style: 3,
  border_color: "neon_red"
)

# Uso rapido clasico
nombre = GRmenu.input("Ingresa tu Nombre:", default: "admin")
```

* **Controles:** Escribir texto normal, `Backspace` para borrar, `Ctrl+U` para limpiar toda la línea y `Enter` para confirmar.

---

### 6. Sistema de Temas .gr y CSS para TUI

GRmenu incluye un motor de temas declarativos en archivos `.gr` con sintaxis limpia tipo CSS que ahora cubre menús, submenús, pestañas, inputs, tablas, tarjetas, sliders y checkboxes.

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

#### Especificacion Completa de Bloques en un Archivo de Tema (`mi_tema.gr`):
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

### 7. Exportacion de Temas desde Terminal / CLI

Puedes extraer y exportar el tema configurado en cualquier script de Ruby directamente a un archivo `.gr`:

```bash
# Exporta el tema del script con nombre automatico:
ruby mi_app.rb -theme

# Exporta a un archivo de salida especifico:
ruby mi_app.rb -theme -o salida_tema.gr
```

De forma programática en Ruby:
```ruby
GRmenu.export_from_file("mi_app.rb", "tema_extraido.gr")
menu.export_theme("mi_tema.gr")
```

---

### 8. CSS Inline en el Codigo (`<<-GR`)

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

### 9. Tablas Interactivas con Buscador y Ordenamiento

Visualiza y navega colecciones de datos tabulares con buscador instantaneo, ordenamiento por columnas con la tecla `s`, paginacion y proteccion anti-desbordes. Acepta tanto argumentos posicionales como por palabra clave:

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

# Llamada clasica con argumentos posicionales:
seleccion = GRmenu.table(headers, filas, style: 3, header_color: "neon_yellow")

# O mediante keywords:
seleccion = GRmenu.table(
  headers: headers,
  rows: filas,
  title: "Monitor de Infraestructura",
  search: true,
  sort: true,
  page_size: 5,
  style: 3
)
```

---

### 10. Tarjetas y Alertas Estilizadas

Cuadros informativos con división automática de párrafos (*word-wrapping*) y soporte completo para colores TrueColor y Neón:

```ruby
# Alertas contextuales
GRmenu.alert(:success, "Conexion establecida con el servidor.")
GRmenu.alert(:warning, "Memoria RAM al 85%.", pause: false)

# Tarjeta con argumentos posicionales (ideal para respuestas y logs)
GRmenu.card("NGINX Web Server", "NGINX iniciado en el puerto 80 (PID 1024)", style: 3, border_color: "neon_green", pause: false)

# Tarjeta con argumentos por palabra clave
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

### 11. Colores Hexadecimales TrueColor y Catalogo de 90+ Colores

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

---

### 12. Iluminacion Dinamica Living Neon a 30 FPS

Al configurar `animate: "diagonal"`, `"linear"` o `"fade"`, el motor proyecta una ola de luz senoidal continua en tiempo real a 30 FPS que barre los marcos y los banners con destellos de incandescencia (*glow*), sin introducir ningun lag:

```ruby
menu = GRmenu.new(
  opciones,
  banner: "THEMES",
  title: "Efecto Neon Vivo",
  style: 3,
  animate: "diagonal"
)
menu.set_style.border("neon_red").banner("neon_red").focus("neon_yellow")
menu.draw
```

---

### 13. Seleccion Multiple con Checkboxes

Permite seleccionar múltiples elementos simultáneamente mediante casillas de verificación interactivas `[X]` / `[ ]`:

```ruby
paquetes = [
  ["Servidor Nginx Web", true, "Proxy inverso de alta velocidad"],
  ["Base de Datos PostgreSQL 16", true, "Motor de datos principal"],
  ["Almacen de Cache Redis 7.2", false, "Cache en memoria RAM"]
]

seleccionados = GRmenu.checkbox(
  paquetes,
  title: "Instalador de Paquetes",
  color: "neon_cyan",
  style: 3
)
```

* **Teclas:** `Espacio` para marcar/desmarcar, `a` (todos), `n` (ninguno), `i` (invertir), `Enter` (confirmar).

---

### 14. Control Deslizante Interactivo

Barra horizontal ajustable en tiempo real con flechas:

```ruby
ram = GRmenu.slider("Asignar Memoria RAM:", min: 1, max: 64, step: 1, default: 16, unit: "GB", color: "gold", style: 3)
```

---

### 15. Modales Nativos de Confirmacion

```ruby
if GRmenu.confirm("Deseas aplicar los cambios en produccion?", default: true, color: "neon_green", style: 3)
  puts "Aplicando..."
end
```

---

### 16. Renderizado Universal de Imagenes

Decodifica y renderiza cualquier formato de imagen (PNG, JPEG, JPG, WEBP, GIF, BMP) con **micro-subpíxeles ANSI TrueColor de 24 bits** usando medios bloques `▀` (2 píxeles verticales por carácter, relación 1:1) y remuestreo Lanczos:

```ruby
GRmenu.image("logo.png", width: 40, style: 3, color: "neon_cyan", center: true)
```

---

### 17. Barra de Progreso y Spinner de Carga

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

### 18. Banners 3D y Modulo de Color

```ruby
GRmenu.banner("ADMIN", 0, color: "neon_red", style: 3, font: 1)
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
| `functions` | `Array` | *Obligatorio* | Lista de metodos, simbolos, arrays `[nombre, accion, tooltip]`, submenus anidados o hashes. |
| `title:` | `String` | `""` | Titulo centrado en la cabecera del marco de opciones. |
| `banner:` | `String` | `""` | Texto convertido a arte ASCII 3D superior. |
| `subtitle:` | `String` | `""` | Descripcion o subtitulo (soporta saltos de linea `\n`). |
| `search:` | `Boolean` | `false` | Activa el buscador instantaneo mientras se escribe. |
| `columns:` | `Integer` | `1` | Cantidad de columnas para distribucion en cuadricula 2D. |
| `page_size:` | `Integer` | `auto` | Maximo de filas visibles antes de activar desplazamiento con scroll. |
| `mouse:` | `Boolean` | `false` | Activa soporte de raton ANSI SGR 1006 (clic, scroll, submenus). |
| `tabs:` | `Hash` | `nil` | Especifica estructura de pestanas horizontales. |
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
| `GRmenu.tabs` | `(tabs_hash, **opciones)` | Crea un menu interactivo dividido por pestanas horizontales. |
| `GRmenu.theme` | `(nombre_o_simbolo)` | Carga un tema `.gr` predefinido para todo el sistema. |
| `GRmenu.import_config` | `(ruta_archivo_gr)` | Carga un archivo de tema `.gr` personalizado. |
| `GRmenu.export_from_file`| `(script_origen, archivo_gr)` | Extrae el tema de un script sin correr bucles. |
| `GRmenu.style` | `(texto_css_gr)` | Inyecta estilos CSS inline globalmente. |
| `GRmenu.table` | `(headers, rows, ...)` | Muestra tabla interactiva con buscador y ordenamiento. |
| `GRmenu.card` | `(title, content, ...)` | Muestra tarjeta estilizada con auto-wrap y pause configurable. |
| `GRmenu.alert` | `(tipo, mensaje, ...)` | Muestra alerta emergente estilizada. |
| `GRmenu.checkbox` | `(items, ...)` | Devuelve array con items marcados (`[X]`). |
| `GRmenu.slider` | `(prompt, ...)` | Devuelve valor numerico seleccionado en barra interactiva. |
| `GRmenu.confirm` | `(pregunta, ...)` | Devuelve booleano (`true`/`false`) con botones interactivos. |
| `GRmenu.input` | `(title: ..., label: ..., ...)` | Entrada de texto redisenada con marco y cursor `█`. |
| `GRmenu.image` | `(filepath, width:, style:, color:)` | Renderiza imagen en TrueColor 24-bit (Lanczos / Zlib). |
| `GRmenu.progress` | `(total = 100, ... &bloque)` | Barra de progreso dinamica con bloque. |
| `GRmenu.spinner` | `(mensaje, ... &bloque)` | Spinner animado no bloqueante. |
| `GRmenu.banner` | `(texto, delay = 0, ...)` | Imprime banner ASCII 3D. |
| `GRmenu.help` | `()` | Muestra guia completa de documentacion en consola. |

---

## Mapa de Controles: Teclado y Raton

| Control | Contexto | Accion Realizada |
|:--------|:---------|:-----------------|
| `↑` (Arriba) / `k`  | Menus / Tablas / Checkbox | Mueve el foco hacia arriba (con salto continuo *Snake* en extremos). |
| `↓` (Abajo) / `j`   | Menus / Tablas / Checkbox | Mueve el foco hacia abajo. |
| `Tab` / `Shift+Tab` | Pestanas (`tabs`) | Cambia a la siguiente o anterior pestana. |
| `→` (Derecha)       | Submenus / Grid 2D | Abre submenu lateral (hasta 3 niveles) o salta columna en grid 2D. |
| `←` (Izquierda)     | Submenus / Grid 2D | Cierra el submenu lateral actual y regresa al nivel padre. |
| `Clic Izquierdo`    | Raton (`mouse: true`) | Enfoca la opcion; si ya esta enfocada, la ejecuta inmediatamente. |
| `Clic en Pestana`   | Raton (`mouse: true`) | Salta instantaneamente a la pestana seleccionada. |
| `Clic en Submenu`   | Raton (`mouse: true`) | Abre o enfoca la caja del submenu correspondiente. |
| `Rueda de Scroll`   | Raton (`mouse: true`) | Desplaza el foco arriba o abajo (↑ / ↓) fluidamente en el panel activo. |
| `Clic en ▲ / ▼`     | Raton (`mouse: true`) | Sube o baja de pagina en paginacion. |
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
