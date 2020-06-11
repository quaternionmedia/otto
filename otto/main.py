import render
import os, json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response, JSONResponse, FileResponse
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from uvicorn import run
from otto.getdata import urlToJson
from otto.models import VideoForm

app = FastAPI()
# app.mount("/static", StaticFiles(directory='static', html=True), name="static")
templates = Jinja2Templates(directory="templates")

@app.post('/render')
async def process(request: Request):#video_data: VideoForm):#
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
    data = VideoForm.parse_file('examples/talavideo.json')

    return templates.TemplateResponse("VideoForm.html", {"request": request, "video_data": data.dict()})


if __name__ == '__main__':
    run(app, host='0.0.0.0', port=8000)
