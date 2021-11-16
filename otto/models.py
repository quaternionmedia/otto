from pydantic import BaseModel, AnyUrl
from typing import List, Dict, Optional, Union
from otto.as_form import as_form

@as_form
class VideoForm(BaseModel):
    project: str = ''
    name: str = ''
    logo: str = '' #AnyUrl
    address: str = ''
    phone: str = ''
    hours: str = ''
    website: str = '' #AnyUrl = 'talahairstudio.com'
    initial: str = ''
    bullets: str = ''
    media: str = ''
    audio: str = ''
    call: str = ''
    closing: str = ''
    fontcolor: str = '#FFFFFF'
    themecolor: str = '#CC5500'
    font: str = 'Segoe_UI_Bold'
    duration: float = 5

class Clip(BaseModel):
    duration: float = 5
    type: Optional[str] = None
    name: Optional[str] = None
    inpoint: Optional[float] = None
    outpoint: Optional[float] = None
    offset: Optional[float] = None
    start: Optional[float] = None
    position: Optional[tuple] = None
    data: Optional[dict] = None
    resize: Optional[Union[float, tuple]]
    relative: Optional[bool] = True
    fxs: Optional[dict] = None


class Edl(BaseModel):
    clips: List[Clip]
    duration: float = None
