"""scenes says where a video's picture cuts from one shot to another.

Measured on clips the suite makes from ffmpeg's own test sources: one colour
then another, which is a cut, and a plain colour, which is not.
"""

import pytest

from helpers import ffmpeg
from otto.demo import demoClip
from otto.exceptions import FFmpegException
from otto.media import SCENE_RATE, SCENE_THRESHOLD, Scenes, scenes


@pytest.fixture(scope='module')
def clips(tmp_path_factory):
    root = tmp_path_factory.mktemp('scenes')
    made = {'cut': str(root / 'cut.mp4'), 'color': str(root / 'color.mp4')}
    # A second of black, then a second of white: one cut, at 1 s, that any
    # threshold passes.
    ffmpeg(
        '-f',
        'lavfi',
        '-i',
        'color=c=black:s=160x90:r=24:d=1',
        '-f',
        'lavfi',
        '-i',
        'color=c=white:s=160x90:r=24:d=1',
        '-filter_complex',
        '[0:v][1:v]concat=n=2:v=1:a=0',
        made['cut'],
    )
    demoClip(made['color'], 'color', duration=2, size=(160, 90), fps=24)
    made['sound'] = str(root / 'sound.wav')
    ffmpeg(
        '-f',
        'lavfi',
        '-i',
        'sine=frequency=440:sample_rate=16000:duration=1',
        made['sound'],
    )
    return made


def test_a_cut_is_found_where_it_is_and_a_still_has_none(clips):
    """Mutation: answer every frame's time -- red; a still would have cuts."""
    found = scenes(clips['cut'])
    assert isinstance(found, Scenes)
    assert found.threshold == SCENE_THRESHOLD
    # To the rate's precision: the first frame of the second colour.
    assert len(found.seconds) == 1
    assert abs(found.seconds[0] - 1.0) <= 1 / SCENE_RATE
    assert scenes(clips['color']).seconds == []


def test_the_threshold_and_the_rate_are_the_caller_s(clips):
    found = scenes(clips['cut'], threshold=0.99, rate=12)
    assert found.threshold == 0.99
    assert len(found.seconds) == 1 and abs(found.seconds[0] - 1.0) <= 1 / 12


@pytest.mark.parametrize(
    'arguments',
    [
        {'threshold': 0},
        {'threshold': 1.5},
        {'threshold': True},
        {'rate': 0},
        {'size': (0, 9)},
    ],
)
def test_a_threshold_rate_or_size_that_is_not_one_is_refused_first(clips, arguments):
    with pytest.raises(ValueError):
        scenes(clips['cut'], **arguments)


def test_a_sound_has_no_picture_to_read(clips):
    with pytest.raises(FFmpegException):
        scenes(clips['sound'])


def test_a_file_that_is_not_there(tmp_path):
    with pytest.raises(FFmpegException):
        scenes(str(tmp_path / 'nowhere.mp4'))
