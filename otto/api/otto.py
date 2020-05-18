import ffmpeg
import numpy as np
from subprocess import run
from os import path
from glob import glob
from json import loads, dumps
from random import choice, randrange
from moviepy.editor import TextClip, ColorClip, ImageClip, VideoClip, concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.transitions import slide_in
from colortransitions import growBox, boxReveal, flyInAndGrow
import time
from PIL.ImageColor import getcolor

def download(url, location='data'):
    if url.find('.jpg'):
        basename = run(['basename', url.split('.jpg')[0] + '.jpg'], capture_output=True).stdout.decode()
    elif url.find('.png'):
        basename = run(['basename', url.split('.png')[0] + '.png'], capture_output=True).stdout.decode()
    else:
        basename = run(['basename', url.split('/')[-1]])
    filename = path.join(location, basename) if location else basename
    if not path.isfile(filename):
        if location:
            run(['wget', '--content-disposition', '-N', '-O', filename, url])
        else:
            run(['wget', '--content-disposition',  '-N', url])
    return filename

def openCsv(path):
    import csv
    reader = csv.reader(open(path, 'r'))
    d = {}
    for row in reader:
       k, v = row
       d[k] = v
    return d

def openJson(path):
    with open(path, 'r') as f:
        return loads(f.read())

transitions = ['left-in', 'right-in', 'center']
moviesize = (1920,1080)
def scale(n):
    return int(moviesize[0]/n), int(moviesize[1]/n)

def kburns(clips, padding=1, duration=5):
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

## Assumes all media files are in a folder called data, and linked properly in the csv


def title(text,
            data=None,
            color=None,
            fontsize=None,
            size=(1920,1080),
            font='Segoe UI Black',
            method='caption',
            duration=5,
            position='center',
            opacity=.4,
            fps=30):
    if not color:
        color = data['FONTCOLOR']
    t = (TextClip(text.rstrip().lstrip(),
        color=color,
        fontsize=fontsize,
        size=size,
        font=font,
        method=method,
        stroke_color=None)
            .set_position(position)
    )
    boxclip = boxReveal(duration=duration, size=size, fill=getcolor(data['THEMECOLOR'], 'RGB')).set_position(position)

    return (CompositeVideoClip([t, boxclip], size=moviesize)
            .set_position('center')
            .set_fps(fps)
            .set_duration(duration)
            # .resize(lambda t: min(t+.01, 1))
            .crossfadein(1)
            .crossfadeout(1)
            )

def initial(text,
            data=None,
            color=None,
            fontsize=None,
            size=(1920,1080),
            font='Segoe UI Black',
            method='caption',
            start=0,
            duration=5,
            position='center',
            opacity=.4,
            fps=30,
            ):
    if not color:
        color = data['FONTCOLOR']
    text = text.split('.')
    text = [t.lstrip().rstrip() for t in text if t.lstrip().rstrip()]
    texts = [TextClip(t.rstrip().lstrip(),
                color=color,
                fontsize=fontsize,
                size=size,
                font=font,
                method=method,
                stroke_color=None,
                align='west'
                ).set_start(i*duration)
                .set_duration(duration or 2 + pow(len(t.rstrip().lstrip().split(' ')), .5))
                .set_position(position)
                .crossfadein(1)
                .crossfadeout(1) for i, t in enumerate(text) if t.rstrip().lstrip()]

    bkgs = [ColorClip((t.w, t.h),color=getcolor(data['THEMECOLOR'], 'RGB'))
                .set_duration(t.duration)
                .set_start(t.start)
                .set_position(t.pos)
                .set_opacity(opacity)
                .crossfadein(1)
                .crossfadeout(1)
                for i, t in enumerate(texts)]
    return (CompositeVideoClip([*bkgs, *texts], size=moviesize)
            .set_position(position)
            .set_fps(30))


def bullets(text,
            data=None,
            color=None,
            fontsize=None,
            size=(1920,1080),
            font='Segoe UI Black',
            method='caption',
            start=0,
            duration=5,
            position='center',
            opacity=.4,
            fps=30,
            align='west'):
    if not color:
        color = data['FONTCOLOR']
    text = text.split('\u2022')
    text = [t.lstrip().rstrip() for t in text if t.lstrip().rstrip()]
    print('bullet texts', text)
    texts = [TextClip(t,
                color=color,
                fontsize=fontsize,
                size=size,
                font=font,
                method=method,
                stroke_color=None,
                align='west'
                ).set_start(i*duration)
                .set_duration(duration)
                .set_position(position)
                .crossfadein(1)
                .crossfadeout(1) for i, t in enumerate(text) if t.rstrip().lstrip()]

    bkgs = [ColorClip((t.w, t.h),color=getcolor(data['THEMECOLOR'], 'RGB'))
                .set_duration(t.duration)
                .set_start(t.start)
                .set_position(t.pos)
                .set_opacity(opacity)
                .crossfadein(1)
                .crossfadeout(1)
                for i, t in enumerate(texts)]
    return (CompositeVideoClip([*bkgs, *texts], size=moviesize)
            .set_position(position)
            .set_fps(30))

