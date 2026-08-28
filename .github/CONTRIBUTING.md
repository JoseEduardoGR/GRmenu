# Contribuir a GRmenu

Gracias por tu interés en contribuir. Esta guía es corta a propósito porque el proyecto también lo es.

## Antes de empezar

- Abrí un [issue](https://github.com/JoseEduardoGR/GRmenu/issues/new/choose) primero si vas a proponer un cambio grande, para discutir el enfoque antes de escribir código.
- Para bugs o mejoras chicas, podés ir directo a un pull request.

## Cómo levantar el proyecto

```bash
git clone https://github.com/JoseEduardoGR/GRmenu.git
cd GRmenu
pip install -e .
```

`GRmenu.py` es el único archivo del paquete — no hay dependencias externas.

## Probar tus cambios

El proyecto no tiene suite de tests automatizada porque depende de una TTY real (`termios`/`tty`) para leer teclas en modo crudo, algo que no se simula fácil en CI. Probá tus cambios a mano, en una terminal real:

```python
from GRmenu import GRmenu

def opcion_uno():
    print("ok")

menu = GRmenu([opcion_uno], title="Test", style=19)
menu.draw()
```

Verificá que las flechas, `Enter` y `q` se comporten como esperás, y que no queden secuencias de escape rotas al salir.

## Enviar un pull request

1. Forkeá el repo y creá una rama descriptiva (`fix-borde-ancho`, `feature-color-custom`, etc.)
2. Hacé el cambio más chico posible que resuelva el problema.
3. Abrí el PR contra `main` y completá la plantilla.

### Sobre versiones y releases

No necesitás tocar `pyproject.toml` ni crear tags vos mismo. Cuando el PR se mergea a `main`, un workflow automático sube el número de versión, crea el tag y publica en PyPI. Vos solo enfocate en el código.

## Licencia

Al contribuir, aceptás que tu código se distribuya bajo la misma licencia [MIT](../LICENSE) del proyecto.
