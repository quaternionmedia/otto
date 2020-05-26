from moviepy.editor import concatenate_videoclips, ColorClip, CompositeVideoClip, ImageClip, VideoFileClip
from moviepy.video.compositing.transitions import slide_in
from time import strftime
import kburns
import getdata as gd
from templates import *
import os

class Otto:
    def __init__(self, data=None):
        self.dir =  os.path.dirname(os.path.abspath(__file__))

        if(data is None):
            data = os.path.join(self.dir, 'examples/talavideo.json')
        self.data = gd.openJson(data)
        self.photos = [gd.download(m, location='data') for m in self.data['MEDIA']]
        self.moviesize=(1920,1080)


    def scale(self, n):
        return int(self.moviesize[0]/n), int(self.moviesize[1]/n)

    def makeColor(self,
            size, #tuple (x,y)
            color=(1,1,1), #tuple (r,g,b)
            position=(0,0), #tuple (x,y) from top left
            opacity=0.5,
            start=0,
            duration=5
            ):
            return (ColorClip(size,color=color)
                        .set_position(position)
                        .set_opacity(opacity)
                        .set_start(start)
                        .set_duration(duration)
                        .set_fps(30)
                        .crossfadein(1)
                        .crossfadeout(1)
                        )

    def render(self, size=(1920,1080)):
        # (photos + endcard) * duration = 60 seconds
        duration = 60/(len(self.photos) + 1)
        slides = kburns.kburns(self.photos, duration = duration)
        # slides = VideoFileClip('kbout.mp4')
        logodl = gd.download(self.data['LOGO'])
        logobg = self.makeColor(self.moviesize,color=(0,0,0),opacity=0)
        logoimg = (ImageClip(logodl)
                  .set_duration(slides.duration)
                  .resize(height=self.moviesize[1]//5)
                  .margin(right=8, top=8, opacity=0) # (optional) logo-border padding
                  .set_position(('right','bottom'))
                  )
        logo = CompositeVideoClip([logobg,logoimg],size=self.moviesize).fx(slide_in, 1.5,'right')

        titles = concatenate_videoclips([
            title(text=self.data['NAME'], data=self.data, size=self.scale(2), duration=duration),
            initial(text=self.data['INITIAL'], data=self.data, size=(1600, 300), position=('center', 'top')),
            bullets(text=self.data['BULLETS'], data=self.data, size=(1300, 300), position=('left', 'bottom'), align='west', fontsize=100),
            # initial(text=self.data['OPTIONAL'], data=self.data, size=scale(3), duration=duration/2),
            initial(text=self.data['CALL'], data=self.data, size=self.scale(1.5), position=('center', 'bottom')),
            ])
        ending = final(text=self.data['NAME'], data=self.data, duration=duration).set_start(slides.duration)
        final_clip = CompositeVideoClip([slides, logo, titles, ending])
        timestr = strftime('%Y%m%d-%H%M%S')
        finalout = os.path.join(self.dir, f'output/{timestr}_ottorender.mp4')
        final_clip.write_videofile(finalout, fps=30)

if __name__ == '__main__':

    v = Otto()
    v.render()