"""Short clips made from nothing, for an install that has no media yet.

`demoClip` has the ffmpeg otto encodes with synthesise a clip from one of its
own test sources -- colour bars, a test card, a plain colour -- so no file,
download or network is needed. A clip is small and short: the point is to
have something real to edit, not footage. A 3-second 320x180 clip encodes in
about a second and costs a few kilobytes.
"""

import math
import numbers
import os
import subprocess
from uuid import uuid4

from moviepy.config import get_setting

from otto.exceptions import FFmpegException
from otto.render import AUDIO_FPS

DEMO_SOURCES = {
    'bars': 'smptebars',
    'testcard': 'testsrc',
    'color': 'color=c=0x101820',
}
"""The pictures a demo clip can show, by name: SMPTE colour bars, ffmpeg's
test card (a moving pattern with a counter), and a plain dark blue-grey."""

DEMO_SIZE = (320, 180)
"""A demo clip's (width, height) unless asked otherwise."""

DEMO_FPS = 24
"""A demo clip's frame rate unless asked otherwise."""

DEMO_DURATION = 3
"""A demo clip's length in seconds unless asked otherwise."""


def _positive(value, name):
    """Refuse a `value` that is not a positive, finite number."""
    if (
        isinstance(value, numbers.Real)
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value > 0
    ):
        return
    raise ValueError(f'{name} must be a positive number, not {value!r}')


def _size(size):
    """`size` as a (width, height) pair of positive whole numbers."""
    try:
        width, height = size
    except (TypeError, ValueError):
        width = height = None
    for side in (width, height):
        if (
            not (isinstance(side, numbers.Integral) and not isinstance(side, bool))
            or not side > 0
        ):
            raise ValueError(f'size must be (width, height) in pixels, not {size!r}')
    return int(width), int(height)


def _source(source, duration, size, fps):
    """The lavfi source that draws `source` at `size` and `fps` for `duration`."""
    name, _, options = DEMO_SOURCES[source].partition('=')
    width, height = size
    settings = [options] if options else []
    settings += [f'size={width}x{height}', f'rate={fps}', f'duration={duration}']
    return f'{name}={":".join(settings)}'


def demoClip(
    filename,
    source='bars',
    duration=DEMO_DURATION,
    size=DEMO_SIZE,
    fps=DEMO_FPS,
    tone=None,
):
    """Write a demo clip to `filename`, an MP4 whatever it is called, and
    return `filename`.

    `source` names its picture, one of DEMO_SOURCES; it runs for `duration`
    seconds at `size` (width, height) and `fps` frames a second, in yuv420p
    so that a browser plays it. A clip is silent unless `tone` is a frequency
    in Hz: then it carries that sine, at -18 dBFS, for its whole length --
    1000 is bars and tone.

    The file appears whole or not at all: ffmpeg writes beside it under a
    hidden temporary name, which is moved into place once ffmpeg has finished,
    so a file already there is replaced only by a whole clip.

    Raises ValueError, before ffmpeg is asked anything, for a `source` that is
    not one of DEMO_SOURCES and for a duration, frame rate, size or tone that
    is not positive; FFmpegException, carrying what ffmpeg said, when ffmpeg
    does not write the clip; and OSError when ffmpeg cannot be started.
    """
    if source not in DEMO_SOURCES:
        raise ValueError(
            f'no demo source is named {source!r}; '
            f'the sources are {", ".join(DEMO_SOURCES)}'
        )
    _positive(duration, 'duration')
    _positive(fps, 'fps')
    size = _size(size)
    if tone is not None:
        _positive(tone, 'tone')

    inputs = ['-f', 'lavfi', '-i', _source(source, duration, size, fps)]
    if tone is not None:
        sine = f'sine=frequency={tone}:sample_rate={AUDIO_FPS}:duration={duration}'
        inputs += ['-f', 'lavfi', '-i', sine]
    directory, name = os.path.split(os.fspath(filename))
    partial = os.path.join(directory, f'.{name}.{uuid4().hex}.part')
    try:
        result = subprocess.run(
            [get_setting('FFMPEG_BINARY'), '-nostdin', '-y', *inputs]
            # yuv420p, which a browser plays. ffmpeg's test sources default to
            # a pixel format most players will not touch.
            + ['-pix_fmt', 'yuv420p']
            # The sound as AAC, which MP4 carries and a browser plays.
            + (['-c:a', 'aac'] if tone is not None else [])
            # Named, because the name it is written under says nothing about
            # the format.
            + ['-f', 'mp4', partial],
            capture_output=True,
            text=True,
            errors='replace',
        )
        if result.returncode != 0 or not os.path.isfile(partial):
            raise FFmpegException(
                f'ffmpeg could not write a demo clip to {filename}: '
                f'{result.stderr[-400:]}',
                stderr=result.stderr,
            )
        os.replace(partial, filename)
    except BaseException:
        try:
            os.remove(partial)
        except OSError:
            pass
        raise
    return filename
