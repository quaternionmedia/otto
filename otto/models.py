from pydantic import BaseModel, AnyUrl
from typing import List, Dict, Optional, Union


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
