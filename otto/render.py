from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.AudioClip import CompositeAudioClip
from otto.templates import TEMPLATES
from otto.getdata import download
from otto.models import Edl
from otto.exceptions import DownloadException, EmptyClipsException, EdlException

CLIP_TYPES = ('template', 'video', 'image', 'audio')
"""The values a clip's `type` may take."""


def _describe(index, clip):
    """How an error names a clip: its index in the Edl, and its name."""
    return f'clip {index} ({clip.name!r})'


def _make_template(clip, where, moviesize):
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
            duration=clip.duration,
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

    Raises EdlException naming the clip -- `clip 2 ('title'): ...` -- for a
    clip that cannot be rendered: a missing or unknown `type`, a template name
    that is not in `otto.templates.TEMPLATES`, a template clip without `data`,
    a template that fails, media that cannot be fetched or opened.
    """
    if len(edl.clips) == 0:
        raise EmptyClipsException('There were no clips in the Edl')
    clips = []
    for index, clip in enumerate(edl.clips):
        where = _describe(index, clip)
        if clip.type not in CLIP_TYPES:
            raise EdlException(
                f'{where}: unknown clip type {clip.type!r}; '
                f'a clip is one of {", ".join(CLIP_TYPES)}'
            )
        try:
            if clip.type == 'template':
                c = _make_template(clip, where, moviesize)
            elif clip.type == 'video':
                c = VideoFileClip(
                    _media_path(clip, where), target_resolution=(moviesize[1], None)
                )
            elif clip.type == 'audio':
                c = CompositeAudioClip(
                    [AudioFileClip(_media_path(clip, where), fps=48000)]
                )
                audio = c.audio_fadein(1).audio_fadeout(1)
            elif clip.type == 'image':
                c = CompositeVideoClip([ImageClip(_media_path(clip, where))])
        except EdlException:
            raise
        except Exception as exc:
            raise EdlException(
                f'{where}: could not be opened: {type(exc).__name__}: {exc}'
            ) from exc

        # Apply Effects
        if clip.resize:
            c = c.resize(clip.resize)
        if clip.offset:
            if clip.offset < 0:
                c = c.subclip(-clip.offset)
            else:
                c = c.set_start(clip.offset)
        if clip.inpoint:
            c = c.subclip(clip.inpoint)
        # if clip.outpoint:
        #     c = c.set_duration(clip.outpoint - getattr(clip, 'inpoint', 0))
        if clip.duration is not None:
            c = c.set_duration(clip.duration)
        if clip.position:
            c = c.set_position(clip.position, relative=clip.relative)
        if clip.start:
            c = c.set_start(clip.start)
        if clip.fadeIn:
            c = c.crossfadein(clip.fadeIn)
        if clip.fadeOut:
            c = c.crossfadeout(clip.fadeOut)
        if clip.opacity:
            c = c.set_opacity(clip.opacity)
        # if clip.fxs:
        #     render fx
        clips.append(c)
    video = CompositeVideoClip(clips)
    if audio:
        video = video.set_audio(audio)
    if edl.duration:
        video = video.set_duration(edl.duration)
    # video = video.crossfadeout(1).audio_fadeout(1)
    return video


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
    """Render v2: renders a multitrack Edl as seperate layers"""
    video = generateEdl(edl, moviesize, **kwargs)
    video.write_videofile(
        filename,
        fps=30.0,
        logger=logger,
        threads=8,
        audio_fps=48000,
        audio_codec='aac',
        audio_bitrate=audio_bitrate,
        codec=codec,
        bitrate=bitrate,
        ffmpeg_params=ffmpeg_params,
    )
