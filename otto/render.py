from moviepy.editor import concatenate_videoclips, ColorClip, ImageClip, AudioFileClip, VideoFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.transitions import slide_in
from time import strftime
from kburns import kburns
from getdata import *
from templates import *
import os
from subprocess import run
from colortransitions import *
from cliparse import args
from log import logger as ll

class Otto:
    def __init__(self, data=None, path=None):
        self.dir =  os.path.dirname(os.path.abspath(__file__))

        if (path is None) and (data is None):
            self.data = openJson(os.path.join(self.dir, 'examples', 'talavideo.json'))
        if (path is None) and (data is not None):
            self.data = data
        if (path is not None) and (data is None):
            self.data = openJson(path)
        self.name = self.data['NAME'].replace(' ', '_')
        self.media = [download(m, location='data') if m.startswith('http') else m for m in self.data['MEDIA']]
        self.moviesize=(1920,1280)
        self.duration = float(self.data.get('DURATION')) or 60.0
        self.slideduration = max(min(self.duration / len(self.data['MEDIA']), 8), 2)
        self.audio = [self.audioClip(a) for a in self.data['AUDIO']]
        self.clips = []

        if(args.verbose):
            ll.debug(self)

    def scale(self, n):
        return int(self.moviesize[0]/n), int(self.moviesize[1]/n)

    def movieclip(self, moviepath):
        return VideoFileClip(moviepath).set_duration(self.slideduration)

    def audioClip(self, audiopath):
        return AudioFileClip(audiopath)

    def render(self, size=(1920,1080), outfile='out.mp4', frame=-1):
        slides = kburns(self.media, duration=self.slideduration, moviesize=self.moviesize)
        slides = (VideoFileClip('videos/kbout.mp4')
                .crossfadein(1)
                .crossfadeout(1)
        )
        self.clips.append(title(text=self.data['NAME'],
            data=self.data,
            clipsize=self.moviesize,
            textsize=self.scale(2),
            position='center',
            duration=min(5, self.duration),
            )
        )
        if self.duration > 15:
            initsize = int(self.moviesize[0]*0.7), int(self.moviesize[1]*0.5)
            self.clips.append(initial(text=self.data['INITIAL'],
                data=self.data,
                clipsize=self.moviesize,
                textsize=initsize,
                fontsize=self.moviesize[1]//15,
                position='center',
                duration=min(5, self.duration - 15),
                fxs=[boxShrink(size=initsize,
                    duration=self.slideduration,
                    fill=rgbToDec(self.data['THEMECOLOR']),
                    transparent=True,
                    direction=0,
                    startpos=(initsize[0]//2, initsize[1]//2),
                    endpos=(initsize[0]//2, 9*initsize[1]//10),
                    startwh=initsize,
                    endwh=(int(initsize[0]*0.8), int(initsize[1]*0.1))
                ).crossfadeout(1)]
                )
            )

        if self.duration > 20:
            bulletsize = (int(self.moviesize[0]), int(self.moviesize[1]))
            self.clips.extend(bullets(text=self.data['BULLETS'],
                data=self.data,
                clipsize=self.moviesize,
                textsize=bulletsize,
                fontsize=self.moviesize[1]//13,
                duration=self.duration - 20,
                fxs=[boxShrink(
                    size=(int(bulletsize[0]), bulletsize[1]),
                    duration=self.slideduration,
                    fill=rgbToDec(self.data['THEMECOLOR']),
                    transparent=True,
                    direction=0,
                    startpos=(bulletsize[0]//2, bulletsize[1]//2),
                    endpos=(bulletsize[0]//10, bulletsize[1]//2),
                    startwh=(bulletsize),
                    endwh=(int(bulletsize[0]*0.1), int(bulletsize[1]*0.8))
                ).crossfadeout(1)]
                )
            )
        if self.duration > 10:
            self.clips.append(initial(text=self.data['CALL'],
                data=self.data,
                clipsize=self.moviesize,
                textsize=(int(self.moviesize[0]*0.7), int(self.moviesize[1]*0.5)),
                fontsize=self.moviesize[1]//13,
                position='center',
                duration=min(5, self.duration - 10),)
            )
        if self.duration > 5:
            self.clips.append(final(text=self.data['NAME'],
                data=self.data,
                duration=min(5, self.duration - 5),
                clipsize=self.moviesize,
                fontsize=self.moviesize[1]//10,)
            )
        t = 0
        print('clips:')
        print(self.clips)
        for c in self.clips:
            print(c)
            c.set_start(t)
            t += c.duration

        allclips = e.concatenate_videoclips(self.clips)
        logodl = download(self.data['LOGO'])
        logobg = makeColor(self.moviesize,color=(0,0,0),opacity=0)
        logoimg = (e.ImageClip(logodl)
                .set_duration(self.duration)
                .resize(height=self.moviesize[1]//5)
                .margin(right=8, top=8, opacity=0)
                .set_position(('right','bottom'))
        )
        logo = CompositeVideoClip([logobg,logoimg],
            size=self.moviesize).fx(slide_in, 1.5,'right')
        finalVideo = (CompositeVideoClip([slides, allclips, logo])
                    .set_audio(self.audio[0])
                    .set_duration(self.duration)
        )
        timestr = strftime('%Y%m%d-%H%M%S')
        filename = os.path.join(self.dir, 'output', f'{timestr}_{self.name}_{int(self.duration)}_{self.moviesize[0]}x{self.moviesize[1]}.mp4')
        if(args.frame>=0):
            finalVideo.save_frame(f'{fileout}.png', t=args.frame)

        if(args.render):
            finalVideo.write_videofile(filename, fps=30, threads=8,)


if __name__ == '__main__':
    timestr = strftime('%Y%m%d-%H%M%S')
    fileout = f'output/{timestr}_ottorender'

    ll.info("otto started")
    v = Otto()

    if(args.verbose):
        ll.info("verbosly starting")

    if(args.frame>=0):
        ll.info(f"rendering frame:{args.frame}")
        v.render(outfile=fileout, frame=args.frame)
        ll.info("render frame complete")

    if(args.render):
        ll.info("render starting")
        v.render(outfile=fileout)
        ll.info("render complete")

    if(args.open):
        ll.info("opening")
        run(['vlc', fileout])
        ll.info("opened")
