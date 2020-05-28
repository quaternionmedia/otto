from moviepy.editor import concatenate_videoclips, ColorClip, ImageClip, VideoFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.transitions import slide_in
from time import strftime
from kburns import kburns
import getdata as gd
from templates import *
import os

class Otto:
    def __init__(self, data=None):
        self.dir =  os.path.dirname(os.path.abspath(__file__))
        self.data = gd.openJson(data or os.path.join(self.dir, 'examples', 'talavideo.json'))
        
        self.name = self.data['NAME'].replace(' ', '_')
        self.photos = [gd.download(m, location='data') for m in self.data['MEDIA']]
        self.moviesize=(1920,1080)
        self.duration = self.data.get('DURATION') or 60
        self.slideduration = self.duration / len(self.data['MEDIA'])
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
        slides = kburns(self.photos, duration=self.slideduration)
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
            # bg=self.videos[0],
            )
        )
        if self.duration > 15:
            self.clips.append(initial(text=self.data['INITIAL'],
                data=self.data,
                clipsize=self.moviesize,
                textsize=(int(self.moviesize[0]*0.7), int(self.moviesize[1]*0.5)),
                fontsize=self.moviesize[1]//13,
                position='center',
                duration=min(5, self.duration - 15),)
            )
                
        if self.duration > 20:
            self.clips.extend(bullets(text=self.data['BULLETS'],
                data=self.data,
                clipsize=self.moviesize,
                textsize=(int(self.moviesize[0]*0.7), int(self.moviesize[1]*0.5)),
                fontsize=self.moviesize[1]//13,
                duration=min(5, self.duration - 20),)
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
                duration=min(5, self.duration - 5),)
            )
        t = 0
        print('clips:')
        print(self.clips)
        for c in self.clips:
            print(c)
            c.set_start(t)
            t += c.duration

        allclips = e.concatenate_videoclips(self.clips)
        logodl = gd.download(self.data['LOGO'])
        logobg = ct.makeColor(self.moviesize,color=(0,0,0),opacity=0)
        logoimg = (e.ImageClip(logodl)
                .set_duration(self.duration)
                .resize(height=self.moviesize[1]//5)
                .margin(right=8, top=8, opacity=0)
                .set_position(('right','bottom'))
        )
        logo = e.CompositeVideoClip([logobg,logoimg],
            size=self.moviesize).fx(slide_in, 1.5,'right')
        finalVideo = (e.CompositeVideoClip([slides, allclips, logo])
                    .set_audio(self.audios[0])
                    .set_duration(self.duration)
        )
        timestr = strftime('%Y%m%d-%H%M%S')
        filename = os.path.join(self.dir, 'output', f'{timestr}_{self.name}.mp4')

        finalVideo.write_videofile(filename, fps=30)

if __name__ == '__main__':

    v = Otto()
    v.render()
