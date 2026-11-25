"""What a media file holds: how long it runs, how big its picture is, how
fast its frames come, and whether it has a sound; and how much its picture
moves over time.

`probe` asks the ffmpeg otto encodes with to describe a file -- `ffmpeg -i`,
which reads the file's headers, prints what it found and exits, decoding
nothing -- and `parse` reads that description. `motion` has the same ffmpeg
decode the picture small and measures how much it changes from one moment
to the next. Each call starts ffmpeg once: a caller that asks about the same
files often keeps the answers itself, keyed by whatever says a file has
changed.
"""

import os
import re
import subprocess
from typing import List, NamedTuple, Optional, Tuple

import numpy as np
from moviepy.config import get_setting

from .exceptions import FFmpegException

PROBE_TIMEOUT = 10
"""Seconds `probe` gives ffmpeg to describe a file. Long enough for a large
file on a slow disk: ffmpeg reads only the headers."""

PROBE_TYPES = ('video', 'image', 'audio')
"""The clip types `probe` can describe a file as."""


class MediaInfo(NamedTuple):
    """What is known about a media file. Anything unknown is None."""

    duration: Optional[float] = None
    """Seconds, to the millisecond."""

    width: Optional[int] = None
    """The picture's width as it is shown: a quarter turn swaps it with the
    height."""

    height: Optional[int] = None
    """The picture's height as it is shown."""

    fps: Optional[float] = None
    """Frames a second."""

    sound: Optional[bool] = None
    """Whether the file has a sound stream."""

    @property
    def size(self):
        """The picture's (width, height) as it is shown, or None."""
        if self.width is None or self.height is None:
            return None
        return (self.width, self.height)


UNKNOWN = MediaInfo()
"""What is known about a file ffmpeg cannot describe: nothing."""

_DURATION = re.compile(r'Duration:\s*(\d+):(\d{2}):(\d{2}(?:\.\d+)?)')
_STREAM = re.compile(r'Stream #\d+:\d+')
_VIDEO_STREAM = re.compile(r'Stream #\d+:\d+.*?: Video: (?P<description>.*)')
_AUDIO_STREAM = re.compile(r'Stream #\d+:\d+.*?: Audio: ')
# The frame size follows ", " in the stream line. Codec tags such as
# `(avc1 / 0x31637661)` hold an `x` between digits too, but never after ", ".
_SIZE = re.compile(r', (\d{1,5})x(\d{1,5})(?=[ ,\[]|$)')
_FPS = re.compile(r', (\d+(?:\.\d+)?)(k?) fps')
_ROTATION = re.compile(
    r'(?:rotate\s*:\s*(-?\d+(?:\.\d+)?))|(?:rotation of (-?\d+(?:\.\d+)?) degrees)'
)


def _check_type(type):
    if type is not None and type not in PROBE_TYPES:
        raise ValueError(
            f'a file is probed as one of {", ".join(PROBE_TYPES)}, not {type!r}'
        )


def rotation(description: str) -> float:
    """How far `ffmpeg -i`'s description of an input says its picture is
    turned, in degrees, or 0 when it says nothing of it.

    ffmpeg says it as a `rotate` tag (ffmpeg 4) or as a display matrix, which
    it spells `displaymatrix:` (ffmpeg 7.0) or `Display Matrix:` (ffmpeg 9).
    Each is read; the first one ffmpeg printed is the answer.
    """
    match = _ROTATION.search(description)
    return float(match[1] or match[2]) if match else 0.0


def parse(description: str, type=None) -> MediaInfo:
    """Read what `ffmpeg -i` said about an input, on its standard error.

    `type` is the kind of clip the file is for, one of PROBE_TYPES, and leaves
    out what such a clip does not use: an `image` is a still, so it has no
    duration, no frame rate and no sound, whatever ffmpeg says (it gives a
    still a nominal 25 fps, and an animated GIF its own); `audio` has no
    picture, so an MP3's cover art is not one. None reads everything.

    The picture's size is as it is shown: a quarter turn, as `rotation` reads
    it, swaps its sides.
    `sound` is None when ffmpeg described no stream at all.
    """
    _check_type(type)
    duration = None
    match = _DURATION.search(description)
    if match and type != 'image':
        hours, minutes, seconds = match.groups()
        duration = round(int(hours) * 3600 + int(minutes) * 60 + float(seconds), 3)

    width = height = fps = None
    stream = _VIDEO_STREAM.search(description)
    if stream and type != 'audio':
        size = _SIZE.search(stream['description'])
        if size:
            width, height = int(size[1]), int(size[2])
            # A quarter turn shows the picture the other way round.
            if round(rotation(description)) % 180 == 90:
                width, height = height, width
        rate = _FPS.search(stream['description'])
        if rate and type != 'image':
            fps = float(rate[1]) * (1000 if rate[2] else 1)

    sound = None
    if type != 'image' and _STREAM.search(description):
        sound = bool(_AUDIO_STREAM.search(description))
    return MediaInfo(
        duration=duration, width=width, height=height, fps=fps, sound=sound
    )


