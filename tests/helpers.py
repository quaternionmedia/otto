"""Helpers shared by the test modules."""

import subprocess
from os import path

import numpy as np

from otto.models import Clip, TemplateData

TEST_DIR = path.dirname(path.realpath(__file__))
BLACK_MP4 = path.join(TEST_DIR, 'black.mp4')
BLACK_PNG = path.join(TEST_DIR, 'black.png')

SECONDS = [
    ('black', (0, 0, 0)),
    ('red', (255, 0, 0)),
    ('lime', (0, 255, 0)),
    ('blue', (0, 0, 255)),
]
"""The colour of each second of the `clock` media fixture."""


def color_clip(color='#00ff00', **attrs):
    """A makeColor template clip, which needs no media, ImageMagick or cairo."""
    attrs.setdefault('duration', 2.0)
    return Clip(
        type='template', name='makeColor', data=TemplateData(color=color), **attrs
    )


def pixel(video, t, x, y):
    """The RGB value of one pixel of `video` at time `t`, as ints."""
    return tuple(int(round(c)) for c in np.asarray(video.get_frame(t))[y, x][:3])


def close_to(actual, expected, tolerance=3):
    return all(abs(a - e) <= tolerance for a, e in zip(actual, expected))


def ffmpeg(*args):
    """Run the ffmpeg moviepy uses."""
    import imageio_ffmpeg

    subprocess.run(
        [imageio_ffmpeg.get_ffmpeg_exe(), '-nostdin', '-y', '-loglevel', 'error']
        + list(args),
        check=True,
    )
