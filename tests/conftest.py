"""Shared fixtures.

Media is synthesised once per session with the ffmpeg moviepy itself uses
(imageio-ffmpeg's), so the suite needs no media beyond the two files checked
in, and no network.

Every test downloads into a directory of its own (OTTO_DOWNLOAD_DIR), so none
fetches into, or reuses a file from, the real download cache.
"""

import pytest
from PIL import Image

from helpers import SECONDS, ffmpeg
from otto import getdata


@pytest.fixture(autouse=True)
def download_dir(monkeypatch, tmp_path):
    """The directory remote media is fetched into during this test."""
    directory = tmp_path / 'downloads'
    monkeypatch.setenv(getdata.DOWNLOAD_DIR_ENV, str(directory))
    return directory


class FakeHead:
    """What `requests.head` answers, as far as `download` reads it."""

    def __init__(self, content_type='video/mp4', content_length='1000'):
        self.headers = {}
        if content_type is not None:
            self.headers['content-type'] = content_type
        if content_length is not None:
            self.headers['content-length'] = content_length


@pytest.fixture
def fake_head(monkeypatch):
    """Answer `download`'s HEAD requests; call the result to change the answer."""
    state = {'response': FakeHead()}
    monkeypatch.setattr(getdata, 'head', lambda url, allow_redirects: state['response'])

    def serve(**kwargs):
        state['response'] = FakeHead(**kwargs)

    return serve


@pytest.fixture(scope='session')
def media(tmp_path_factory):
    """Paths to synthetic media, keyed by what each one is for."""
    root = tmp_path_factory.mktemp('media')
    files = {}

    # 16:9 red picture with a 440 Hz tone, 2 seconds.
    files['wide'] = str(root / 'wide.mp4')
    ffmpeg(
        '-f', 'lavfi', '-i', 'color=c=red:size=160x90:rate=25:duration=2',
        '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=48000:duration=2',
        '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', files['wide'],
    )  # fmt: skip

    # 9:16 blue picture, silent, 2 seconds.
    files['tall'] = str(root / 'tall.mp4')
    ffmpeg(
        '-f', 'lavfi', '-i', 'color=c=blue:size=90x160:rate=25:duration=2',
        '-pix_fmt', 'yuv420p', files['tall'],
    )  # fmt: skip

    # A clock: four seconds, each a different colour (SECONDS), so the colour
    # of a frame says which second of the source it came from.
    files['clock'] = str(root / 'clock.mp4')
    sources = ';'.join(
        f'color=c={name}:size=32x18:rate=10:duration=1[s{n}]'
        for n, (name, _) in enumerate(SECONDS)
    )
    ffmpeg(
        '-filter_complex', f'{sources};[s0][s1][s2][s3]concat=n=4:v=1:a=0[out]',
        '-map', '[out]', '-pix_fmt', 'yuv444p', '-c:v', 'libx264', '-qp', '0',
        files['clock'],
    )  # fmt: skip

    # A 1 kHz tone, 3 seconds, as an mp3: the way remote audio arrives.
    files['tone'] = str(root / 'tone.mp3')
    ffmpeg(
        '-f', 'lavfi', '-i', 'sine=frequency=1000:sample_rate=48000:duration=3',
        files['tone'],
    )  # fmt: skip

    # Images: a wide opaque one, a tall one whose bottom half is transparent,
    # and a greyscale one.
    files['wide_png'] = str(root / 'wide.png')
    Image.new('RGB', (200, 100), (0, 0, 255)).save(files['wide_png'])

    tall = Image.new('RGBA', (50, 100), (255, 0, 0, 255))
    tall.paste((0, 0, 0, 0), (0, 50, 50, 100))
    files['tall_png'] = str(root / 'tall.png')
    tall.save(files['tall_png'])

    files['grey_png'] = str(root / 'grey.png')
    Image.new('L', (40, 40), 200).save(files['grey_png'])

    return files
