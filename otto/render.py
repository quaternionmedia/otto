from moviepy.editor import concatenate_videoclips, ColorClip, ImageClip, AudioFileClip, VideoFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.transitions import slide_in
from time import strftime
from kburns import kburns2 as kburns
from getdata import *
from templates import *
import os
from subprocess import run
from colortransitions import *
from cliparse import options, args
from log import logger as ll

class Otto:
    def __init__(self, data=None):
        self.dir =  os.path.dirname(os.path.abspath(__file__))

        if(data is None):
            data = os.path.join(self.dir, 'examples/talavideo.json')
        self.data = openJson(data)
        self.name = self.data['NAME'].replace(' ', '_')
        self.photos = [download(m, location='data') for m in self.data['MEDIA']]
        self.moviesize=(1920,1080)
        self.totalduration = 0
        self.slideduration = 5
        self.videos = [self.movieclip(m) for m in self.data['VIDEOS']]
        self.audios = [self.audioClip(a) for a in self.data['AUDIOS']]
        self.clips = []

        if(options.verbose):
            ll.debug(self)

    def scale(self, n):
        return int(self.moviesize[0]/n), int(self.moviesize[1]/n)

    def movieclip(self, moviepath):
        return VideoFileClip(moviepath).set_duration(self.slideduration)

    def audioClip(self, audiopath):
        return AudioFileClip(audiopath)

    def render(self, size=(1920,1080), outfile='out.mp4', frame=-1):

        # slides = kburns(self.photos)
        slides = (VideoFileClip('videos/kbout.mp4')
                .crossfadein(1)
                .crossfadeout(1)
        )

        self.clips.append(title(text=self.data['NAME'],
            data=self.data,
            clipsize=self.moviesize,
            textsize=self.scale(2),
            duration=self.slideduration,
            position='center',
            # bg=self.videos[0],
            )
        )

        initsize = int(self.moviesize[0]*0.7), int(self.moviesize[1]*0.5)
        self.clips.append(initial(text=self.data['INITIAL'],
            data=self.data,
            clipsize=self.moviesize,
            textsize=initsize,
            fontsize=self.moviesize[1]//15,
            position='center',
            fxs=[boxShrink(size=initsize,
                    duration=self.slideduration,
                    fill=getcolor(self.data['THEMECOLOR'], 'RGB'),
                    transparent=True,
                    direction=0,
                    startpos=(initsize[0]//2, initsize[1]//2),
                    endpos=(initsize[0]//2, 9*initsize[1]//10),
                    startwh=initsize,
                    endwh=(int(initsize[0]*0.8), int(initsize[1]*0.1))
                    ).crossfadeout(1)]))

        bulletsize = (int(self.moviesize[0]), int(self.moviesize[1]))
        self.clips.extend(bullets(text=self.data['BULLETS'],
            data=self.data,
            clipsize=self.moviesize,
            textsize=bulletsize,
            duration=self.slideduration,
            fontsize=self.moviesize[1]//13,
            fxs=[boxShrink(size=(int(bulletsize[0]), bulletsize[1]),
                    duration=self.slideduration,
                    fill=getcolor(self.data['THEMECOLOR'], 'RGB'),
                    transparent=True,
                    direction=0,
                    startpos=(bulletsize[0]//2, bulletsize[1]//2),
                    endpos=(bulletsize[0]//10, bulletsize[1]//2),
                    startwh=(bulletsize),
                    endwh=(int(bulletsize[0]*0.1), int(bulletsize[1]*0.8))
                    ).crossfadeout(1)]))

        self.clips.append(initial(text=self.data['CALL'],
            data=self.data,
            clipsize=self.moviesize,
            textsize=(int(self.moviesize[0]*0.7), int(self.moviesize[1]*0.5)),
            fontsize=self.moviesize[1]//13,
            position='center'))

        self.clips.append(final(text=self.data['NAME'],
            data=self.data))

        for i, c in enumerate(self.clips):
            c.set_start(i*self.slideduration)

        self.totalduration = len(self.clips)* self.slideduration
        allclips = concatenate_videoclips(self.clips)
        logodl = download(self.data['LOGO'])
        logobg = makeColor(self.moviesize,color=(0,0,0),opacity=0)
        logoimg = (ImageClip(logodl)
                .set_duration(self.totalduration)
                .resize(height=self.moviesize[1]//5)
                .margin(right=8, top=8, opacity=0)
                .set_position(('right','bottom'))
        )
        logo = CompositeVideoClip([logobg,logoimg],
            size=self.moviesize).fx(slide_in, 1.5,'right')
        # ending = final(text=self.data['NAME'], data=self.data, duration=self.slideduration).set_start(self.totalduration - self.slideduration)
        finalVideo = (CompositeVideoClip([allclips])
                    .set_audio(self.audios[0])
                    .set_duration(self.totalduration)
        )
        # timestr = strftime('%Y%m%d-%H%M%S')
        # filename = os.path.join(self.dir, 'output', f'{timestr}_{self.name}.mp4')
        if(options.frame>=0):
            finalVideo.save_frame(f'output/{fileout}_frame{options.frame}.png', t=options.frame)

        if(options.render):
            finalVideo.write_videofile(fileout, fps=30, threads=16)

if __name__ == '__main__':
    timestr = strftime('%Y%m%d-%H%M%S')
    fileout = f'output/{timestr}_ottorender.mp4'

    ll.info("otto started")
    v = Otto()

    if(options.verbose):
        ll.info("verbosly starting")

    if(options.frame>=0):
        ll.info(f"rendering frame :{options.frame})")
        v.render(outfile=fileout, frame=options.frame)
        ll.info("render frame complete")

    if(options.render):
        ll.info("render starting")
        v.render(outfile=fileout)
        ll.info("render complete")

    if(options.open):
        ll.info("opening")
        run(['vlc', fileout])
        ll.info("opened")
