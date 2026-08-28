<div align="center">

# GRmenu

**Menús de navegación por teclado para terminal, en modo TTY crudo**

Flechas arriba/abajo para moverte · `Enter` para elegir · `q` para salir

[![PyPI version](https://img.shields.io/pypi/v/grmenu?color=blue&label=PyPI)](https://pypi.org/project/grmenu/)
[![Python versions](https://img.shields.io/pypi/pyversions/grmenu)](https://pypi.org/project/grmenu/)
[![PyPI downloads](https://img.shields.io/pypi/dm/grmenu)](https://pypi.org/project/grmenu/)
[![License: MIT](https://img.shields.io/github/license/JoseEduardoGR/GRmenu)](LICENSE)
[![Publish to PyPI](https://github.com/JoseEduardoGR/GRmenu/actions/workflows/publish.yml/badge.svg)](https://github.com/JoseEduardoGR/GRmenu/actions/workflows/publish.yml)
[![GitHub last commit](https://img.shields.io/github/last-commit/JoseEduardoGR/GRmenu)](https://github.com/JoseEduardoGR/GRmenu/commits/main)
[![GitHub stars](https://img.shields.io/github/stars/JoseEduardoGR/GRmenu?style=social)](https://github.com/JoseEduardoGR/GRmenu/stargazers)

</div>

---

## ✨ Características

- 🎮 **Navegación con flechas** — arriba/abajo para moverte, `Enter` para ejecutar, `q` para salir
- 🎨 **20 estilos de borde** — desde ASCII clásico hasta caracteres Unicode y emoji-like
- 🌈 **Colores personalizables** — borde, opciones y foco por separado, con 8 colores en 2 tonos cada uno
- 📦 **Cero dependencias externas** — solo la librería estándar de Python (`termios`, `tty`, `os`)
- 🐍 **Ligero** — un único archivo, fácil de auditar y de vendorizar si hace falta
- 🐧 **Linux / macOS** — funciona en cualquier terminal POSIX

> ⚠️ Requiere una terminal real (TTY) en Linux o macOS. No funciona en Windows ni en streams no interactivos, porque usa los módulos `termios`/`tty` para leer teclas en modo crudo.

---

## 📦 Instalación

```bash
pip install grmenu
```

<sub>Requiere Python ≥ 3.9.</sub>

---

## 🚀 Uso rápido

```python
from GRmenu import GRmenu

def opcion_uno():
    print("elegiste uno")

def opcion_dos():
    print("elegiste dos")

menu = GRmenu([opcion_uno, opcion_dos], title="Mi menu", style=19)
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

### Colores (`SetStyle`)

Cada zona del menú se personaliza por separado. `level=1` es el tono normal y `level=2` el brillante.

```python
menu.SetStyle.Border("cyan")        # color del borde
menu.SetStyle.Options("white")      # color de las opciones no seleccionadas
menu.SetStyle.Focus("green", 2)     # color de la opción resaltada
```

Colores disponibles: `black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`.

### Estilos de borde (`style`)

El parámetro `style` acepta un número que define cómo se dibuja el marco del menú:

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

```python
menu = GRmenu([opcion_uno, opcion_dos], title="Mi menu", style=7)  # bordes redondeados
```

### Ancho del menú

`draw()` acepta `size_max`, el ancho mínimo en caracteres del cuadro (se expande automáticamente si el título o las opciones son más largos):

```python
menu.draw(size_max=30)
```

---

## 📖 Referencia de la API

### `GRmenu(functions, title="", style=19)`

| Parámetro   | Tipo         | Descripción                                      |
|-------------|--------------|---------------------------------------------------|
| `functions` | `list[Callable]` | Funciones a mostrar como opciones, en orden.  |
| `title`     | `str`        | Título mostrado en la cabecera del menú.          |
| `style`     | `int`        | Número de estilo de borde (ver tabla arriba).     |

### `menu.draw(size_max=20)`

Dibuja el menú y bloquea el hilo hasta que el usuario elige una opción (`Enter`) o sale (`q`).

### `menu.SetStyle`

| Método                          | Descripción                              |
|----------------------------------|-------------------------------------------|
| `SetStyle.Border(color, level=1)` | Color del marco del menú.               |
| `SetStyle.Options(color, level=1)`| Color de las opciones sin seleccionar.  |
| `SetStyle.Focus(color, level=2)`  | Color de la opción resaltada.           |

---

## 🧩 Ejemplo completo

```python
from GRmenu import GRmenu

def saludar():
    print("¡Hola!")

def salir_app():
    print("Hasta luego 👋")

def acerca_de():
    print("GRmenu v0.1.0 — menú TTY para terminal")

menu = GRmenu(
    [saludar, acerca_de, salir_app],
    title="GRmenu Demo",
    style=7,
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
