from pydantic import BaseModel, AnyUrl
from typing import List, Tuple, Dict, Optional, Union

class FX(BaseModel):
    name: str
    data: Optional[dict]

class TemplateData(BaseModel):
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
    duration: float = 5
    type: Optional[str]
    name: Optional[str]
    inpoint: Optional[float]
    outpoint: Optional[float]
    offset: Optional[float]
    start: Optional[float]
    position: Optional[Union[Tuple, str]]
    resize: Optional[Union[float, tuple]]
    relative: Optional[bool] = True
    opacity: Optional[float]
    fadeOut: Optional[float] = 1
    fadeIn: Optional[float] = 1
    clipsize: Optional[tuple]
    data: Optional[TemplateData]



class Edl(BaseModel):
    clips: List[Clip]
    duration: float = None
