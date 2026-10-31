"""otto works on the Pillow alfred pins (9.5) and on Pillow 10 and later.

moviepy 1.0.3 resizes with `Image.ANTIALIAS`, which Pillow 10 removed.
"""

import warnings

import PIL
from moviepy.editor import ColorClip
from PIL import Image

import otto  # noqa: F401 - importing otto is what restores the name

PILLOW_MAJOR = int(PIL.__version__.split('.')[0])


def test_antialias_resolves_to_lanczos():
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', DeprecationWarning)
        assert Image.ANTIALIAS == Image.LANCZOS


def test_pillow_is_only_touched_when_it_lacks_the_name():
    defined_here = 'ANTIALIAS' in vars(Image)
    # Pillow 9 serves the name itself, through its module __getattr__.
    assert defined_here == (PILLOW_MAJOR >= 10)


def test_moviepy_can_resize():
    shrunk = ColorClip((10, 8), color=(255, 0, 0)).resize(0.5)
    assert shrunk.get_frame(0).shape == (4, 5, 3)
