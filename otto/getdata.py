from os import path
from csv import reader
from json import loads
from time import strftime
from requests import head
from hashlib import sha256
from otto.utils import download_url

content_types = ['image/jpeg', 'video/mp4', 'image/png', 'audio/mpeg']
extensions = ['jpg', 'mp4', 'png', 'mp3']


def hash(s):
    return sha256(s.encode()).hexdigest()


def download(url, location='data'):
    if not url.startswith('http'):
        return url
    else:
        try:
            h = head(url, allow_redirects=True)
            content_type = h.headers.get('content-type').lower()
            if not content_type:
                raise Exception('no content_type')
            if 'text' in content_type:
                raise Exception('text not allowed')
            if 'html' in content_type:
                raise Exception('html not allowed')
            if float(h.headers.get('content-length')) > 1e10:
                raise Exception('filesize too large', h.headers.get('content-length'))
            ct = h.headers.get('content-type')
            if ct not in content_types:
                raise Exception('type not allowed', h.headers.get('content-type'))
            ext = extensions[content_types.index(ct)]
            basename = f'{hash(url)}.{ext}'
            filename = path.join(location, basename) if location else basename
            if not path.isfile(filename):
                download_url(url, filename)

            return filename
        except Exception as e:
            print('error downloading file', url, e)


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


def scale(n, size=(1920, 1080)):
    return int(size[0] / n), int(size[1] / n)


def timestr(format='%Y%m%d-%H%M%S'):
    return strftime(format)


def urlToJson(path):
    import urllib.request as request

    # Open API URL
    with request.urlopen(path) as response:
        if response.getcode() == 200:
            source = response.read()
            data = loads(source)
        else:
            print('An error occurred while attempting to retrieve data from the API.')
    return data
