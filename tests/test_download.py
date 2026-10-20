"""Remote media is fetched into a private cache, never the working directory.

`download` fetched into `data/` under the working directory: in alfred, the
directory served without authentication, so every remote file a render used
was there for anyone to fetch by name. It also wrote the file in place, so a
fetch that failed part way left a truncated file that was reused as if whole.
"""

import os
import shutil
import stat
import tempfile
import urllib.request

import pytest

from helpers import BLACK_MP4
from otto import getdata
from otto.exceptions import DownloadException
from otto.models import Clip, Edl
from otto.render import generateEdl

URL = 'https://example.test/a.mp4'
OTHER_URL = 'https://example.test/b.mp4'

posix_only = pytest.mark.skipif(
    not hasattr(os, 'getuid'), reason='POSIX ownership and permissions'
)


@pytest.fixture
def fetched(monkeypatch):
    """Fetch every URL as a copy of BLACK_MP4; the URLs fetched, in order."""
    urls = []

    def fetch(url, filename):
        urls.append(url)
        shutil.copy(BLACK_MP4, filename)

    monkeypatch.setattr(getdata, 'download_url', fetch)
    return urls


@pytest.fixture
def temp(monkeypatch, tmp_path):
    """No OTTO_DOWNLOAD_DIR, and a system temporary directory of this test's own."""
    root = tmp_path / 'tmp'
    root.mkdir()
    monkeypatch.delenv(getdata.DOWNLOAD_DIR_ENV, raising=False)
    monkeypatch.setattr(tempfile, 'tempdir', str(root))
    monkeypatch.setattr(getdata, '_own_cache', None)
    return root


@pytest.fixture
def cwd(monkeypatch, tmp_path):
    """A working directory with a `data/` in it, as alfred's has."""
    work = tmp_path / 'work'
    (work / 'data').mkdir(parents=True)
    monkeypatch.chdir(work)
    return work


def files_in(directory):
    return sorted(
        str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file()
    )


def inside(filename, directory):
    return os.path.commonpath([str(filename), str(directory)]) == str(directory)


def mode(path):
    return stat.S_IMODE(os.stat(path).st_mode)


# --- where it goes ----------------------------------------------------------


def test_remote_media_is_not_fetched_into_the_working_directory(
    fake_head, fetched, temp, cwd
):
    filename = getdata.download(URL)

    assert files_in(cwd) == []
    assert os.path.isfile(filename)
    assert inside(filename, temp)
    assert os.path.dirname(filename) == getdata.download_dir()


def test_a_render_fetches_its_remote_media_into_the_cache(
    fake_head, fetched, temp, cwd
):
    generateEdl(Edl(clips=[Clip(type='video', name=URL, duration=1)]), (32, 18))

    assert fetched == [URL]
    assert files_in(cwd) == []
    assert len(files_in(temp)) == 1


@posix_only
def test_the_cache_is_readable_by_this_user_alone(fake_head, fetched, temp):
    filename = getdata.download(URL)
    assert mode(os.path.dirname(filename)) == 0o700


def test_otto_download_dir_says_where_remote_media_goes(
    fake_head, fetched, monkeypatch, tmp_path
):
    configured = tmp_path / 'remote' / 'cache'
    monkeypatch.setenv(getdata.DOWNLOAD_DIR_ENV, str(configured))

    filename = getdata.download(URL)

    assert os.path.dirname(filename) == str(configured), 'and it is made if need be'
    assert os.path.isfile(filename)


def test_a_download_dir_that_cannot_be_used_is_reported(
    fake_head, fetched, monkeypatch, tmp_path
):
    not_a_directory = tmp_path / 'file'
    not_a_directory.write_text('')
    monkeypatch.setenv(getdata.DOWNLOAD_DIR_ENV, str(not_a_directory))

    with pytest.raises(DownloadException, match=f'{URL}: nowhere to download it'):
        getdata.download(URL)
    assert fetched == []