def final(text,
            data=None,
            color=None,
            fontsize=None,
            size=(1920,1080),
            font='Segoe UI Black',
            method='caption',
            start=0,
            duration=5,
            position='center',
            opacity=.4,
            fps=30,):
    if not color:
        color = data['FONTCOLOR']
    texts = [
        TextClip(text, color=color,
            fontsize=fontsize,
            size=scale(1.5),
            font=font,
            method='label',
            stroke_color=None,
            align='north').set_position(('center', 'top')),
        TextClip(data['ADDRESS'], color=color,
            fontsize=fontsize,
            size=scale(3),
            font=font,
            method=method,
            stroke_color=None,
            align='west').set_position(('left', 'center')),
        TextClip(data['WEBSITE'], color=color,
            fontsize=fontsize,
            size=scale(1.5),
            font=font,
            method=method,
            stroke_color=None,
            align='south').set_position(('center', 'bottom')),
        TextClip(data['PHONE'], color=color,
            fontsize=fontsize,
            size=scale(3),
            font=font,
            method=method,
            stroke_color=None,
            align='east').set_position(('right', 'center')),
    ]

    fiag = flyInAndGrow(size=moviesize, duration=duration, fill=getcolor(data['THEMECOLOR'], 'RGB'), transparent=True)#, size=scale(2))
    box = VideoClip(fiag)
    boxmask = VideoClip(lambda t: fiag(t)[:,:,3]/255.0, ismask=True, duration=duration)
    boxclip = VideoClip(lambda t: fiag(t)[:,:,:3], duration=duration, ).set_mask(boxmask).set_position(position)


    return (CompositeVideoClip([boxclip, *texts], size=size)
            .set_fps(fps)
            .set_duration(duration)
            .crossfadein(1)
            .crossfadeout(1))


class Otto:
    def __init__(self, data: str):
        self.data = openJson(data)
        self.photos = [download(m, location='data') for m in self.data['MEDIA']]

    def makeText(self,
            txt,
            color=None,
            fontsize=None,
            size=(1920/2,1080/2),
            font='Segoe UI Black',
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
        # (photos + endcard) * duration = 60 seconds
        duration = 60/(len(self.photos) + 1)
        slides = kburns(self.photos, duration = duration)
        # slides = VideoFileClip('kbout.mp4')
        logodl = download(self.data['LOGO'])
        logobg = self.makeColor(moviesize,color=(0,0,0),opacity=0)
        logoimg = (ImageClip(logodl)
                  .set_duration(slides.duration)
                  .resize(height=moviesize[1]//5) # if you need to resize...
                  .margin(right=8, top=8, opacity=0) # (optional) logo-border padding
                  .set_position(('right','bottom'))
                  )
        logo = CompositeVideoClip([logobg,logoimg],size=moviesize).fx(slide_in, 1,'right')

        titles = concatenate_videoclips([
            title(text=self.data['NAME'], data=self.data, size=scale(2), duration=duration),
            initial(text=self.data['INITIAL'], data=self.data, size=(1600, 300), duration=duration/1.5, position='top'),
            bullets(text=self.data['BULLETS'], data=self.data, size=(1300, 300), duration=duration/2, position=('left', 'bottom'), align='west', fontsize=100),
            # initial(text=self.data['OPTIONAL'], data=self.data, size=scale(3), duration=duration/2),
            initial(text=self.data['CALL'], data=self.data, size=scale(2), duration=duration/1.5),
            ])
        ending = final(text=self.data['NAME'], data=self.data, duration=duration).set_start(slides.duration)
        final_clip = CompositeVideoClip([slides, logo, titles, ending])
        timestr = time.strftime('%Y%m%d-%H%M%S')
        final_clip.write_videofile(f'{timestr}_ottorender.mp4', fps=30)

if __name__ == '__main__':
    v = Otto('talavideo.json')
    v.render()
