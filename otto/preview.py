from os.path import join

from fastapi import APIRouter

from otto.getdata import timestr
from otto.models import Edl, Render
from otto.render import renderFrame

previewAPI = APIRouter()


@previewAPI.post('/')
async def previewFrame(t: float, render: Render):
    """# Preview frame
    Generates a frame of a given `edl` at time `t`, with `width` and `height`.

    Returns the name of a file on this server when available, or a relevant error
    """
    print('previewing', render.edl, 'at frame', t)
    active_clips = [
        c for c in render.edl.clips if t >= (c.start or 0) + (c.offset or 0)
    ]
    print('generating active clips', active_clips, t)
    frame_name = join('data', timestr() + '.jpg')
    print(f'saving frame {t} as: {frame_name}')
    return renderFrame(
        Edl(clips=active_clips), t, frame_name, moviesize=(render.width, render.height)
    )
