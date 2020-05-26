from subprocess import run
from json import loads, dumps
from getdata import download
import moviepy.editor as e

def kburns(photos, duration=5):
        config = loads(open('examples/example.json', 'r').read())
        config['slides'] = []

        for p in photos:
            config['slides'].append({
                'file': p,
                'slide_duration': duration + 1,
            })
        with open('examples/export.json', 'w') as f:
            f.write(dumps(config))
        run(['kburns', 'kbout.mp4', '-f', 'examples/export.json'])



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
    photos = loads(open('examples/talavideo.json', 'r').read())['MEDIA']
    photos = [download(p) for p in photos]
    kburns(photos)
