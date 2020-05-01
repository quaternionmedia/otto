import ffmpeg
import numpy as np
from subprocess import run
from typing import List
from seed import photoSeed
from os import path

def download(url):
    filename = url.split('/')[-1]
    if not path.isfile(filename):
        run(["wget", "-N", url])
    return filename

class Otto:
    def __init__(self,
                photos:List=photoSeed,
                logo=None,
                music=None,
                address=None,
                price=None,
                bedrooms=None,
                bathrooms=None,
                sqft=None):
        self.photos = photos
        self.logo = logo
        self.music = music
        self.address = address
        self.price = price
        self.bedrooms = bedrooms
        self.bathrooms = bathrooms
        self.sqft = sqft

    # def getPhoto(self, photo):
    #     return download(photo)

    def getMusic(self, song=None):
        download(song)

    def render(self):
        p = []
        for i in self.photos:
            p.append(
                ffmpeg.input(
                    download(i),
                    loop=1,
                    framerate=30)
                .zoompan(s='hd1080')
                .filter('setsar', sar=1)
                .trim(start_frame=0, end_frame=30))
        c = ffmpeg.concat(*p)
        print('rendering', c)
        out = ffmpeg.output(c, 'out.mp4')
        out.run()

if __name__ == '__main__':
    v = Otto()
    v.render()

# get template from xml or csv

# get photos from links from xml (max 20)

# get logo and display watermarked/ghosted to entire video

# get music

# add text at 5 seconds with address, city, price

# add text from 10 seconds, each entry for 5 seconds
    # number of bedrooms
    # number of bathrooms
    # square footage

# rotate photos for 60/(number of photos) seconds each

# add text at 50 seconds with address, city price

# add text at 55 seconds with name, phone number, email, website
