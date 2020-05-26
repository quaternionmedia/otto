import moviepy.editor as e
import moviepy.video.compositing.transitions as mvct
import colortransitions as ct
import time as t
import kburns
import getdata as gd
import templates as ts
import os
from subprocess import run

class Otto:
    def __init__(self, data=None):
        self.dir =  os.path.dirname(os.path.abspath(__file__))
        self.moviesize=(1920,1080)
        self.totalduration = 0
        self.slideduration = 5
        if(data is None):
            data = os.path.join(self.dir, 'examples/talavideo.json')
        self.data = gd.openJson(data)
        self.photos = [gd.download(m, location='data') for m in self.data['MEDIA']]
        self.videos = [self.movieclip(m) for m in self.data['VIDEOS']]
        self.audios = [self.audioClip(a) for a in self.data['AUDIOS']]

        self.clips = []

    def scale(self, n):
        return int(self.moviesize[0]/n), int(self.moviesize[1]/n)

    def movieclip(self, moviepath):
        return e.VideoFileClip(moviepath).set_duration(self.slideduration)

    def audioClip(self, audiopath):
        return e.AudioFileClip(audiopath)

    def render(self, size=(1920,1080), outfile='out.mp4'):

        slides = kburns.kburns(self.photos)
        # slides = VideoFileClip('kbout.mp4')


        # titles = concatenate_videoclips([
        #     title(text=self.data['NAME'], data=self.data, size=self.scale(2), duration=duration),
        #     initial(text=self.data['INITIAL'], data=self.data, size=(1600, 300), position=('center', 'top')),
        #     bullets(text=self.data['BULLETS'], data=self.data, size=(1300, 300), position=('left', 'bottom'), align='west', fontsize=100),
        #     # initial(text=self.data['OPTIONAL'], data=self.data, size=scale(3), duration=duration/2),
        #     initial(text=self.data['CALL'], data=self.data, size=self.scale(1.5), position=('center', 'bottom')),
        #     ])
        # ending = final(text=self.data['NAME'], data=self.data, duration=duration).set_start(slides.duration)
        # final_clip = CompositeVideoClip([slides, logo, titles, ending])
        # timestr = strftime('%Y%m%d-%H%M%S')
        # finalout = os.path.join(self.dir, f'output/{timestr}_ottorender.mp4')
        # final_clip.write_videofile(finalout, fps=30)

        self.clips.append(ts.title(text=self.data['NAME'],
            data=self.data,
            duration=self.slideduration,
            position='center',
            bg=self.videos[0]))

        self.clips.append(ts.initial(text=self.data['INITIAL'],
            data=self.data,
            clipsize=self.moviesize,
            textsize=(int(self.moviesize[0]*0.7), int(self.moviesize[1]*0.5)),
            fontsize=self.moviesize[1]//13,
            position='center'))

        self.clips.extend(ts.bullets(text=self.data['BULLETS'],
            data=self.data,
            clipsize=self.moviesize,
            textsize=(int(self.moviesize[0]*0.7), int(self.moviesize[1]*0.5)),
            duration=self.slideduration,
            position=('left', 'bottom'),
            fontsize=self.moviesize[1]//13))

        self.clips.append(ts.initial(text=self.data['CALL'],
            data=self.data,
            clipsize=self.moviesize,
            textsize=(int(self.moviesize[0]*0.7), int(self.moviesize[1]*0.5)),
            fontsize=self.moviesize[1]//13,
            position='center'))

        self.clips.append(ts.final(text=self.data['NAME'],
            data=self.data))

        for i, c in enumerate(self.clips):
            c.set_start(i*self.slideduration)

        self.totalduration = len(self.clips)* self.slideduration

        allclips = e.concatenate_videoclips(self.clips)

        logodl = gd.download(self.data['LOGO'])
        logobg = ct.makeColor(self.moviesize,color=(0,0,0),opacity=0)
        logoimg = (e.ImageClip(logodl)
                  .set_duration(self.totalduration)
                  .resize(height=self.moviesize[1]//5) # if you need to resize...
                  .margin(right=8, top=8, opacity=0) # (optional) logo-border padding
                  .set_position(('right','bottom'))
                  )
        logo = e.CompositeVideoClip([logobg,logoimg],
                    size=self.moviesize).fx(mvct.slide_in, 1.5,'right')

        final_clip = e.CompositeVideoClip([slides, allclips, logo])
        final_clip_audio = final_clip.set_audio(self.audios[0].set_duration(self.totalduration))
        finalout = os.path.join(self.dir, outfile)
        final_clip_audio.write_videofile(finalout, fps=30)

if __name__ == '__main__':
    timestr = t.strftime('%Y%m%d-%H%M%S')
    fileout = f'output/{timestr}_ottorender.mp4'
    v = Otto()
    v.render(outfile=fileout)
    run(['vlc', fileout])
