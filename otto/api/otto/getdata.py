from subprocess import run
from os import path
from csv import reader
from json import loads


def download(url, location='data'):
    if url.find('.jpg') > 0:
        basename = run(['basename', url.split('.jpg')[0] + '.jpg'], capture_output=True).stdout.decode().strip()
    elif url.find('.png') > 0:
        basename = run(['basename', url.split('.png')[0] + '.png'], capture_output=True).stdout.decode().strip()
    else:
        basename = run(['basename', url.split('/')[-1]]).strip()
    filename = path.join(location, basename) if location else basename
    if not path.isfile(filename):
        if location:
            run(['wget', '--content-disposition', '-O', filename, url])
        else:
            run(['wget', '--content-disposition', url])
    return filename

def openCsv(path):
    csvreader = reader(open(path, 'r'))
    d = {}
    for row in csvreader:
       k, v = row
       d[k] = v
    return d

def openJson(path):
    with open(path, 'r') as f:
        return loads(f.read())

def scale(n, size=(1920,1080)):
    return int(size[0]/n), int(size[1]/n)
