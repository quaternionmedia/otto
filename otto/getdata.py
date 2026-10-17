from os import path
from csv import reader
from json import loads
from time import strftime
from requests import head
from hashlib import sha256
from otto.exceptions import DownloadException
from otto.utils import download_url

content_types = ['image/jpeg', 'video/mp4', 'image/png', 'audio/mpeg']
extensions = ['jpg', 'mp4', 'png', 'mp3']

MAX_DOWNLOAD_BYTES = 1e10
"""The largest remote file `download` will fetch, by its content-length."""


def hash(s):
    return sha256(s.encode()).hexdigest()


def download(url, location='data'):
    """A local path for `url`, fetching it into `location` first if it is remote.

    Anything not starting with `http` is taken to be local already and is
    returned unchanged. A remote file is fetched once, named by a hash of its
    URL, and only when its HEAD response describes one of `content_types` no
    larger than MAX_DOWNLOAD_BYTES.

    Raises DownloadException, naming the URL and the reason, when the file is
    refused or cannot be fetched.
    """
    if not url.startswith('http'):
        return url
    try:
        response = head(url, allow_redirects=True)
    except Exception as exc:
        raise DownloadException(f'{url}: could not be reached: {exc}') from exc

    content_type = response.headers.get('content-type')
    if not content_type:
        raise DownloadException(f'{url}: no content_type in the response')
    media_type = content_type.split(';')[0].strip().lower()
    if 'text' in media_type or 'html' in media_type:
        raise DownloadException(f'{url}: {content_type!r} not allowed: text')
    if media_type not in content_types:
        raise DownloadException(
            f'{url}: {content_type!r} type not allowed; '
            f'allowed: {", ".join(content_types)}'
        )

    length = response.headers.get('content-length')
    try:
        size = float(length)
    except (TypeError, ValueError):
        raise DownloadException(
            f'{url}: content-length {length!r} not allowed: the size must be known'
        ) from None
    if size > MAX_DOWNLOAD_BYTES:
        raise DownloadException(
            f'{url}: filesize too large: {length} bytes, '
            f'the limit is {MAX_DOWNLOAD_BYTES:.0f}'
        )

    ext = extensions[content_types.index(media_type)]
    basename = f'{hash(url)}.{ext}'
    filename = path.join(location, basename) if location else basename
    if not path.isfile(filename):
        try:
            download_url(url, filename)
        except Exception as exc:
            raise DownloadException(f'{url}: download failed: {exc}') from exc
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
