import ffmpeg
import numpy as np
from subprocess import run
from os import path
from json import loads, dumps
from random import choice
from moviepy.editor import TextClip, ColorClip, ImageClip#, CompositeVideoClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.transitions import slide_in


def download(url, location=None):
    filename = path.join(location, url.split('/')[-1]) if location else url.split('/')[-1]
    if not path.isfile(filename):
        if location:
            run(['wget', '-N', '-O', filename, url])
        else:
            run(["wget", "-N", url])
    return filename

def openCsv(path):
    import csv
    reader = csv.reader(open(path, 'r'))
    d = {}
    for row in reader:
       k, v = row
       d[k] = v
    return d

def textEsc(cmd):
    return cmd.replace("'", r"\\\'").replace(',', r'\,')

transitions = ['left-in', 'right-in', 'center']
moviesize = (1920,1080)

## Assumes all media files are in a folder called data, and linked properly in the csv
## commas escaped by '\' (single backslash)
## apostrophes escaped by '\\\' (triple backslash)

class Otto:
    def __init__(self, data: str):
        self.data = openCsv(data)
        self.photos = []
        for i in range(1,11):
            self.photos.append(download(self.data['MEDIA' + str(i)], location='data'))

    def makeText(self,
            txt,
            color=None,
            fontsize=None,
            size=(1920/2,1080/2),
            font='Yrsa-Bold',
            method='caption',
            duration=5,
            start=0,
            position='center'):
        if not color:
            color = self.data['COLOR']
        return (TextClip(txt,
            color=color,
            fontsize=fontsize,
            size=size,
            font=font,
            method=method)
                .set_fps(30)
                .set_duration(duration)
                .set_start(start)
                .set_position(position)
                .crossfadein(1)
                .crossfadeout(1)
                )

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

    def render(self):
        #TODO rename config so its not a duplicate key!

        # self.config = loads(open('example.json', 'r').read())
        # self.config['slides'] = []
        #
        # for p in self.photos:
        #     self.config['slides'].append({
        #         'file': p,
        #         'slide_duration': 5,
        #     })
        # with open('export.json', 'w') as f:
        #     f.write(dumps(self.config))
        # run(['kburns', 'kbout.mp4', '-f', 'export.json'])



        # logoout.mp4 becomes input to text generation
        slides = VideoFileClip('logoout.mp4')
        texts = [
            # text1: NAME
            self.makeText(self.data['NAME']),
            # text2: ADDRESS, PHONE, HOURS, WEBSITE
            self.makeText('\n\n'.join([
                self.data['ADDRESS'],
                self.data['PHONE'],
                self.data['HOURS'],
                self.data['WEBSITE']]), start=5),
            # text3: INITIAL (drop character)
            self.makeText(self.data['INITIAL'], start=10),
            # text4: BULLETS
            self.makeText(self.data['BULLET1'], start=15),
            self.makeText(self.data['BULLET2'], start=20),
            self.makeText(self.data['BULLET3'], start=25),
            self.makeText(self.data['BULLET4'], start=30),
            # text5: OPTIONAL
            self.makeText(self.data['OPTIONAL'], start=35),
            # text6: CALL
            self.makeText(self.data['CALL'], start=40),
            # text7: NAME, PHONE, ADDRESS, WEBSITE
            self.makeText('\n\n'.join([
                self.data['NAME'],
                self.data['PHONE'],
                self.data['ADDRESS'],
                self.data['WEBSITE']
            ]), start=45)
        ]

        colors = [self.makeColor((slides.w//10,slides.h),color=(0,0.7,0.1))]

        for txt in texts:
            colors.append(self.makeColor(txt.size, position=txt.pos, start=txt.start))

        logobg = self.makeColor(moviesize,color=(0,0,0),opacity=0)
        logoimg = (ImageClip("data/steves.png")
                  .set_duration(slides.duration)
                  # .resize(height=50) # if you need to resize...
                  .margin(right=8, top=8, opacity=0) # (optional) logo-border padding
                  .set_position(("right","bottom"))
                  )
        logo = CompositeVideoClip([logobg,logoimg],size=moviesize).fx(slide_in, 1,'left')

        final_clip = CompositeVideoClip([slides, logo, *colors, *texts], size = moviesize)
        final_clip.write_videofile("ottotxt.mp4", fps=30)

if __name__ == '__main__':
    v = Otto('data.csv')
    v.render()
