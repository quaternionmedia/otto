![deploy](https://github.com/quaternionmedia/otto/actions/workflows/CI.yml/badge.svg)
![deploy](https://github.com/quaternionmedia/otto/actions/workflows/CD.yml/badge.svg)
[![codecov](https://codecov.io/gh/quaternionmedia/otto/branch/main/graph/badge.svg?token=1IYRXZPPYY)](https://codecov.io/gh/quaternionmedia/otto)

# otto

an ottomatic video creator

## Install from pip

```bash
pip install al-otto
```

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

Inlcudes pytest and other testing dependencies. Run with:

```bash
pytest
```

Can also be run with VSCode Python test extension, or VSCode debugger.

Tests marked `render` draw text and shapes, so they need what the `render`
extra needs from the system (below). The Dockerfile's `test` target has all of
it:

```bash
docker build --target test -t otto-test . && docker run --rm otto-test
```

### `render`

Includes the python dependencies needed for rendering and effects.

**NOTE** Requires a working installation of [imagemagick](https://imagemagick.org/)
whose security policy allows reading text from a file (moviepy passes text as
`@file`; Debian and Ubuntu forbid it), fonts, and cairo.

```bash
pip install .[render]
```

#### Remote media

A clip whose `name` is an `http(s)` URL is fetched before it is rendered: into
the directory `OTTO_DOWNLOAD_DIR` names, or else into a cache of the user's own
under the system temporary directory -- never the working directory. Each file
is named by a hash of its URL and is fetched once.

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
