# import render
import os, json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, Response, JSONResponse, FileResponse
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from starlette.responses import FileResponse
from uvicorn import run
from otto.getdata import urlToJson
from otto.models import VideoForm
from otto import templates
from importlib import import_module
from moviepy.video.compositing.concatenate import concatenate_videoclips

app = FastAPI()
# app.mount("/static", StaticFiles(directory='static', html=True), name="static")
jt = Jinja2Templates(directory="templates")

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

@app.get('/template/{template}')
async def renderTemplate(request: Request, template: str, text='asdf'):
    # if import_module(f'otto.templates.{template}'):
    tmp = getattr(templates, template)
    if tmp:
        try:
            q = request.query_params
            clip = tmp(**q)
            if isinstance(clip, list):
                clip = concatenate_videoclips(clip)
            clip.save_frame('temp.png', t=q['t'])
            return FileResponse('temp.png')
        except Exception as e:
            raise HTTPException(status_code=500, detail='error making template')
    else: raise HTTPException(status_code=422, detail='no such template')

@app.get("/")
async def main(request: Request):

    data = None
    data = VideoForm.parse_file('examples/talavideo.json')

    return jt.TemplateResponse("VideoForm.html", {"request": request, "video_data": data.dict()})


if __name__ == '__main__':
    run(app, host='0.0.0.0', port=8000)
