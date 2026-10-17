import os
import re
import subprocess
from typing import NamedTuple

import numpy as np
from moviepy.audio.AudioClip import AudioClip, CompositeAudioClip
from moviepy.config import get_setting
from moviepy.editor import AudioFileClip, ColorClip, ImageClip, VideoFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.io.ffmpeg_reader import ffmpeg_parse_infos
from PIL import Image

from otto.exceptions import DownloadException, EdlException, EmptyClipsException
from otto.getdata import download
from otto.models import Edl
from otto.templates import TEMPLATES

CLIP_TYPES = ('template', 'video', 'image', 'audio')
"""The values a clip's `type` may take."""

AUDIO_FPS = 48000
"""The sample rate sound is decoded at, mixed at and encoded at.

Decoding every source at the rate the output is written at means ffmpeg does
any resampling, rather than the mix picking the nearest sample.
"""

DEFAULT_FPS = 30.0
"""The frame rate of a render that asks for none and has no clip that has one."""


def _describe(index, clip):
    """How an error names a clip: its index in the Edl, and its name."""
    return f'clip {index} ({clip.name!r})'


def _frame_size(moviesize):
    """`moviesize` as a (width, height) pair of positive ints."""
    try:
        width, height = (int(n) for n in moviesize)
    except (TypeError, ValueError):
        raise EdlException(
            f'moviesize must be (width, height), not {moviesize!r}'
        ) from None
    if width <= 0 or height <= 0:
        raise EdlException(f'moviesize must be positive, not {moviesize!r}')
    return width, height


def _fit(size, box):
    """The largest size with the proportions of `size` that fits in `box`."""
    width, height = size
    scale = min(box[0] / width, box[1] / height)
    return max(1, round(width * scale)), max(1, round(height * scale))


_DISPLAY_MATRIX = re.compile(r'displaymatrix: rotation of (-?\d+(?:\.\d+)?) degrees')


def _rotation(path, infos):
    """How far the file says its picture is turned, in degrees.

    moviepy reads the `rotate` tag that ffmpeg 4 prints. ffmpeg 5 and later
    print only a display matrix -- imageio-ffmpeg 0.6 bundles ffmpeg 7 -- so
    without asking ffmpeg again, a portrait phone video looked unrotated.
    """
    if infos.get('video_rotation'):
        return infos['video_rotation']
    probe = subprocess.run(
        [get_setting('FFMPEG_BINARY'), '-hide_banner', '-i', path],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        errors='replace',
    )
    match = _DISPLAY_MATRIX.search(probe.stderr)
    return float(match.group(1)) if match else 0


def _open_video(path, box):
    """A video file, scaled by ffmpeg as it decodes to fit inside `box`."""
    infos = ffmpeg_parse_infos(path)
    if not infos.get('video_found'):
        raise ValueError('it has no video stream')
    width, height = infos['video_size']
    if round(_rotation(path, infos)) % 180 == 90:
        # ffmpeg turns the frames upright as it decodes them, so the picture
        # has the displayed proportions rather than the stored ones.
        width, height = height, width
    fitted = _fit((width, height), box)
    source = VideoFileClip(path, target_resolution=fitted[::-1], audio_fps=AUDIO_FPS)
    # Past its end a video holds its last frame. Left to itself the reader
    # returns whichever frame it read last: the last one when a render reads
    # in order, but the first one when a preview seeks straight past the end.
    last = max(0, source.duration - 1 / source.fps)
    return source.fl(lambda get_frame, t: get_frame(min(t, last)), apply_to=[])


def _open_image(path, box):
    """An image file scaled to fit inside `box`; its transparency, a mask."""
    with Image.open(path) as picture:
        transparent = 'A' in picture.getbands() or 'transparency' in picture.info
        picture = picture.convert('RGBA' if transparent else 'RGB')
    fitted = _fit(picture.size, box)
    if fitted != picture.size:
        picture = picture.resize(fitted, Image.LANCZOS)
    return ImageClip(np.array(picture))


