from subprocess import run
from os import path
from csv import reader
from json import loads


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
    csvreader = reader(open(path, 'r'))
    d = {}
    for row in csvreader:
       k, v = row
       d[k] = v
    return d

def openJson(path):
    with open(path, 'r') as f:
        return loads(f.read())
