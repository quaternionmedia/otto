from subprocess import run
from json import loads, dumps
from moviepy.editor import CompositeVideoClip, ImageClip, VideoFileClip
from sys import path
from os.path import join
from otto.getdata import download
from random import choice, randrange
from threading import Thread

def kburns(media, duration=5, moviesize=(1920,1080)):
        config = loads(open(join('examples', 'example.json'), 'r').read())
        config['config']['output_width'] = moviesize[0]
        config['config']['output_height'] = moviesize[1]
        slides = []
        for m in media:
            if m.endswith('.mp4'):
                slides.append({
                        'file': media[0],
                        'force_no_audio': True,
                        'start': 0,
                        'end': duration*2,
                    })
            elif m.endswith(('.jpg', '.jpeg', '.png')):
                slides.append({
                    'file': m,
                    'slide_duration': duration + 1,
                })
        config['slides'] = slides
        with open(join('examples', 'export.json'), 'w') as f:
            f.write(dumps(config))
        run(['kburns', join('videos', 'kbout.mp4'), '-f', join('examples', 'export.json')])


def write(c,path):
    c.write_videofile(path,fps=30,threads=8)
    c.close()

def kburns2(clips, padding=1, duration=5, moviesize=(800,600)):
    kbpaths = []
    kbclips = []

    threads = []

    for j,c in enumerate(clips):
        dirs = ((randrange(-7,7,1),randrange(-7,7,1)))
        zoom = randrange(2, 4, 1)/100 * choice([1, -1])
        clip = (CompositeVideoClip([(ImageClip(c)
                                        .set_duration(duration+padding)
                                        .set_position(lambda t: (t*dirs[0],t*dirs[1]))
                                        .resize(lambda t : 1+zoom*t if zoom > 0 else (1-zoom)+zoom*t)
                                        )]))
        clippath = f'output/{j}.mp4'
        kbpaths.append(clippath)

        thread = Thread(target=write, args=(clip,clippath))
        thread.start()
        threads.append(thread)

    for k,p in enumerate(kbpaths):
        threads[k].join()
        kbclips.append((VideoFileClip(p)
                        .set_start(k*duration)
                        .crossfadein(padding)
                        .crossfadeout(padding)
                        ))

    return CompositeVideoClip(kbclips).crossfadeout(1)


if __name__ == '__main__':
    config = loads(open('examples/talavideo.json', 'r').read())
    photos = [download(p) for p in config['MEDIA'][1:4]]
    print('running kburns with', photos)
    kb = kburns2(photos, duration=10/(len(photos) + 1))
    kb.write_videofile('output/kbtest.mp4', fps=30, threads=8,)
