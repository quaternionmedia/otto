# Otto

The Ottomatic video engine

## Install

otto runs on Python 3.8.1 up to, but not including, 3.12: pyproject.toml
declares `requires-python = ">=3.8.1,<3.12"`. The cap is pydantic's. otto
allows `pydantic~=1.10`, and the oldest releases that admits support no
Python newer than 3.11, so the cap rises only with the pydantic floor. CI and
the Dockerfile run 3.11.

```bash
pip install al-otto
```

Drawing text and shapes needs the `render` extra (`pip install
al-otto[render]`) and, from the system, ImageMagick with a policy that lets it
read text from a file, fonts, and cairo. The README says why; the Dockerfile's
`test` target has all of it.

### From a clone

otto is packaged with [pdm](https://pdm-project.org), not Poetry:
`pyproject.toml` declares the dependencies and the optional groups (`render`,
`test`, `docs`), and `pdm.lock` pins all of them.

```bash
git clone https://github.com/quaternionmedia/otto.git
cd otto/
pdm install -G render -G test
```

pip installs from a clone too, resolving `pyproject.toml`'s ranges rather than
the lock:

```bash
pip install -e .[render,test]
```

## Rendering

[Rendering](rendering.md) says what otto does with an Edl: how it encodes one
by a named preset, draws one frame of it, and writes a timeline's sound alone.
The [reference](reference/render.md) has each function.

## Media files

[Media files](media.md) says how otto describes a file -- how long it runs,
how big its picture is, whether it has a sound -- and how it makes demo clips
from nothing, for an install with no media yet.
