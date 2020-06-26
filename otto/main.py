# import render
import os, json
from fastapi import FastAPI, Request, HTTPException, Form, BackgroundTasks, Depends
from fastapi.responses import HTMLResponse, Response, JSONResponse, FileResponse
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from jinja2 import Environment
from starlette.responses import FileResponse
from uvicorn import run
from otto.getdata import urlToJson, timestr
from otto.models import VideoForm, Edl
from otto.render import renderEdl, renderForm
from otto import Otto, templates, defaults
from importlib import import_module
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.editor import VideoFileClip
from typing import List

app = FastAPI()

env = Environment()
@app.get('/template/{template}')
async def renderTemplate(request: Request, template: str, text='asdf', width: int = 1920, height: int = 1080):
    # if import_module(f'otto.templates.{template}'):
    q = request.query_params
    clipsize = (width, height)
    print('making template', q, clipsize)
    tmp = getattr(templates, template)
    print('making tmp', tmp)
    if tmp:
        try:
            clip = tmp(**q, clipsize=clipsize)
            if isinstance(clip, list):
                clip = concatenate_videoclips(clip)
            clip.save_frame('temp.png', t=q['t'], withmask=True)
            return FileResponse('temp.png')
        except Exception as e:
            raise HTTPException(status_code=500, detail='error making template')
            print('error making template', e)
    else:
        raise HTTPException(status_code=422, detail='no such template')

@app.post('/render')
async def queueRender(renderer: BackgroundTasks, form: VideoForm = Depends(VideoForm.as_form)):
    ts = f'{timestr()}.mp4'
    print('rendering from form', form, ts)
    renderer.add_task(renderForm, dict(form), filename=os.path.join('videos', ts))
    return True

@app.get('/form')
async def main(request: Request):
    data = VideoForm(**defaults.sample_forms[0]['form'])
    template = env.from_string(defaults.video_form)
    return HTMLResponse(template.render({"request": request, "video_data": data.dict()}))


if __name__ == '__main__':
    run(app, host='0.0.0.0', port=9000)
