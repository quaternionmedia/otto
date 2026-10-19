"""probe says what a media file holds: duration, size, frame rate, sound.

alfred asked ffmpeg itself, and read the answer with its own patterns: media
work in the control plane. otto asks now, with the ffmpeg it encodes with, and
`parse` reads the answer -- pinned against what ffmpeg actually prints
(`ffmpeg_samples.py`), and run on real tiny files the suite makes.
"""

import subprocess
from pathlib import Path

import pytest

from ffmpeg_samples import (
    GIF,
    MP3,
    MP3_WITH_COVER_ART,
    MP4_WITH_SOUND,
    PNG,
    ROTATED_42,
    ROTATED_CURRENT,
    WEBM_NTSC,
)
from helpers import rotated_copy
from otto import media
from otto.media import UNKNOWN, MediaInfo, parse, probe


class TestParsing:
    def test_a_video_with_sound(self):
        assert parse(MP4_WITH_SOUND, 'video') == MediaInfo(
            duration=3.02, width=320, height=180, fps=24.0, sound=True
        )

    def test_a_fractional_frame_rate(self):
        assert parse(WEBM_NTSC, 'video') == MediaInfo(
            duration=2.0, width=64, height=48, fps=29.97, sound=False
        )

    def test_the_codec_tag_is_not_taken_for_a_size(self):
        """`(avc1 / 0x31637661)` has digits either side of an x."""
        assert parse(MP4_WITH_SOUND, 'video').width == 320

    def test_audio_has_a_duration_a_sound_and_no_picture(self):
        assert parse(MP3, 'audio') == MediaInfo(duration=1.54, sound=True)

    def test_cover_art_is_not_audio_s_picture(self):
        assert parse(MP3_WITH_COVER_ART, 'audio') == MediaInfo(
            duration=1.54, sound=True
        )

    def test_an_image_has_a_size_and_nothing_else(self):
        """ffmpeg gives a still a nominal 25 tbr; that is not a frame rate."""
        assert parse(PNG, 'image') == MediaInfo(width=40, height=30)

    def test_an_animated_gif_is_still_an_image(self):
        """An image clip shows it still; how long it runs is the clip's."""
        assert parse(GIF, 'image') == MediaInfo(width=80, height=60)

    def test_with_no_type_everything_is_read(self):
        assert parse(GIF) == MediaInfo(
            duration=1.0, width=80, height=60, fps=10.0, sound=False
        )
        assert parse(MP3_WITH_COVER_ART).size == (500, 500)

    @pytest.mark.parametrize('description', [ROTATED_42, ROTATED_CURRENT])
    def test_a_quarter_turn_swaps_the_picture_s_sides(self, description):
        """What is shown, which is what an editor lays out."""
        found = parse(description, 'video')
        assert found.height > found.width

    def test_a_current_ffmpeg_s_output(self):
        assert parse(ROTATED_CURRENT, 'video') == MediaInfo(
            duration=62.5, width=1080, height=1920, fps=59.94, sound=False
        )

    def test_nothing_recognisable_is_unknown(self):
        assert parse('file: Invalid data found when processing input', 'video') == (
            UNKNOWN
        )

    def test_a_template_is_not_a_file(self):
        with pytest.raises(ValueError, match="not 'template'"):
            parse(MP4_WITH_SOUND, 'template')


class TestARealProbe:
    """The ffmpeg otto encodes with, on files the suite made."""

    def test_a_video_with_sound(self, media):
        found = probe(media['wide'], 'video')
        assert (found.size, found.fps, found.sound) == ((160, 90), 25.0, True)
        assert found.duration == pytest.approx(2.0, abs=0.1)

    def test_a_silent_video(self, media):
        found = probe(media['tall'], 'video')
        assert (found.size, found.sound) == ((90, 160), False)

    def test_a_turned_video_is_described_as_shown(self, media, tmp_path):
        turned = str(tmp_path / 'turned.mp4')
        rotated_copy(media['wide'], turned)
        assert probe(turned, 'video').size == (90, 160)

    def test_a_sound(self, media):
        found = probe(media['tone'], 'audio')
        assert found.duration == pytest.approx(3.0, abs=0.1)
        assert (found.size, found.fps, found.sound) == (None, None, True)

    def test_an_image(self, media):
        assert probe(media['wide_png'], 'image') == MediaInfo(width=200, height=100)

    def test_a_path_object_is_a_path(self, media):
        assert probe(Path(media['wide_png']), 'image').size == (200, 100)

    def test_a_file_that_is_not_media_is_unknown(self, tmp_path):
        path = tmp_path / 'notes.mp4'
        path.write_bytes(b'not a video')
        assert probe(path, 'video') == UNKNOWN

    def test_a_file_that_is_not_there_is_unknown(self, tmp_path):
        assert probe(tmp_path / 'gone.mp4', 'video') == UNKNOWN

    def test_a_name_ffmpeg_might_read_as_a_protocol(self, tmp_path):
        """`file:` in front, so a file called `concat:...` is just a file."""
        path = tmp_path / 'concat:x.mp4'
        try:
            path.write_bytes(b'not a video')
        except OSError:
            pytest.skip('this filesystem does not allow : in a name')
        assert probe(path, 'video') == UNKNOWN


class TestWhenFfmpegDoesNotAnswer:
    def test_too_slow_is_a_timeout_error_naming_the_file(self, monkeypatch):
        def slow(command, **kwargs):
            raise subprocess.TimeoutExpired(command, kwargs['timeout'])

        monkeypatch.setattr(media.subprocess, 'run', slow)
        with pytest.raises(TimeoutError, match=r'longer than 3s .*/v/a\.mp4'):
            probe('/v/a.mp4', 'video', timeout=3)

    def test_one_that_cannot_be_started_is_an_os_error(self, monkeypatch):
        monkeypatch.setattr(media, 'get_setting', lambda name: '/no/such/ffmpeg')
        with pytest.raises(OSError):
            probe('/v/a.mp4', 'video')

    def test_a_type_it_cannot_describe_is_refused_before_ffmpeg_is_asked(
        self, monkeypatch
    ):
        asked = []
        monkeypatch.setattr(media.subprocess, 'run', lambda *a, **k: asked.append(a))
        with pytest.raises(ValueError):
            probe('/v/a.mp4', 'template')
        assert asked == []
