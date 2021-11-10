from subprocess import run
from json import loads, dumps
from moviepy.editor import CompositeVideoClip, ImageClip, VideoFileClip
from sys import path
from os.path import join
from otto.getdata import download
from otto.defaults import kburns_config
from random import choice, randrange
from threading import Thread, _shutdown

def kburns(media, duration=5, moviesize=(1920,1080), filename='kbout.mp4'):
        config = kburns_config
        config['config']['output_width'] = moviesize[0]
        config['config']['output_height'] = moviesize[1]
        slides = []
        for m in media:
            if m.endswith('mp4'):
                slides.append({
                        'file': m,
                        'force_no_audio': True,
                        'start': 0,
                        'end': duration + 1,
                    })
            else:
                slides.append({
                    'file': m,
                    'slide_duration': duration + 1,
                })
        config['slides'] = slides
        config_path = join('output', 'kb_config.json')
        with open(config_path, 'w') as f:
            f.write(dumps(config))
        run(['kburns', filename, '-f', config_path])


def write(c,path,duration,padding,direction,zoom):

    # print(dirs, zoom)
    clip = (CompositeVideoClip([(ImageClip(c)
                                    .set_duration(duration+padding)
                                    .set_position(lambda t: (int(t*direction[0]),int(t*direction[1])))
                                    .resize(lambda t : 1+zoom*t if zoom > 0 else (1-zoom)+zoom*t)
                                    )]))
    clip.write_videofile(path,fps=30,threads=8)
    clip.close()

def kburns2(clips, padding=1, duration=5, moviesize=(800,600)):
    kbpaths = []
    kbclips = []

    threads = []

    for j,c in enumerate(clips):
        clippath = join('videos/', f'{j}.mp4')
        kbpaths.append(clippath)
        # write(clip,clippath)
        dirs = ((randrange(-7,7,1),randrange(-7,7,1)))
        zoom = randrange(2, 4, 1)/100 * choice([1, -1])
        thread = Thread(target=write, args=(c,clippath,duration,padding,dirs,zoom,))
        thread.start()
        threads.append(thread)

    _shutdown()

    for k,p in enumerate(kbpaths):
        kbclips.append((VideoFileClip(p)
                        .resize(moviesize)
                        .set_start(k*duration)
                        .crossfadein(padding)
                        .crossfadeout(padding)
                        ))

    return CompositeVideoClip(kbclips).crossfadeout(1)


if __name__ == '__main__':
    config = loads(open('examples/talavideo.json', 'r').read())
    photos = [download(p) for p in config['media'][1:5]]
    print('running kburns with', photos)
    kb = kburns2(photos, duration=10/(len(photos) + 1))
    kb.write_videofile('output/kbtest.mp4', fps=30, threads=8,)
