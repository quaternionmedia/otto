import logging
import os
import stat
import tempfile
from csv import reader
from hashlib import sha256
from json import loads
from os import path
from time import strftime

from requests import head

from otto.exceptions import DownloadException
from otto.utils import download_url

log = logging.getLogger(__name__)

content_types = ['image/jpeg', 'video/mp4', 'image/png', 'audio/mpeg']
extensions = ['jpg', 'mp4', 'png', 'mp3']

MAX_DOWNLOAD_BYTES = 1e10
"""The largest remote file `download` will fetch, by its content-length."""

DOWNLOAD_DIR_ENV = 'OTTO_DOWNLOAD_DIR'
"""The environment variable that says where `download` keeps remote media."""


def hash(s):
    return sha256(s.encode()).hexdigest()


_own_cache = None
"""A cache made for this process alone, when the shared one is not trusted."""


def _private_cache_dir():
    """A cache under the system temporary directory that only this user reads.

    Its name is predictable, so where other users can write to the temporary
    directory, one of them could have made it first -- or left a link there --
    and so chosen what a URL's cached file holds. A directory that is not this
    user's own is passed over for one made afresh for this process: as safe,
    but not shared with other processes.
    """
    global _own_cache
    uid = os.getuid() if hasattr(os, 'getuid') else None
    name = 'otto-downloads' if uid is None else f'otto-downloads-{uid}'
    directory = path.join(tempfile.gettempdir(), name)
    try:
        os.mkdir(directory, 0o700)
    except FileExistsError:
        pass
    if uid is None:
        # Windows, where the temporary directory is the user's own already.
        return directory
    info = os.lstat(directory)
    if stat.S_ISDIR(info.st_mode) and info.st_uid == uid:
        if stat.S_IMODE(info.st_mode) & 0o077:
            os.chmod(directory, 0o700)
        return directory
    if _own_cache is None or not path.isdir(_own_cache):
        _own_cache = tempfile.mkdtemp(prefix='otto-downloads-')
        log.warning(
            '%s is not a directory of this user\'s own; downloading to %s instead',
            directory,
            _own_cache,
        )
    return _own_cache


def download_dir():
    """Where `download` keeps remote media when it is not told where.

    OTTO_DOWNLOAD_DIR when that is set, made if it does not exist; otherwise a
    cache of this user's own under the system temporary directory. Never the
    working directory: `download` fetched into `data/` there, which is the
    directory alfred serves without authentication, so every remote file a
    render used was published to anyone who asked for it by name.
    """
    configured = os.environ.get(DOWNLOAD_DIR_ENV)
    if configured:
        os.makedirs(configured, mode=0o700, exist_ok=True)
        return configured
    return _private_cache_dir()


def download(url, location=None):
    """A local path for `url`, fetching it into `location` first if it is remote.

    Anything not starting with `http` is taken to be local already and is
    returned unchanged. A remote file is fetched only when its HEAD response
    describes one of `content_types` no larger than MAX_DOWNLOAD_BYTES. It is
    named by a hash of its URL, and a URL already fetched into `location` is
    not fetched again. `location` defaults to `download_dir()`.

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
    try:
        if location is None:
            location = download_dir()
        elif location:
            os.makedirs(location, exist_ok=True)
    except OSError as exc:
        raise DownloadException(f'{url}: nowhere to download it to: {exc}') from exc
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