class Timing(NamedTuple):
    """Where a clip sits on the output timeline, and what of its source plays."""

    start: float
    """Seconds into the output at which the clip begins."""

    inpoint: float
    """Seconds into the source at which playback begins."""

    length: float
    """Seconds the clip plays for."""

    @property
    def outpoint(self):
        """Seconds into the source at which playback ends."""
        return self.inpoint + self.length


def clipTiming(clip, where='clip'):
    """The Timing of `clip`, per the rules in `generateEdl`.

    Raises EdlException, prefixed with `where`, for timing that describes no
    clip: a negative start or inpoint, an outpoint not after the inpoint, a
    duration that is not positive.
    """
    for field in ('start', 'inpoint'):
        value = getattr(clip, field)
        if value is not None and value < 0:
            raise EdlException(f'{where}: {field} must not be negative, not {value}')
    offset = clip.offset or 0
    start = (clip.start or 0) + max(offset, 0)
    inpoint = (clip.inpoint or 0) + max(-offset, 0)
    if clip.outpoint is not None:
        if clip.outpoint <= inpoint:
            raise EdlException(
                f'{where}: outpoint ({clip.outpoint}) must be after '
                f'the inpoint ({inpoint})'
            )
        length = clip.outpoint - inpoint
    elif clip.duration is None or clip.duration <= 0:
        raise EdlException(f'{where}: duration must be positive, not {clip.duration}')
    else:
        length = clip.duration
    return Timing(start, inpoint, length)


def _check_resize(clip, where):
    """Refuse a `resize` that leaves nothing to draw.

    A factor of 0, or a negative or zero width or height, reached Pillow as an
    empty image and failed there, naming neither the clip nor the field.
    """
    if clip.resize is None:
        return
    factors = clip.resize if isinstance(clip.resize, (tuple, list)) else [clip.resize]
    if not factors or not all(
        isinstance(f, (int, float)) and not isinstance(f, bool) and f > 0
        for f in factors
    ):
        raise EdlException(
            f'{where}: resize must be a positive factor or (width, height), '
            f'not {clip.resize!r}'
        )


def _fade(clip, field, where):
    """Seconds of fade asked for: 0 (no fade) when the field is 0 or null."""
    seconds = getattr(clip, field)
    if seconds is None:
        return 0
    if seconds < 0:
        raise EdlException(f'{where}: {field} must not be negative, not {seconds}')
    return seconds


def _place_sound(source, timing, fade_in, fade_out, where):
    """An audio clip's sound, cut to its timing and faded, ready to mix."""
    if timing.inpoint >= source.duration:
        raise EdlException(
            f'{where}: inpoint {timing.inpoint} is not in its source, '
            f'which is {source.duration:g} seconds long'
        )
    # Past the end of its source a sound is silence; moviepy raises when asked
    # to read there, so stop at the end instead.
    sound = source.subclip(timing.inpoint, min(timing.outpoint, source.duration))
    sound = sound.set_start(timing.start)
    if fade_in > 0:
        sound = sound.audio_fadein(fade_in)
    if fade_out > 0:
        sound = sound.audio_fadeout(fade_out)
    return sound


def _soundtrack(audio):
    """generateEdl's `audio`: None, an AudioClip, or a path or URL to a file."""
    if audio is None or isinstance(audio, AudioClip):
        return audio
    if isinstance(audio, str):
        try:
            return AudioFileClip(download(audio), fps=AUDIO_FPS)
        except Exception as exc:
            raise EdlException(f'soundtrack {audio!r}: {exc}') from exc
    raise EdlException(
        'audio must be an AudioClip or a path or URL to an audio file, '
        f'not {type(audio).__name__}'
    )


def _make_template(clip, where, moviesize, duration):
    """Build a template clip from the registry, or say why it cannot be built."""
    template = TEMPLATES.get(clip.name)
    if template is None:
        raise EdlException(
            f'{where}: no template is named {clip.name!r}; '
            f'the templates are {", ".join(TEMPLATES)}'
        )
    if clip.data is None:
        raise EdlException(f'{where}: a template clip needs `data`')
    try:
        made = template(
            **clip.data.dict(exclude_none=True),
            clipsize=clip.clipsize or moviesize,
            duration=duration,
        )
    except Exception as exc:
        raise EdlException(
            f'{where}: template {clip.name!r} could not be built: '
            f'{type(exc).__name__}: {exc}'
        ) from exc
    if made is None:
        raise EdlException(f'{where}: template {clip.name!r} built nothing')
    return made


