from pydantic import BaseModel, AnyUrl
from typing import List, Dict
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
    optional: str = ''
    media: List[str] = ['']
    audio: List[str] = ['']
    call: str = ''
    closing: str = ''
    fontcolor: str = '#FFFFFF'
    themecolor: str = '#CC5500'
    font: str = 'Segoe_UI_Bold'
    duration: float = 5


class Edl(BaseModel):
    edl: List
    time: float = None
