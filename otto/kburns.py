from subprocess import run
from json import loads, dumps
from getdata import download
import moviepy.editor as e
from sys import path
from os.path import join

def kburns(media, duration=5):
        config = loads(open('examples/example.json', 'r').read())
        slides = [

        ]
        for m in media:
            if m.endswith('.mp4'):
                slides.append({
                        'file': media[0],
                        'force_no_audio': True,
                        'start': 0,
                        'end': duration*2,
                    })
            else:
                slides.append({
                    'file': m,
                    'slide_duration': duration + 1,
                })
        config['slides'] = slides
        with open('examples/export.json', 'w') as f:
            f.write(dumps(config))
        run(['kburns', join('videos', 'kbout.mp4'), '-f', join('examples', 'export.json')])



from random import choice, randrange
import moviepy.editor as e

# FIXME - all zooms use the final random settings
def kburns2(clips, padding=1, duration=5, moviesize=(1920,1080)):
    kb = []
    t = 0
    for c in clips:
        # zoom = randrange(2, 4, 1)/100 * choice([1, -1])
        # print('kburns', c, zoom,)
        kb.append( e.CompositeVideoClip([e.ImageClip(c)])
                    # .resize(moviesize)
                    .set_duration(duration + padding)
                    # .resize(lambda t : 1+zoom*t if zoom > 0 else (1-zoom)+zoom*t)
                    .set_start(t)
                    .crossfadein(padding))
        t += kb[-1].duration - padding
    for k in kb:
        zoom = randrange(2, 4, 1)/100 * choice([1, -1])
        k.resize(lambda t : 1+zoom*t if zoom > 0 else (1-zoom)+zoom*t)
    return e.CompositeVideoClip(kb).crossfadeout(1)

if __name__ == '__main__':
    config = loads(open('examples/talavideo.json', 'r').read())
    photos = config['VIDEOS']
    photos += [download(p) for p in config['MEDIA']]
    print('running kburns with', photos)
    kburns(photos, duration=60/(len(photos) + 1))
