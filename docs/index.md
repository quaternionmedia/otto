# Otto

The Ottomatic video engine

## Install

```bash
pip install al-otto
```

otto runs on Python `>=3.8.1,<3.12` (`requires-python` in pyproject.toml);
CI and the Dockerfile run 3.11. pydantic no longer sets the cap. Every release
`pydantic~=2.5` allows ships wheels for 3.12; a floor of 2.8 adds 3.13, and
2.12 adds 3.14. Raising the cap waits on the suite passing on the newer Python.

Drawing text and shapes needs the `render` extra (`pip install
al-otto[render]`) and, from the system, fonts, cairo, and ImageMagick with a
policy that lets it read text from a file. The
[README](https://github.com/quaternionmedia/otto#render) says why; the
Dockerfile's `test` target has all of it.

### From a clone

otto is packaged with [pdm](https://pdm-project.org), not Poetry.
`pyproject.toml` declares the dependencies and the optional groups (`render`,
`test`, `docs`); `pdm.lock` pins them all.

```bash
git clone https://github.com/quaternionmedia/otto.git
cd otto/
pdm install -G render -G test
```

pip installs from a clone too, resolving `pyproject.toml`'s ranges instead of
the lock:

```bash
pip install -e .[render,test]
```

## Guides

- [Rendering](rendering.md): encoding an Edl by a named preset, drawing one
  frame of it, and writing its sound alone. The
  [reference](reference/render.md) has each function.
- [Media files](media.md): what a file holds (how long it runs, how big its
  picture is, whether it has sound), and demo clips made from nothing.
