"""Otto models

Generic model classes for media and template data
"""

from typing import List, Literal, Optional, Tuple, Union

from pydantic import BaseModel


class FX(BaseModel):
    """FX options"""

    name: str
    data: Optional[dict]


class TemplateData(BaseModel):
    """Options for Template data"""

    text: Optional[str]
    textsize: Optional[tuple]
    color: Optional[str]
    themecolor: Optional[str]
    fontsize: Optional[float]
    font: Optional[str]
    method: Optional[str] = 'label'
    bg: Optional[str]
    align: Optional[str]
    position: Optional[Union[Tuple, str]]
    fxs: Optional[List[FX]]


class Clip(BaseModel):
    """Generic Clip properties

    A Clip is a single element of an EDL. `otto.render.generateEdl` documents
    how the timing fields combine.
    """

    duration: float = 5
    """How long the clip plays, in seconds, when it has no `outpoint`"""

    type: Optional[str]
    """The source type: template, video, image or audio"""

    name: Optional[str]
    """The name of the template, or the path or URL of the media"""

    inpoint: Optional[float]
    """Where playback begins in the source, in seconds. Default 0"""

    outpoint: Optional[float]
    """Where playback ends in the source, in seconds.

    When given, the clip plays for `outpoint - inpoint` seconds and `duration`
    is not consulted."""

    offset: Optional[float]
    """**Deprecated: use `start` or `inpoint`.**

    A positive offset is added to `start`, a negative one to `inpoint`."""

    start: Optional[float]
    """Where the clip begins in the output, in seconds. Absent is 0"""

    position: Optional[Union[Tuple, str]]
    """The (x, y) position of the clip in the frame.

    Video and image clips without one are centred."""

    resize: Optional[Union[float, tuple]]
    """Scale the clip by a factor, or to (width, height), after it is fitted"""

    relative: Optional[bool] = True
    """Use relative positioning. Default = True"""

    opacity: Optional[float]
    """The opacity of the clip.

    Values:
        0: transparent
        1.0: opaque"""
    fadeOut: Optional[float] = 1
    """Seconds of fade at the end of the clip; 0 or null for none"""

    fadeIn: Optional[float] = 1
    """Seconds of fade at the start of the clip; 0 or null for none"""

    clipsize: Optional[tuple]
    """The size a template is drawn at, or the box media is fitted into.

    Defaults to the frame."""

    data: Optional[TemplateData]
    """What a template clip draws. Required for template clips"""


class Edl(BaseModel):
    """EDL: Edit Decision List

    A data object representing the video to be renendered.

    Attributes:
        clips: List[Clip] A list of clips
        duration: float = None
    """

    clips: List[Clip]
    duration: float = None


class Render(BaseModel):
    edl: Edl
    width: Optional[int] = 1920
    height: Optional[int] = 1080
    fps: Optional[float] = 30.0


ImageFormat = Literal['jpg', 'png']
"""Available Image output formats"""


VideoFormat = Literal['mp4', 'mkv', 'mpg', 'avi']
"""Available Video output formats"""
