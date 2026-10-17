"""What renderMultitrack is asked for is what it writes.

A few real encodes, kept tiny: 64x36, a second or two, ultrafast.
"""

import numpy as np
import pytest
from moviepy.editor import AudioFileClip, VideoFileClip
from moviepy.video.io.ffmpeg_reader import ffmpeg_parse_infos

from helpers import color_clip
from otto.exceptions import EdlException
from otto.models import Clip, Edl
from otto.render import renderMultitrack

FRAME = (64, 36)


def encode(edl, path, **kwargs):
    kwargs.setdefault('moviesize', FRAME)
    renderMultitrack(
        edl,
        filename=str(path),
        logger=None,
        ffmpeg_params=['-preset', 'ultrafast'],
        **kwargs,
    )
    return ffmpeg_parse_infos(str(path))


def sound(path, **attrs):
    return Clip(type='audio', name=path, fadeIn=0, fadeOut=0, **attrs)


def peak(path):
    with AudioFileClip(str(path)) as track:
        return float(np.abs(track.to_soundarray(fps=8000)).max())


@pytest.fixture
def recorded_encode(monkeypatch):
    """The arguments write_videofile is called with, instead of encoding."""
    calls = []

    def write_videofile(self, filename, **kwargs):
        calls.append({'filename': filename, 'size': tuple(self.size), **kwargs})

    monkeypatch.setattr(
        'moviepy.video.VideoClip.VideoClip.write_videofile', write_videofile
    )
    return calls


# --- frame rate -------------------------------------------------------------


@pytest.mark.parametrize('fps', [12, 24, 60.0])
def test_the_requested_fps_reaches_the_encoder(fps, recorded_encode):
    renderMultitrack(Edl(clips=[color_clip()]), fps=fps, moviesize=FRAME)
    assert recorded_encode[0]['fps'] == fps


def test_no_fps_takes_the_clips_rate(recorded_encode):
    renderMultitrack(Edl(clips=[color_clip()]), fps=None, moviesize=FRAME)
    assert recorded_encode[0]['fps'] == 30  # makeColor's


@pytest.mark.parametrize('fps', [0, -24])
def test_an_fps_that_is_not_positive_is_refused(fps, recorded_encode):
    with pytest.raises(EdlException, match='fps must be positive'):
        renderMultitrack(Edl(clips=[color_clip()]), fps=fps, moviesize=FRAME)
    assert recorded_encode == []


@pytest.mark.render
def test_the_file_is_written_at_the_requested_fps(tmp_path):
    infos = encode(Edl(clips=[color_clip(duration=1)]), tmp_path / 'out.mp4', fps=12)

    assert infos['video_fps'] == 12
    with VideoFileClip(str(tmp_path / 'out.mp4')) as written:
        assert tuple(written.size) == FRAME
        assert written.duration == pytest.approx(1, abs=0.1)


# --- sound ------------------------------------------------------------------


def test_the_soundtrack_reaches_the_encoder(media, recorded_encode):
    renderMultitrack(Edl(clips=[color_clip()]), audio=media['tone'], moviesize=FRAME)
    assert recorded_encode, 'nothing was encoded'


@pytest.mark.render
def test_an_audio_clip_is_in_the_file(media, tmp_path):
    out = tmp_path / 'out.mp4'
    edl = Edl(clips=[color_clip(duration=1.5), sound(media['tone'], duration=1.5)])

    infos = encode(edl, out)

    assert infos['audio_found']
    assert peak(out) > 0.05


@pytest.mark.render
def test_a_soundtrack_is_in_the_file(media, tmp_path):
    out = tmp_path / 'out.mp4'
    infos = encode(Edl(clips=[color_clip(duration=1)]), out, audio=media['tone'])

    assert infos['audio_found']
    assert peak(out) > 0.05


@pytest.mark.render
def test_a_video_held_past_the_end_of_its_sound_encodes(media, tmp_path):
    """Reading the sound past its end used to raise in the middle of the encode."""
    out = tmp_path / 'out.mp4'
    clip = Clip(type='video', name=media['wide'], duration=3, fadeIn=0, fadeOut=0)

    infos = encode(Edl(clips=[clip]), out)

    assert infos['audio_found']
    assert infos['duration'] == pytest.approx(3, abs=0.15)


@pytest.mark.render
def test_a_silent_edl_encodes(tmp_path):
    infos = encode(Edl(clips=[color_clip(duration=1)]), tmp_path / 'out.mp4')
    assert not infos['audio_found']


def test_the_sound_is_written_beside_the_output(recorded_encode):
    renderMultitrack(Edl(clips=[color_clip()]), filename='/renders/a.mp4')
    assert recorded_encode[0]['temp_audiofile'] == '/renders/a.audio.m4a'


@pytest.mark.render
def test_an_encode_leaves_the_working_directory_alone(media, tmp_path, monkeypatch):
    """moviepy wrote its temporary sound file there, named after the output."""
    cwd = tmp_path / 'cwd'
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    out = tmp_path / 'out' / 'render.mp4'
    out.parent.mkdir()

    encode(Edl(clips=[color_clip(duration=1), sound(media['tone'], duration=1)]), out)

    assert list(cwd.iterdir()) == []
    assert [p.name for p in out.parent.iterdir()] == ['render.mp4']
