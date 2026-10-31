"""What a media file holds: how long it runs, how big its picture is, how
fast its frames come, and whether it has a sound.

`probe` asks the ffmpeg otto encodes with to describe a file -- `ffmpeg -i`,
which reads the file's headers, prints what it found and exits, decoding
nothing -- and `parse` reads that description. Each call starts ffmpeg once:
a caller that asks about the same files often keeps the answers itself, keyed
by whatever says a file has changed.
"""

import os
import re
import subprocess
from typing import NamedTuple, Optional

from moviepy.config import get_setting

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


def parse(description: str, type=None) -> MediaInfo:
    """Read what `ffmpeg -i` said about an input, on its standard error.

    `type` is the kind of clip the file is for, one of PROBE_TYPES, and leaves
    out what such a clip does not use: an `image` is a still, so it has no
    duration, no frame rate and no sound, whatever ffmpeg says (it gives a
    still a nominal 25 fps, and an animated GIF its own); `audio` has no
    picture, so an MP3's cover art is not one. None reads everything.

    The picture's size is as it is shown: a `rotate` tag (ffmpeg 4) or a
    display matrix (ffmpeg 5 and later) of a quarter turn swaps its sides.
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
            rotation = _ROTATION.search(description)
            if rotation:
                angle = float(rotation[1] or rotation[2])
                # A quarter turn shows the picture the other way round.
                if round(angle) % 180 == 90:
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
