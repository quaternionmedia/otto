"""What renderMultitrack is asked for is what it writes.

A few real encodes, kept tiny: 64x36, a second or two, ultrafast.
"""

import re

import numpy as np
import pytest
from moviepy.editor import AudioFileClip, VideoFileClip
from moviepy.video.io.ffmpeg_reader import ffmpeg_parse_infos

from helpers import color_clip
from otto.exceptions import EdlException
from otto.models import Clip, Edl
from otto.render import PRESETS, renderMultitrack

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


# --- presets ----------------------------------------------------------------


def test_the_presets_are_named():
    assert list(PRESETS) == ['draft', 'standard', 'high']


def test_better_quality_asks_for_a_lower_rate_factor_and_more_time():
    crf = {name: preset.crf for name, preset in PRESETS.items()}
    assert crf['draft'] > crf['standard'] > crf['high']
    speeds = ['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium']
    speeds += ['slow', 'slower', 'veryslow']
    order = [speeds.index(p.x264_preset) for p in PRESETS.values()]
    assert order == sorted(order)


@pytest.mark.parametrize('name', list(PRESETS))
def test_a_preset_reaches_the_encoder(name, recorded_encode):
    renderMultitrack(Edl(clips=[color_clip()]), moviesize=FRAME, preset=name)

    (call,) = recorded_encode
    chosen = PRESETS[name]
    assert call['codec'] == 'libx264'
    assert call['preset'] == chosen.x264_preset
    assert call['ffmpeg_params'] == ['-crf', str(chosen.crf)]
    assert call['audio_bitrate'] == chosen.audio_bitrate
    assert call['bitrate'] is None


def test_without_a_preset_the_encoding_is_as_given(recorded_encode):
    """moviepy's own `preset` default, medium, and 320k sound, as before."""
    renderMultitrack(Edl(clips=[color_clip()]), moviesize=FRAME)
    renderMultitrack(
        Edl(clips=[color_clip()]),
        moviesize=FRAME,
        bitrate='900k',
        audio_bitrate='96k',
        ffmpeg_params=['-tune', 'animation'],
    )

    plain, given = recorded_encode
    assert 'preset' not in plain
    assert (plain['bitrate'], plain['audio_bitrate'], plain['ffmpeg_params']) == (
        None,
        '320k',
        None,
    )
    assert (given['bitrate'], given['audio_bitrate'], given['ffmpeg_params']) == (
        '900k',
        '96k',
        ['-tune', 'animation'],
    )


@pytest.mark.parametrize(
    'arguments, refusal',
    [
        ({'preset': 'web'}, "preset must be one of draft, standard, high, not 'web'"),
        ({'preset': 'draft', 'bitrate': '5000k'}, 'bitrate cannot be given'),
        ({'preset': 'draft', 'audio_bitrate': '64k'}, 'audio_bitrate cannot be'),
        ({'preset': 'high', 'ffmpeg_params': ['-crf', '0']}, 'ffmpeg_params cannot'),
        ({'preset': 'high', 'codec': 'mpeg4'}, "cannot encode with 'mpeg4'"),
    ],
)
def test_what_a_preset_cannot_be_given_with_is_refused(
    arguments, refusal, recorded_encode
):
    with pytest.raises(EdlException, match=re.escape(refusal)):
        renderMultitrack(Edl(clips=[color_clip()]), moviesize=FRAME, **arguments)
    assert recorded_encode == []


@pytest.mark.render
def test_a_draft_is_encoded(tmp_path):
    out = tmp_path / 'draft.mp4'
    renderMultitrack(
        Edl(clips=[color_clip(duration=1)]),
        filename=str(out),
        moviesize=FRAME,
        logger=None,
        preset='draft',
    )
    infos = ffmpeg_parse_infos(str(out))
    assert infos['video_size'] == list(FRAME)
    assert infos['duration'] == pytest.approx(1, abs=0.1)
