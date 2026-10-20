![deploy](https://github.com/quaternionmedia/otto/actions/workflows/CI.yml/badge.svg)
![deploy](https://github.com/quaternionmedia/otto/actions/workflows/CD.yml/badge.svg)
[![codecov](https://codecov.io/gh/quaternionmedia/otto/branch/main/graph/badge.svg?token=1IYRXZPPYY)](https://codecov.io/gh/quaternionmedia/otto)

# otto

an ottomatic video creator

## Install from pip

```bash
pip install al-otto
```

otto runs on Python `>=3.8.1,<3.12` (`requires-python` in
[pyproject.toml](pyproject.toml)); CI and the Dockerfile run 3.11. The cap is
pydantic's; [docs/index.md](docs/index.md#install) says why.

## Optional packages

Otto ships with several optional packages, which can be installed with `pip` or `pdm`

#### pip install

```bash
pip install al-otto[test]
```

#### local pip install

```bash
pip install .[test]
```

#### pdm

```bash
pdm install -G test
```

## Rendering

| `otto.render` | does |
|---|---|
| `generateEdl` | builds an Edl into a moviepy clip |
| `renderMultitrack` | encodes it to a video file, by a named preset (`draft`, `standard` or `high`) if asked |
| `renderFrame` | writes one moment of it as a JPEG |
| `renderSound` | writes only its sound, as a mono 16-bit WAV at the rate asked for |

[docs/rendering.md](docs/rendering.md) has the details.

## Media files

- `otto.media.probe` says what a file holds: its duration, its picture's size
  as shown, its frame rate, and whether it has sound.
- `otto.demo.demoClip` makes a short clip from nothing (colour bars, a test
  card or a plain colour, silent or with a tone) for an install with no media
  yet.

Both run the ffmpeg otto encodes with. [docs/media.md](docs/media.md) has the
details.

## Development

0. Install pdm

```bash
pip install pdm
```

1. Clone the repository

```bash
git clone https://github.com/quaternionmedia/otto.git
```

2. cd into the repo

```bash
cd otto
```

3. Install the development dependencies

```bash
pdm install
```

4. Create a local virtual environment

```bash
pdm venv create
```

5. Activate your local virtual environment

```bash
eval $(pdm venv activate)
```

Or...

```bash
source .venv/bin/activate
```

Deactivate your virtual environment by running `deactivate`

### `test`

Includes pytest and other testing dependencies. Run with:

```bash
pytest
```

Can also be run with VSCode Python test extension, or VSCode debugger.

Tests marked `render` draw text and shapes, so they need the `render` extra's
system packages (below). The Dockerfile's `test` target has them all:

```bash
docker build --target test -t otto-test . && docker run --rm otto-test
```

### `render`

Includes the python dependencies needed for rendering and effects.

**NOTE** Requires, from the system, fonts, cairo, and
[imagemagick](https://imagemagick.org/) with a security policy that allows
reading text from a file: moviepy passes text as `@file`, which Debian and
Ubuntu forbid.

```bash
pip install .[render]
```

#### Remote media

A clip whose `name` is an `http(s)` URL is fetched once, before it is
rendered, into a file named by a hash of its URL. It goes to
`OTTO_DOWNLOAD_DIR` if set, else to a cache of the user's own under the system
temporary directory; never the working directory.

#### `docs`

Includes documentation building tool. Run with:

```bash
mkdocs serve -a 0.0.0.0:9000
```

Then visit [localhost:9000](http://localhost:9000/)

## nox

Running all tests and formatters can be done as a one-liner using `nox`

```bash
pip install nox
```

Then run:

```bash
nox
```

### Sessions

To run a single session, i.e. just the test suite, run:

```bash
nox -s coverage
```

See [noxfile.py](noxfile.py) for other commands.

## Credits

Created by [Quaternion Media, LLC](https://www.quaternion.media/)