def _media_path(clip, where):
    """The local file a media clip plays, downloading it if it is remote.

    Leaves `clip.name` as the caller wrote it.
    """
    if not clip.name:
        raise EdlException(f'{where}: a {clip.type} clip needs a `name`')
    try:
        return download(clip.name)
    except DownloadException as exc:
        raise EdlException(f'{where}: {exc}') from exc


def generateEdl(edl: Edl, moviesize=(1920, 1080), audio=None, **kwargs):
    """Generates a moviepy CompositeVideoClip from an Edl

    **Timing.** Clips are layered, not sequenced: each is placed by its own
    timing, and clips that overlap in time are stacked in list order, later
    clips on top.

    - `start` is where the clip begins in the output, in seconds. A clip with
      no start begins at 0, exactly as one with `start: 0` does.
    - `inpoint` is where playback begins in the clip's source (default 0).
    - `outpoint`, when given, is where playback ends in the source, and the
      clip plays for `outpoint - inpoint` seconds; `duration` is then not
      consulted. Without an outpoint the clip plays for `duration` seconds.
      alfred sends both, with `duration == outpoint - inpoint`.
    - `offset` is deprecated: a positive offset is added to `start`, a
      negative one to `inpoint`.
    - `fadeIn` and `fadeOut` are seconds of fade; 0 or null is no fade. They
      are the only fades a clip gets: templates do not add their own.
    - `opacity`, when given, scales the clip's opacity: 0 is invisible.
    - `Edl.duration`, when given, is the length of the output; otherwise the
      output ends with its last clip.

    A video that ends before its clip does holds its last frame. A template is
    built with enough duration to cover `outpoint`.

    **Sound.** Audio clips are mixed, never drawn: their timing works as
    above, and their fades fade the volume. The sound of video clips is mixed
    with them, as is `audio` -- a soundtrack, given as an AudioClip or a path
    or URL to an audio file -- from the start of the output. Sound that ends
    before its clip does is followed by silence. An Edl of audio clips alone
    renders over black.

    **Geometry.** The result is `moviesize` (width, height), whatever size its
    clips are. Video and image clips are scaled to fit inside the frame -- or
    inside their `clipsize`, when they have one -- keeping their proportions,
    and `resize` then scales them further. A video or image clip with no
    `position` is centred in the frame.

    **Errors.** Raises EdlException naming the clip -- `clip 2 ('title'):
    ...` -- for a clip that cannot be rendered: a missing or unknown `type`, a
    template name that is not in `otto.templates.TEMPLATES`, a template clip
    without `data`, a template that fails, media that cannot be fetched or
    opened, timing that describes no clip, a negative fade, an opacity outside
    0..1, a resize that is not positive.
    """
    if len(edl.clips) == 0:
        raise EmptyClipsException('There were no clips in the Edl')
    moviesize = _frame_size(moviesize)
    if edl.duration is not None and edl.duration <= 0:
        raise EdlException(f'Edl duration must be positive, not {edl.duration}')
    clips = []
    sounds = []
    ends = []
    for index, clip in enumerate(edl.clips):
        where = _describe(index, clip)
        if clip.type not in CLIP_TYPES:
            raise EdlException(
                f'{where}: unknown clip type {clip.type!r}; '
                f'a clip is one of {", ".join(CLIP_TYPES)}'
            )
        timing = clipTiming(clip, where)
        fade_in = _fade(clip, 'fadeIn', where)
        fade_out = _fade(clip, 'fadeOut', where)
        if clip.opacity is not None and not 0 <= clip.opacity <= 1:
            raise EdlException(
                f'{where}: opacity must be between 0 and 1, not {clip.opacity}'
            )
        _check_resize(clip, where)
        box = clip.clipsize or moviesize
        try:
            if clip.type == 'template':
                c = _make_template(clip, where, moviesize, timing.outpoint)
            elif clip.type == 'video':
                c = _open_video(_media_path(clip, where), box)
            elif clip.type == 'audio':
                c = AudioFileClip(_media_path(clip, where), fps=AUDIO_FPS)
            elif clip.type == 'image':
                c = _open_image(_media_path(clip, where), box)
        except EdlException:
            raise
        except Exception as exc:
            raise EdlException(
                f'{where}: could not be opened: {type(exc).__name__}: {exc}'
            ) from exc

        ends.append(timing.start + timing.length)
        if clip.type == 'audio':
            sounds.append(_place_sound(c, timing, fade_in, fade_out, where))
            continue

        # A video's sound can end before its picture does. Drop sound that has
        # ended before the clip begins, and below, stop it where it ends.
        if c.audio is not None and c.audio.duration <= timing.inpoint:
            c = c.without_audio()
        sound_end = c.audio.duration if c.audio is not None else None

        # Which part of the source plays, and for how long. An image is the
        # same picture throughout, so only its length matters.
        try:
            if timing.inpoint and clip.type != 'image':
                c = c.subclip(timing.inpoint, timing.outpoint)
            else:
                c = c.set_duration(timing.length)
        except Exception as exc:
            raise EdlException(
                f'{where}: inpoint {timing.inpoint} is not in its source: {exc}'
            ) from exc
        if sound_end is not None and sound_end - timing.inpoint < timing.length:
            c = c.set_audio(c.audio.set_duration(sound_end - timing.inpoint))

        if clip.resize:
            c = c.resize(clip.resize)
        if clip.position:
            c = c.set_position(clip.position, relative=clip.relative)
        elif clip.type in ('video', 'image'):
            c = c.set_position('center')
        c = c.set_start(timing.start)
        if fade_in > 0:
            c = c.crossfadein(fade_in)
        if fade_out > 0:
            c = c.crossfadeout(fade_out)
        if clip.opacity is not None:
            c = c.set_opacity(clip.opacity)
        clips.append(c)

    if not clips:
        # Nothing to see: the sound plays over black.
        clips.append(ColorClip(moviesize, color=(0, 0, 0)).set_duration(max(ends)))
    # Sized explicitly: without `size`, a composite takes its first clip's.
    video = CompositeVideoClip(clips, size=moviesize)

    tracks = [video.audio] if video.audio is not None else []
    tracks += sounds
    soundtrack = _soundtrack(audio)
    if soundtrack is not None:
        tracks.append(soundtrack)
    if tracks:
        video = video.set_audio(CompositeAudioClip(tracks))
    return video.set_duration(edl.duration if edl.duration is not None else max(ends))


