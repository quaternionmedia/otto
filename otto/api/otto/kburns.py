from random import choice, randrange
from moviepy.editor import ImageClip, CompositeVideoClip

def kburns(clips, padding=1, duration=5, moviesize=(1920,1080)):
    kb = []
    t = 0
    for c in clips:
        zoom = randrange(2, 4, 1)/100 * choice([1, -1])
        print('kburns', c, zoom,)
        kb.append( CompositeVideoClip([ImageClip(c)])
                    .resize(moviesize)
                    .set_duration(duration + padding)
                    .resize(lambda t : 1+zoom*t if zoom > 0 else (1-zoom)+zoom*t)
                    .set_start(t)
                    .crossfadein(padding))
        t += kb[-1].duration - padding
    return CompositeVideoClip(kb).crossfadeout(1)
