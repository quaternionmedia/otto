import render
import os, json
from typing import List
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response, JSONResponse, FileResponse
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, AnyUrl
from getdata import urlToJson
from uvicorn import run

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
    MEDIA: List[str] = ["videos/talavid.mp4", "audios/talaaudio.mp3"]
    CALL: str
    CLOSING: str
    FONTCOLOR: str = "#FFFFFF"
    THEMECOLOR: str = "#CC5500"
    FONT: str = "Segoe_UI_Bold"

app = FastAPI()
# app.mount("/static", StaticFiles(directory='static', html=True), name="static")
templates = Jinja2Templates(directory="templates")

@app.post('/render')
async def process(request: Request):#vid_request: Video_Request):#
    form = await request.form()
    dform = dict(form)
    # print(dform['MEDIA'])
    # v = render.Otto(data=dform)
    # return dform

    with open("config_otto.json", "r") as config_file:
        config = json.load(config_file)


    returnDict = urlToJson(config['formpath'])

    # # v = render.Otto()
    #file_path = await v.render()
    # v.render()
    # return {'status': True }
    #return FileResponse( file_path )
    # return StreamingResponse(fake_video_streamer())
    return returnDict


@app.get("/")
async def main(request: Request):

    data = None
    data = Video_Request.parse_file('examples/talavideo.json')

    return templates.TemplateResponse("video_request.html", {"request": request, "vid_request": data.dict()})


if __name__ == '__main__':
    run(app, host='0.0.0.0', port=8000)
