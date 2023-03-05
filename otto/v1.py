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
from otto.as_form import as_form


@as_form
class VideoForm(BaseModel):
    project: str = ''
    name: str = ''
    logo: str = ''  # AnyUrl
    address: str = ''
    phone: str = ''
    hours: str = ''
    website: str = ''  # AnyUrl = 'talahairstudio.com'
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


env = Environment()


@app.post('/render')
async def queueRender(
    renderer: BackgroundTasks, form: VideoForm = Depends(VideoForm.as_form)
):
    """# Queue Render
    accepts a `VideoForm` and adds a task to the renderer"""
    ts = f'{timestr()}.mp4'
    print('rendering from form', form, ts)
    renderer.add_task(renderForm, dict(form), filename=os.path.join('videos', ts))
    return True


@app.get('/template/{template}')
async def renderTemplate(
    request: Request, template: str, width: int = 1920, height: int = 1080
):
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
    return HTMLResponse(
        template.render({"request": request, "video_data": data.dict()})
    )


def renderEdl(
    edl: Edl,
    media,
    audio=None,
    filename='render.mp4',
    moviesize=(1920, 1080),
    logger='bar',
):
    """Render v1 - Depricated in favor of renderMultitrack"""
    clips = []
    duration = 0
    media = [download(m) for m in media]
    for clip in edl.clips:
        print('making clip', clip, type(clip))
        duration += clip.duration
        if clip.type == 'template':
            tmp = getattr(templates, clip.name)
            print('making template', tmp)
            clips.append(tmp(**clip.data, duration=clip.duration, clipsize=moviesize))
        elif clip.type == 'video':
            clips.append(
                VideoFileClip(clip.name)
                .subclip(clip.inpoint)
                .set_duration(clip.duration)
            )
    print('made clips', clips)
    video = concatenate_videoclips(clips).resize(moviesize)
    print('made video', video, duration)
    kburns(
        media[: int(1 + duration // 5)],
        moviesize=moviesize,
        filename=f'{filename}_kbout.mp4',
    )
    slides = (
        VideoFileClip(f'{filename}_kbout.mp4')
        .set_duration(duration)
        .crossfadein(1)
        .crossfadeout(1)
    )
    video = CompositeVideoClip([slides, video])
    if audio:
        video = video.set_audio(AudioFileClip(audio))
    video = video.set_duration(duration).crossfadeout(1).audio_fadeout(1)
    video.write_videofile(filename, fps=30, logger=logger, threads=8)


def renderForm(form, filename='render.mp4', logger='bar'):
    v = Otto(form)
    v.render().write_videofile(filename=filename, fps=fps, logger=logger)
