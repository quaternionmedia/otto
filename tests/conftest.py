"""Shared fixtures.

Media is synthesised once per session with the ffmpeg moviepy itself uses
(imageio-ffmpeg's), so the suite needs no media beyond the two files checked
in, and no network.
"""

import pytest
from PIL import Image

from helpers import SECONDS, ffmpeg


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