def _describe(path, timeout):
    """ffmpeg's description of `path`: what it prints on standard error."""
    result = subprocess.run(
        # `file:` so a name is only ever a file, never another protocol.
        [
            get_setting('FFMPEG_BINARY'),
            '-hide_banner',
            '-nostdin',
            '-i',
            f'file:{os.fspath(path)}',
        ],
        capture_output=True,
        text=True,
        errors='replace',
        timeout=timeout,
    )
    return result.stderr or ''


def probe(path, type=None, timeout=PROBE_TIMEOUT) -> MediaInfo:
    """What the media file at `path` holds, as `parse` reads it: its duration,
    its picture's size and frame rate, and whether it has a sound.

    `type`, one of PROBE_TYPES or None, is the kind of clip the file is for;
    `parse` says what each leaves out. A file ffmpeg cannot describe -- one
    that is not media, or is not there -- is UNKNOWN: nothing is known.

    Starts ffmpeg once, and waits at most `timeout` seconds for it: longer is
    a TimeoutError. An ffmpeg that cannot be started is an OSError, as
    `subprocess` raises it. A `type` that is not one of PROBE_TYPES is a
    ValueError, before ffmpeg is asked anything.
    """
    _check_type(type)
    try:
        description = _describe(path, timeout)
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError(
            f'ffmpeg took longer than {timeout}s to describe {os.fspath(path)}'
        ) from exc
    return parse(description, type)


# --- motion -----------------------------------------------------------------------

MOTION_RATE = 4
"""How many times a second `motion` measures the picture, unless asked
otherwise: enough to place a burst of movement to the quarter second."""

MOTION_SIZE = (32, 18)
"""The size, in pixels, the picture is reduced to before it is measured:
enough to see a camera move or a figure cross the frame, at a fraction of
the cost of the full picture."""


class Motion(NamedTuple):
    """How much a picture changes over time."""

    rate: float
    """How many values a second."""

    values: List[float]
    """Each 0 to 1: the mean change of the picture from the moment before,
    over every pixel of the reduced grey picture, 1 being black to white
    everywhere. The first value is 0, there being no moment before it."""


def _check_motion(rate, size):
    if not isinstance(rate, (int, float)) or isinstance(rate, bool) or not rate > 0:
        raise ValueError(
            f'rate must be a positive number of values a second, not {rate!r}'
        )
    try:
        width, height = size
    except (TypeError, ValueError):
        raise ValueError(
            f'size must be (width, height) in pixels, not {size!r}'
        ) from None
    for side in (width, height):
        if isinstance(side, bool) or not isinstance(side, int) or not side > 0:
            raise ValueError(f'size must be (width, height) in pixels, not {size!r}')
    return float(rate), (int(width), int(height))


def _frames(path, rate, size, timeout) -> Tuple[bytes, str, int]:
    """The picture at `path`, `rate` frames a second at `size` in grey, as raw
    bytes: what ffmpeg wrote, what it said, and how it ended."""
    width, height = size
    result = subprocess.run(
        [
            get_setting('FFMPEG_BINARY'),
            '-hide_banner',
            '-nostdin',
            '-loglevel',
            'error',
            '-i',
            f'file:{os.fspath(path)}',
            '-vf',
            f'fps={rate:g},scale={width}:{height}:flags=area,format=gray',
            '-f',
            'rawvideo',
            '-',
        ],
        capture_output=True,
        timeout=timeout,
    )
    return (
        result.stdout,
        result.stderr.decode('utf-8', errors='replace'),
        result.returncode,
    )


def motion(path, rate=MOTION_RATE, size=MOTION_SIZE, timeout=None) -> Motion:
    """How much the picture of the video at `path` changes over time.

    ffmpeg decodes the picture at `rate` frames a second, reduced to `size`
    pixels in grey; each value is the mean absolute change from the frame
    before, over every pixel, as a fraction of black to white, so a still
    picture measures 0 throughout and a cut from one shot to another
    measures high for one value. A camera that moves, a figure that crosses
    the frame and a scene change all show; what the values do not say is
    which. `timeout` bounds ffmpeg in seconds; None waits for it. A whole
    recording is decoded, so the measure costs minutes for hours of picture:
    a caller keeps the answer.

    Raises ValueError, before ffmpeg is asked anything, for a `rate` or `size`
    that is not positive; FFmpegException, carrying what ffmpeg said, for a
    file whose picture ffmpeg cannot read -- not a video, not there, a sound
    with no picture; TimeoutError past `timeout`; and OSError when ffmpeg
    cannot be started.
    """
    rate, size = _check_motion(rate, size)
    try:
        raw, said, status = _frames(path, rate, size, timeout)
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError(
            f'ffmpeg took longer than {timeout}s to read the picture of {os.fspath(path)}'
        ) from exc
    pixels = size[0] * size[1]
    count = len(raw) // pixels
    if status != 0 or count == 0:
        raise FFmpegException(
            f'ffmpeg could not read the picture of {os.fspath(path)}: {said[-400:].strip()}',
            stderr=said,
        )
    frames = np.frombuffer(raw[: count * pixels], dtype=np.uint8).reshape(count, pixels)
    changes = np.abs(frames[1:].astype(np.int16) - frames[:-1].astype(np.int16))
    values = [0.0] + [round(float(v), 4) for v in changes.mean(axis=1) / 255.0]
    return Motion(rate=rate, values=values)
