"""renderFrame draws one moment of an Edl and writes it as a JPEG.

alfred previewed a timeline by building it with generateEdl and calling
moviepy's `save_frame` on the result: frame handling in a control plane that is
meant to do none. otto draws the frame now -- the one renderMultitrack would
encode at that moment -- and writes it.

The pictures are flat colours, so a pixel read back from the JPEG says which
clip was drawn, within what JPEG's compression moves a colour.
"""

import numpy as np
import pytest
from PIL import Image

from helpers import SECONDS, close_to, color_clip
from otto.exceptions import EdlException, EmptyClipsException
from otto.models import Clip, Edl
from otto.render import generateEdl, renderFrame

FRAME = (64, 36)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# How far JPEG moves a flat colour, in any channel.
JPEG = 12


def still(color='#00ff00', **attrs):
    attrs.setdefault('fadeIn', 0)
    attrs.setdefault('fadeOut', 0)
    return color_clip(color, **attrs)


def read(path):
    """The image at `path`: its format, its size, and its pixels."""
    with Image.open(path) as picture:
        return picture.format, picture.size, np.asarray(picture.convert('RGB'))


def middle(pixels):
    height, width = pixels.shape[:2]
    return tuple(int(c) for c in pixels[height // 2, width // 2])


def test_it_writes_a_jpeg_of_the_size_asked_for_and_returns_its_name(tmp_path):
    path = str(tmp_path / 'frame.jpg')

    assert renderFrame(Edl(clips=[still()]), 0.5, path, moviesize=FRAME) == path

    kind, size, pixels = read(path)
    assert kind == 'JPEG'
    assert size == FRAME
    assert close_to(middle(pixels), GREEN, JPEG)


def test_it_is_a_jpeg_whatever_the_file_is_called(tmp_path):
    path = tmp_path / 'frame.png'
    renderFrame(Edl(clips=[still()]), 0.5, str(path), moviesize=FRAME)
    assert path.read_bytes()[:3] == b'\xff\xd8\xff'
    assert read(path)[0] == 'JPEG'


def test_the_frame_is_the_one_at_t(tmp_path):
    """Clips are layered by their timing: at 1.5 the second covers the first."""
    edl = Edl(clips=[still('#ff0000', duration=3), still(start=1, duration=1)])
    seen = []
    for t in (0.5, 1.5, 2.5):
        path = str(tmp_path / f'{t}.jpg')
        renderFrame(edl, t, path, moviesize=FRAME)
        seen.append(middle(read(path)[2]))

    assert close_to(seen[0], RED, JPEG)
    assert close_to(seen[1], GREEN, JPEG)
    assert close_to(seen[2], RED, JPEG)


def test_a_moment_no_clip_covers_is_black(tmp_path):
    path = str(tmp_path / 'frame.jpg')
    renderFrame(Edl(clips=[still(start=2, duration=1)]), 0.5, path, moviesize=FRAME)
    assert close_to(middle(read(path)[2]), BLACK, JPEG)


def test_a_video_s_frame_comes_from_its_moment_in_the_source(media, tmp_path):
    """The clock's colour says which second of the source was drawn."""
    clip = Clip(type='video', name=media['clock'], duration=4, fadeIn=0, fadeOut=0)
    path = str(tmp_path / 'frame.jpg')
    renderFrame(Edl(clips=[clip]), 2.5, path, moviesize=FRAME)
    assert close_to(middle(read(path)[2]), SECONDS[2][1], JPEG)


def test_it_is_the_frame_save_frame_wrote(tmp_path):
    """What alfred wrote before, through moviepy, is what is written now."""
    edl = Edl(clips=[still('#336699', duration=2), still(start=1, duration=1)])
    ours, theirs = str(tmp_path / 'ours.jpg'), str(tmp_path / 'theirs.jpg')

    renderFrame(edl, 1.5, ours, moviesize=FRAME)
    generateEdl(edl, FRAME).save_frame(theirs, t=1.5, withmask=False)

    assert np.array_equal(read(ours)[2], read(theirs)[2])


def test_a_clip_it_cannot_build_is_refused_and_nothing_is_written(tmp_path):
    """Wherever the clip is: the frame at 0 would not have shown this one."""
    inverted = still(start=5, inpoint=2, outpoint=1)
    path = tmp_path / 'frame.jpg'

    with pytest.raises(EdlException, match=r"clip 2 \('makeColor'\).*outpoint"):
        renderFrame(Edl(clips=[still(), inverted]), 0, str(path), moviesize=FRAME)

    assert not path.exists()


def test_an_empty_edl_is_refused_and_nothing_is_written(tmp_path):
    path = tmp_path / 'frame.jpg'
    with pytest.raises(EmptyClipsException):
        renderFrame(Edl(clips=[]), 0, str(path), moviesize=FRAME)
    assert not path.exists()