def renderMultitrack(
    edl: Edl,
    audio=None,
    filename='render.mp4',
    moviesize=(1920, 1080),
    logger='bar',
    fps=30.0,
    codec='libx264',
    bitrate=None,
    audio_bitrate='320k',
    ffmpeg_params=None,
    **kwargs,
):
    """Render v2: renders a multitrack Edl as seperate layers

    Writes `filename` at `moviesize` and `fps` frames per second. `audio` is a
    soundtrack mixed under the Edl's own sound; see `generateEdl`. An `fps` of
    None takes the fastest clip's frame rate, or DEFAULT_FPS.
    """
    if fps is not None and not fps > 0:
        raise EdlException(f'fps must be positive, not {fps}')
    video = generateEdl(edl, moviesize, audio=audio, **kwargs)
    if fps is None:
        fps = video.fps or DEFAULT_FPS
    video.write_videofile(
        filename,
        fps=fps,
        logger=logger,
        threads=8,
        audio_fps=AUDIO_FPS,
        audio_codec='aac',
        audio_bitrate=audio_bitrate,
        # Beside the output. moviepy otherwise writes the sound to the working
        # directory, named after the output's basename alone, so two renders
        # to the same name in different directories wrote the same file, and
        # a render from a read-only working directory failed.
        temp_audiofile=os.path.splitext(filename)[0] + '.audio.m4a',
        codec=codec,
        bitrate=bitrate,
        ffmpeg_params=ffmpeg_params,
    )