@pytest.mark.parametrize('positional', [True, False])
def test_a_location_given_is_still_where_it_goes(
    positional, fake_head, fetched, temp, cwd
):
    """The signature is unchanged: a caller that names a location gets it."""
    if positional:
        filename = getdata.download(URL, 'data')
    else:
        filename = getdata.download(URL, location='data')

    assert os.path.dirname(filename) == 'data'
    assert files_in(cwd) == [os.path.join('data', os.path.basename(filename))]
    assert files_in(temp) == []


# --- reuse ------------------------------------------------------------------


def test_a_url_is_fetched_once_and_then_reused(fake_head, fetched):
    first = getdata.download(URL)
    again = getdata.download(URL)
    other = getdata.download(OTHER_URL)

    assert first == again
    assert other != first
    assert fetched == [URL, OTHER_URL]


def test_the_cached_name_is_a_hash_of_the_url(fake_head, fetched):
    filename = getdata.download(URL)
    assert os.path.basename(filename) == f'{getdata.hash(URL)}.mp4'


# --- whole or not at all ----------------------------------------------------


def serve_bytes(monkeypatch, *bodies):
    """Make urlretrieve answer with each body in turn. A body that is an
    exception is raised once part of a file has been written."""
    answers = list(bodies)

    def urlretrieve(url, filename, reporthook=None):
        body = answers.pop(0)
        with open(filename, 'wb') as file:
            if isinstance(body, Exception):
                file.write(b'half a file')
                raise body
            file.write(body)
        return filename, {}

    monkeypatch.setattr(urllib.request, 'urlretrieve', urlretrieve)


def test_a_fetch_that_fails_part_way_leaves_nothing_to_reuse(
    fake_head, monkeypatch, download_dir
):
    serve_bytes(monkeypatch, OSError('connection reset'), b'the whole file')

    with pytest.raises(DownloadException, match='connection reset'):
        getdata.download(URL)
    assert files_in(download_dir) == [], 'a partial file was left behind'

    filename = getdata.download(URL)
    with open(filename, 'rb') as file:
        assert file.read() == b'the whole file'
    assert files_in(download_dir) == [os.path.basename(filename)]


@posix_only
def test_a_fetched_file_is_readable_by_this_user_alone(
    fake_head, monkeypatch, download_dir
):
    serve_bytes(monkeypatch, b'media')
    assert mode(getdata.download(URL)) == 0o600


# --- a cache someone else made ----------------------------------------------


def shared_cache(temp):
    return temp / f'otto-downloads-{os.getuid()}'


@posix_only
def test_a_cache_others_can_read_is_made_private(fake_head, fetched, temp):
    cache = shared_cache(temp)
    cache.mkdir()
    cache.chmod(0o755)

    filename = getdata.download(URL)

    assert os.path.dirname(filename) == str(cache)
    assert mode(cache) == 0o700


@posix_only
def test_a_link_where_the_cache_should_be_is_not_followed(
    fake_head, fetched, temp, tmp_path
):
    elsewhere = tmp_path / 'elsewhere'
    elsewhere.mkdir()
    shared_cache(temp).symlink_to(elsewhere, target_is_directory=True)

    first = getdata.download(URL)
    second = getdata.download(OTHER_URL)

    assert files_in(elsewhere) == []
    assert inside(first, temp)
    assert os.path.dirname(first) == os.path.dirname(second), 'one cache per process'
    assert mode(os.path.dirname(first)) == 0o700


@posix_only
@pytest.mark.skipif(
    not hasattr(os, 'geteuid') or os.geteuid() != 0,
    reason='only root can give a directory away',
)
def test_a_cache_another_user_owns_is_not_used(fake_head, fetched, temp):
    cache = shared_cache(temp)
    cache.mkdir(mode=0o700)
    os.chown(cache, os.getuid() + 1, -1)

    filename = getdata.download(URL)

    assert files_in(cache) == []
    assert inside(filename, temp)
    assert os.stat(os.path.dirname(filename)).st_uid == os.getuid()
