"""demoClip makes a short clip from nothing: ffmpeg's own test sources.

alfred ran ffmpeg itself to give an empty install something to edit, with the
sources' filter strings, sizes and pixel format in the control plane. otto
writes the clip now, by the source's name, and probe reads it back.
"""

from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from moviepy.editor import AudioFileClip, VideoFileClip

from helpers import close_to
from otto import demo
from otto.demo import DEMO_DURATION, DEMO_FPS, DEMO_SIZE, DEMO_SOURCES, demoClip
from otto.exceptions import FFmpegException
from otto.media import probe

BLUE_GREY = (0x10, 0x18, 0x20)
# SMPTE bars start with 75% white, then 75% yellow.
GREY_75 = (191, 191, 191)
YELLOW_75 = (191, 191, 0)


def frame(path, t=0.5):
    with VideoFileClip(str(path)) as clip:
        return np.asarray(clip.get_frame(t))


def color_at(picture, x, y):
    return tuple(int(c) for c in picture[y, x][:3])


@pytest.mark.parametrize('source', list(DEMO_SOURCES))
def test_each_source_is_a_short_small_silent_mp4(source, tmp_path):
    path = tmp_path / f'{source}.mp4'

    assert demoClip(str(path), source) == str(path)

    found = probe(path, 'video')
    assert (found.size, found.fps, found.sound) == (DEMO_SIZE, DEMO_FPS, False)
    assert found.duration == pytest.approx(DEMO_DURATION, abs=0.1)
    assert path.read_bytes()[4:8] == b'ftyp', 'an MP4 opens with its file-type box'


def test_each_source_shows_its_own_picture(tmp_path):
    bars = frame(demoClip(str(tmp_path / 'bars.mp4'), 'bars'))
    color = frame(demoClip(str(tmp_path / 'color.mp4'), 'color'))
    card = frame(demoClip(str(tmp_path / 'card.mp4'), 'testcard'))

    width, height = DEMO_SIZE
    assert close_to(color_at(bars, width // 14, height // 4), GREY_75, 12)
    assert close_to(color_at(bars, 3 * width // 14, height // 4), YELLOW_75, 12)
    assert close_to(color_at(color, width // 2, height // 2), BLUE_GREY, 6)
    assert not np.array_equal(card, color) and not np.array_equal(card, bars)


def test_the_length_size_and_rate_can_be_asked_for(tmp_path):
    path = demoClip(str(tmp_path / 'c.mp4'), 'color', duration=1, size=(32, 18), fps=4)
    found = probe(path, 'video')
    assert (found.size, found.fps) == ((32, 18), 4.0)
    assert found.duration == pytest.approx(1, abs=0.3)


def test_a_tone_is_bars_and_tone(tmp_path):
    path = demoClip(str(tmp_path / 'bars.mp4'), 'bars', tone=1000)

    assert probe(path, 'video').sound is True
    with AudioFileClip(path) as sound:
        samples = sound.to_soundarray(fps=8000)
    # A lavfi sine is 1/8 of full scale, -18 dBFS.
    assert np.abs(samples).max() == pytest.approx(0.125, abs=0.03)


def test_it_is_an_mp4_whatever_it_is_called(tmp_path):
    path = tmp_path / 'clip.part'
    demoClip(str(path), 'color', duration=1)
    assert path.read_bytes()[4:8] == b'ftyp'


@pytest.mark.parametrize(
    'arguments',
    [
        {'source': 'stripes'},
        {'duration': 0},
        {'duration': float('inf')},
        {'fps': -24},
        {'size': (0, 180)},
        {'size': (320.5, 180)},
        {'size': 320},
        {'tone': 0},
        {'tone': True},
    ],
)
def test_what_it_cannot_make_is_refused_before_ffmpeg_runs(
    arguments, tmp_path, monkeypatch
):
    asked = []
    monkeypatch.setattr(demo.subprocess, 'run', lambda *a, **k: asked.append(a))
    with pytest.raises(ValueError):
        demoClip(str(tmp_path / 'x.mp4'), **arguments)
    assert asked == [] and list(tmp_path.iterdir()) == []


def test_it_is_written_out_of_sight_and_moved_into_place(tmp_path, monkeypatch):
    """A listing taken while ffmpeg writes must not offer half a clip."""
    target = tmp_path / 'bars.mp4'
    seen = {}

    def run(command, **kwargs):
        written = Path(command[-1])
        seen['directory'], seen['name'] = written.parent, written.name
        seen['in place meanwhile'] = target.exists()
        written.write_bytes(b'a whole clip')
        return SimpleNamespace(returncode=0, stderr='')

    monkeypatch.setattr(demo.subprocess, 'run', run)
    demoClip(str(target), 'bars')

    assert seen['directory'] == tmp_path
    assert seen['name'].startswith('.bars.mp4.') and seen['name'].endswith('.part')
    assert seen['in place meanwhile'] is False
    assert target.read_bytes() == b'a whole clip'
    assert [p.name for p in tmp_path.iterdir()] == ['bars.mp4']


def test_a_failed_run_leaves_nothing_and_says_what_ffmpeg_said(tmp_path, monkeypatch):
    monkeypatch.setitem(DEMO_SOURCES, 'broken', 'nosuchsource')
    target = tmp_path / 'broken.mp4'

    with pytest.raises(FFmpegException) as failed:
        demoClip(str(target), 'broken')

    assert 'nosuchsource' in failed.value.stderr
    assert str(failed.value).startswith(
        f'ffmpeg could not write a demo clip to {target}: '
    )
    assert list(tmp_path.iterdir()) == []


def test_a_failed_run_keeps_the_clip_that_was_there(tmp_path, monkeypatch):
    monkeypatch.setitem(DEMO_SOURCES, 'broken', 'nosuchsource')
    target = tmp_path / 'bars.mp4'
    target.write_bytes(b'the clip from before')

    with pytest.raises(FFmpegException):
        demoClip(str(target), 'broken')

    assert target.read_bytes() == b'the clip from before'
    assert [p.name for p in tmp_path.iterdir()] == ['bars.mp4']


def test_an_ffmpeg_that_cannot_be_started_is_an_os_error(tmp_path, monkeypatch):
    monkeypatch.setattr(demo, 'get_setting', lambda name: '/no/such/ffmpeg')
    with pytest.raises(OSError):
        demoClip(str(tmp_path / 'bars.mp4'), 'bars')
    assert list(tmp_path.iterdir()) == []
