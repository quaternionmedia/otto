import ffmpeg
import numpy as np
from subprocess import run
from os import path
from glob import glob
from json import loads, dumps
from random import choice
from moviepy.editor import TextClip, ColorClip, ImageClip, concatenate_videoclips#, CompositeVideoClip
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
def openJson(path):
    from json import loads
    with open(path, 'r') as f:
        return loads(f.read())

def textEsc(cmd):
    return cmd.replace("'", r"\\\'").replace(',', r'\,')

def resize_func(t, duration=5):
    if t < 4:
        return 1 + 0.2*t  # Zoom-in.
    elif 4 <= t <= 6:
        return 1 + 0.2*4  # Stay.
    else: # 6 < t
        return 1 + 0.2*(duration-t)  # Zoom-out.

transitions = ['left-in', 'right-in', 'center']
moviesize = (1920,1080)
def scale(n):
    return int(moviesize[0]/n), int(moviesize[1]/n)

def kburns(clips, padding=1):
    kb = [clips[0]]
    t = clips[0].duration - padding
    for c in clips[1:]:
        kb.append(c.set_start(t).crossfadein(padding))
        t += c.duration - padding
    return CompositeVideoClip(kb).crossfadeout(1)


## Assumes all media files are in a folder called data, and linked properly in the csv


def title(text,
            data=None,
            color=None,
            fontsize=None,
            size=(1920,1080),
            font='Yrsa-Bold',
            method='label',
            start=0,
            duration=5,
            position='center',
            opacity=.4,
            fps=30):
    if not color:
        color = data['COLOR']
    t = (TextClip(text,
        color=color,
        fontsize=fontsize,
        size=size,
        font=font,
        method=method)
            .set_position(position)
    )
    bkg = (ColorClip((t.w, t.h),color=(1,1,1))
            .set_position(t.pos)
            .set_opacity(opacity)
            )
    return (CompositeVideoClip([bkg, t], size=moviesize)
            .set_fps(fps)
            .set_duration(duration)
            .crossfadein(1)
            .crossfadeout(1))

def initial(text,
            data=None,
            color=None,
            fontsize=None,
            size=(1920,1080),
            font='Yrsa-Bold',
            method='caption',
            start=0,
            duration=5,
            position='center',
            opacity=.4,
            fps=30,):
    if not color:
        color = data['COLOR']
    text = text.split('.')
    texts = [TextClip(t,
                color=color,
                fontsize=fontsize,
                size=size,
                font=font,
                method=method,
                ).set_start(i*duration)
                .set_position(position) for i, t in enumerate(text) if t]
    bkgs = [ColorClip((t.w, t.h),color=(1,1,1))
                .set_position(t.pos)
                .set_opacity(opacity)
                .set_start(i*duration)
                for i, t in enumerate(texts)]
    return (CompositeVideoClip([*bkgs, *texts], size=moviesize)
            .set_position(position)
            .set_fps(30)
            .set_duration(duration)
            .crossfadein(1)
            .crossfadeout(1))

class Otto:
    def __init__(self, data: str):
        self.data = openJson(data)
        self.photos = self.data['MEDIA']

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
        slides = kburns([ImageClip(m).set_duration(5).resize(moviesize).resize(lambda t : 1+0.02*t) for m in self.photos])

        logobg = self.makeColor(moviesize,color=(0,0,0),opacity=0)
        logoimg = (ImageClip("data/steves.png")
                  .set_duration(slides.duration)
                  # .resize(height=50) # if you need to resize...
                  .margin(right=8, top=8, opacity=0) # (optional) logo-border padding
                  .set_position(("right","bottom"))
                  )
        logo = CompositeVideoClip([logobg,logoimg],size=moviesize).fx(slide_in, 1,'left')

        titles = concatenate_videoclips([
            title(text=self.data['NAME'], data=self.data, size=scale(2)),
            initial(text=self.data['INITIAL'], data=self.data, size=scale(1.5)),
            ])
        print('titles', titles)
        final_clip = CompositeVideoClip([slides, logo, titles])
        final_clip.write_videofile("ottotxt.mp4", fps=30)

if __name__ == '__main__':
    v = Otto('data.json')
    v.render()
