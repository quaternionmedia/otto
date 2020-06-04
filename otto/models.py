from pydantic import BaseModel, AnyUrl
from typing import List

class VideoForm(BaseModel):
    NAME: str
    LOGO: str #AnyUrl
    ADDRESS: str
    PHONE: str
    HOURS: str
    WEBSITE: str #AnyUrl = "talahairstudio.com"
    INITIAL: str
    BULLETS: str
    OPTIONAL: str = ""
    MEDIA: List[str] = ["videos/talavid.mp4", "audios/talaaudio.mp3"]
    CALL: str
    CLOSING: str
    FONTCOLOR: str = "#FFFFFF"
    THEMECOLOR: str = "#CC5500"
    FONT: str = "Segoe_UI_Bold"
