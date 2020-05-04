import ffmpeg
import numpy as np
from subprocess import run
from typing import List
from os import path
from json import loads, dumps

def download(url):
    filename = url.split('/')[-1]
    if not path.isfile(filename):
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

class Otto:
    def __init__(self, data: str):
        self.data = openCsv(data)
        self.photos = []
        for i in range(1, 17):
            p = self.data[ 'photo' + str(i) ]
            if p:
                self.photos.append(p)
        assert len(self.photos), '# WARNING: no photos found'
        # self.logo = logo
        # self.music = music
        self.address = self.data['addrdisplay']
        self.city = self.data['addrcity']
        self.state = self.data['addrstate']
        self.zip = self.data['addrzip']
        self.price = int(self.data['price']) or f"{self.data['price_range_min']} - {self.data['price_range_max']}"
        self.bedrooms = int(self.data['bedrooms_normalized_count']) or f"{self.data['bedrooms_normalized_count_range_min']}-{self.data['bedrooms_normalized_count_range_max']}"
        self.bathrooms = int(self.data['bathrooms_normalized_count']) or f"{self.data['bathrooms_normalized_count_range_max']}"
        self.sqft = int(self.data['size_square_footage']) or f"{self.data['size_square_footage_range_min']}-{self.data['size_square_footage_range_max']}"

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
