# import render
import os, json
from fastapi import APIRouter, Request, HTTPException
from otto.getdata import timestr
from otto.models import Edl
from otto.render import generateEdl
from otto import templates

app = APIRouter()


@app.get('/templates')
async def getTemplates():
    """# Get templates
    Returns a list of template names currently loaded and available."""
    return [t for t in dir(templates) if t.islower() and t[0] is not '_']

@app.post('/preview')
async def previewFrame(t: float, edl: Edl, width: int = 1920, height: int = 1080):
    """# Preview frame
    Generates a frame of a given `edl` at time `t`, with `width` and `height`.
    
     Returns the name of a file on this server when available, or a relevant error message"""
    print('previewing', edl, 'at frame', t)
    try:
        active_clips = [c for c in edl.clips if t >= (c.start or 0) + (c.offset or 0)]
        print('generating active clips', active_clips)
        video = generateEdl(Edl(clips=active_clips), moviesize=(width, height))
        frame_name = os.path.join('data', timestr() + '.png')
        video.save_frame(frame_name, t=t, withmask=True)
        return frame_name
    except Exception as e:
        print('error previewing frame', e)
        raise HTTPException(status_code=500, detail='error previewing frame')

if __name__ == '__main__':
    from uvicorn import run
    run(app, host='0.0.0.0', port=9000)
