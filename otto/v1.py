# version 0.1 functions
# to be depricated
from fastapi import BackgroundTasks, Depends, Request
from fastapi.responses import HTMLResponse
from typing import List
from jinja2 import Environment
from starlette.responses import FileResponse
# from importlib import import_module
from moviepy.video.compositing.concatenate import concatenate_videoclips

from otto import templates, defaults
from otto.getdata import timestr
from otto.models import VideoForm
from otto.render import renderForm

env = Environment()

@app.post('/render')
async def queueRender(
        renderer: BackgroundTasks, 
        form: VideoForm = Depends(VideoForm.as_form)):
    """# Queue Render
    accepts a `VideoForm` and adds a task to the renderer"""
    ts = f'{timestr()}.mp4'
    print('rendering from form', form, ts)
    renderer.add_task(renderForm, dict(form), filename=os.path.join('videos', ts))
    return True

@app.get('/template/{template}')
async def renderTemplate(
        request: Request, 
        template: str, 
        width: int = 1920, 
        height: int = 1080):
    """# Render Template
    Renders a still image from query parameters of a `template` with `width` and `height` at time `t`
    
    Returns a PNG file response
    
    Depricated in favor of /preview
    """
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
        

@app.get('/form')
async def main(request: Request):
    data = VideoForm(**defaults.sample_forms[0]['form'])
    template = env.from_string(defaults.video_form)
    return HTMLResponse(template.render({"request": request, "video_data": data.dict()}))