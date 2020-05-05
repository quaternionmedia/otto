import ffmpeg
import numpy as np
from subprocess import run
from typing import List
from os import path
from json import loads, dumps

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
        self.config = loads(open('example.json', 'r').read())
        self.config['slides'] = []
        for p in self.photos:
            self.config['slides'].append({
                'file': p,
                'slide_duration': 5,
            })
        self.config['slides'][0]['overlay'] = self.addOverlay(self.address)
        self.config['slides'][1]['overlay'] = self.addOverlay(f'{self.bedrooms} bedrooms')
        self.config['slides'][2]['overlay'] = self.addOverlay(f'{self.bathrooms} bathrooms')
        self.config['slides'][3]['overlay'] = self.addOverlay(f'{self.sqft} sqft')
        with open('export.json', 'w') as f:
            f.write(dumps(self.config))
        run(['kburns', 'out.mp4', '-f', 'export.json'])


if __name__ == '__main__':
    v = Otto('data.csv')
    v.render()
