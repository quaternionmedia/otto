"""Otto models

Generic model classes for media and template data
"""

from pydantic import BaseModel
from typing import List, Tuple, Optional, Union, Literal


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

    A Clip is a single element of an EDL.
    """

    duration: float = 5
    """The length of the clip, in seconds"""

    type: Optional[str]
    """The source type: video, image, template"""

    name: Optional[str]
    """The name of the template, or the url of the media"""

    inpoint: Optional[float]
    """The start time of the clip"""

    outpoint: Optional[float]
    """The end time of the clip, relative to the beginning of the clip"""

    offset: Optional[float]
    """Offset the start time of the clip. **Depricated. Use start**"""

    start: Optional[float]
    """Offset the start time of the clip"""

    position: Optional[Union[Tuple, str]]
    """Change the (x, y) position of the clip"""

    resize: Optional[Union[float, tuple]]
    """Scale the clip by (x, y)"""

    relative: Optional[bool] = True
    """Use relative positioning. Default = True"""

    opacity: Optional[float]
    """The opacity of the clip.

    Values:
        0: transparent
        1.0: opaque"""
    fadeOut: Optional[float] = 1
    fadeIn: Optional[float] = 1
    clipsize: Optional[tuple]
    data: Optional[TemplateData]


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
