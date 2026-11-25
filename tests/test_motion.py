"""motion says how much a video's picture changes over time.

Measured on clips the suite makes from ffmpeg's own test sources: the test
card, whose pattern moves and whose counter ticks, and a plain colour, which
does not.
"""

import pytest

from helpers import ffmpeg
from otto.demo import demoClip
from otto.exceptions import FFmpegException
from otto.media import MOTION_RATE, MOTION_SIZE, Motion, motion

LENGTH = 2


@pytest.fixture(scope='module')
def clips(tmp_path_factory):
    root = tmp_path_factory.mktemp('motion')
    made = {}
    for source in ('testcard', 'color'):
        made[source] = str(root / f'{source}.mp4')
        demoClip(made[source], source, duration=LENGTH, size=(160, 90), fps=24)
    made['sound'] = str(root / 'sound.wav')
    ffmpeg(
        '-f',
        'lavfi',
        '-i',
        'sine=frequency=440:sample_rate=16000:duration=1',
        made['sound'],
    )
    return made


def test_a_moving_picture_measures_more_than_a_still_one(clips):
    moving = motion(clips['testcard'])
    still = motion(clips['color'])
    assert isinstance(moving, Motion)
    assert moving.rate == MOTION_RATE
    # One value a quarter second, the first for a moment with nothing before it.
    assert abs(len(moving.values) - LENGTH * MOTION_RATE) <= 1
    assert moving.values[0] == 0
    assert max(moving.values[1:]) > 0.01
    assert all(0 <= value <= 1 for value in moving.values)
    assert still.values and all(value == 0 for value in still.values)


def test_the_rate_and_the_size_are_the_caller_s(clips):
    measured = motion(clips['testcard'], rate=10, size=(8, 8))
    assert measured.rate == 10
    assert abs(len(measured.values) - LENGTH * 10) <= 1


def test_the_default_size_is_small():
    assert MOTION_SIZE[0] * MOTION_SIZE[1] < 1000


@pytest.mark.parametrize(
    'arguments',
    [
        {'rate': 0},
        {'rate': -1},
        {'rate': 'fast'},
        {'size': (0, 18)},
        {'size': 32},
        {'size': (32.5, 18)},
    ],
)
def test_a_rate_or_size_that_is_not_positive_is_refused_before_ffmpeg_runs(arguments):
    with pytest.raises(ValueError):
        motion('nowhere.mp4', **arguments)


def test_a_file_that_is_not_a_video_is_an_ffmpeg_exception(tmp_path):
    path = tmp_path / 'notes.mp4'
    path.write_bytes(b'not a video at all')
    with pytest.raises(FFmpegException, match='could not read the picture'):
        motion(str(path))


def test_a_sound_with_no_picture_is_an_ffmpeg_exception(clips):
    with pytest.raises(FFmpegException, match='could not read the picture'):
        motion(clips['sound'])


def test_a_file_that_is_not_there_is_an_ffmpeg_exception(tmp_path):
    with pytest.raises(FFmpegException):
        motion(str(tmp_path / 'gone.mp4'))
