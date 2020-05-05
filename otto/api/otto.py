import ffmpeg
import numpy as np
from subprocess import run
from typing import List
from os import path
from json import loads, dumps
from random import choice
from PIL import Image

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
    # return cmd.replace("'", r"\'").replace(',', '\\,')#.replace(' ', '\\ ')\
    return cmd

transitions = ['left-in', 'right-in', 'center']


##Assumes all media files are in a folder called data, and linked properly in the csv
class Otto:
    def __init__(self, data: str):
        self.data = openCsv(data)
        self.photos = []
        for i in range(1,11):
            self.photos.append(download(self.data['MEDIA' + str(i)], location='data'))



    def addOverlay(self, text, font_size=150, transition=None):
        return {
            'title': text,
            'font': 'Bauhaus 93',
            'font_size': font_size,
            'duration': 5,
            'transition_x': transition or choice(transitions),
        }

    def render(self):
        #TODO rename config so its not a duplicate key!
        self.config = loads(open('example.json', 'r').read())
        self.config['slides'] = []


        for p in self.photos:
            self.config['slides'].append({
                'file': p,
                'slide_duration': 5,
            })
        self.config['slides'][0]['overlay'] = self.addOverlay(textEsc(self.data['NAME']), font_size=200, transition='center')
        self.config['slides'][1]['overlay'] = self.addOverlay(textEsc(self.data['ADDRESS']), font_size=150, transition='center')
        self.config['slides'][2]['overlay'] = self.addOverlay(textEsc(self.data['INITIAL']), font_size=70, transition='center')
        self.config['slides'][3]['overlay'] = self.addOverlay(textEsc(self.data['BULLET1']))
        self.config['slides'][4]['overlay'] = self.addOverlay(textEsc(self.data['BULLET2']))
        self.config['slides'][5]['overlay'] = self.addOverlay(textEsc(self.data['BULLET3']))
        self.config['slides'][6]['overlay'] = self.addOverlay(textEsc(self.data['BULLET4']))
        self.config['slides'][7]['overlay'] = self.addOverlay(textEsc(self.data['OPTIONAL']), font_size=70, transition='center')
        self.config['slides'][-1]['overlay'] = self.addOverlay(textEsc(self.data['NAME']), font_size=200, transition='center')


        with open('export.json', 'w') as f:
            f.write(dumps(self.config))
        run(['kburns', 'kbout.mp4', '-f', 'export.json'])

        im = Image.open('data/steves.png')
        w, h = im.size

        main = ffmpeg.input('kbout.mp4')
        logo = ffmpeg.input('data/' + self.data["LOGO"])
        (
            ffmpeg
            # .overlay(overlay_file)
            .filter([main, logo], 'overlay', self.config['config']['output_width']-w, self.config['config']['output_height']-h)
            .output('logoout.mp4')
            .run()
        )


if __name__ == '__main__':
    v = Otto('data.csv')
    v.render()
