import render
import os, json
from typing import List
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response, JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, AnyUrl

class Video_Request(BaseModel):
    NAME: str
    LOGO: str #AnyUrl
    ADDRESS: str
    PHONE: str
    HOURS: str
    WEBSITE: str #AnyUrl = "talahairstudio.com"
    INITIAL: str
    BULLETS: str
    OPTIONAL: str = ""
    VIDEOS: List[str] = ["videos/talavid.mp4"]
    AUDIOS: List[str] = ["audios/talaaudio.mp3"]
    MEDIA: List[str]
    CALL: str
    CLOSING: str
    FONTCOLOR: str = "#FFFFFF"
    THEMECOLOR: str = "#CC5500"
    FONT: str = "Segoe_UI_Bold"

app = FastAPI()
# app.mount("/static", StaticFiles(directory='static', html=True), name="static")
templates = Jinja2Templates(directory="templates")

@app.post('/render')
async def process(vid_request: Video_Request):#request: Request):#
    # form = json.loads(json.dumps((await request.form()), default=lambda o: o.__dict__, indent=4))['_dict']
    print(vid_request)

    # print(form)
    # v = render.Otto(data=form)

    # # v = render.Otto()
    # # file = await v.render()
    # v.render()
    # return {'status': True }
    return {'status': True }
    # return StreamingResponse(fake_video_streamer())


@app.get("/")
async def main(request: Request):
    # content = """"""
    # return Response(content=content, )

    data = None
    with open('examples/talavideo.json') as json_file:
        data = Video_Request.parse_obj(json.load(json_file))
    # return JSONResponse(content=data.dict())

    return templates.TemplateResponse("video_request.html", {"request": request, "vid_request": data.dict()})


if __name__ == '__main__':
    run(app, host='0.0.0.0', port=8000)
