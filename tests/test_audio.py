"""Audio clips are mixed into the sound, never drawn.

An audio clip used to be built and then appended to the video layers, so any
Edl with one crashed: AttributeError on its crossfade, or CompositeVideoClip
reading `.audio` off it. The `audio` argument of renderMultitrack was dropped.
"""

import numpy as np
import pytest
from moviepy.editor import AudioFileClip

from helpers import color_clip, pixel
from otto.exceptions import EdlException
from otto.models import Clip, Edl
from otto.render import AUDIO_FPS, generateEdl

FRAME = (32, 18)


def render(*clips, audio=None, **edl):
    return generateEdl(Edl(clips=list(clips), **edl), moviesize=FRAME, audio=audio)


def sound(path, **attrs):
    attrs.setdefault('fadeIn', 0)
    attrs.setdefault('fadeOut', 0)
    return Clip(type='audio', name=path, **attrs)


def video(path, **attrs):
    return Clip(type='video', name=path, fadeIn=0, fadeOut=0, **attrs)


def samples(track, start, end):
    return track.get_frame(np.arange(start, end, 1 / AUDIO_FPS))


def loudness(track, start, end):
    """The peak amplitude of `track` between `start` and `end` seconds."""
    return float(np.abs(samples(track, start, end)).max())


def strength(track, start, end, frequency):
    """How much of `frequency` there is in `track` between start and end."""
    left = samples(track, start, end)[:, 0]
    spectrum = np.abs(np.fft.rfft(left)) / len(left)
    frequencies = np.fft.rfftfreq(len(left), 1 / AUDIO_FPS)
    return float(spectrum[np.argmin(np.abs(frequencies - frequency))])


# The synthetic tones are lavfi sines of amplitude 1/8, which read back as
# about 0.085 once upmixed to the stereo moviepy decodes to.
LOUD = 0.05
QUIET = 0.01


def test_an_audio_clip_is_heard_and_not_drawn(media):
    made = render(color_clip(duration=2), sound(media['tone'], duration=2))

    assert len(made.clips) == 1, 'the audio clip became a video layer'
    assert loudness(made.audio, 0.5, 1.5) > LOUD


def test_an_audio_clip_keeps_its_timing(media):
    made = render(
        color_clip(duration=4),
        sound(media['tone'], start=1, inpoint=0.5, outpoint=2, duration=1.5),
    )

    assert loudness(made.audio, 0, 0.95) < QUIET, 'heard before its start'
    assert loudness(made.audio, 1.05, 2.45) > LOUD
    assert loudness(made.audio, 2.55, 4) < QUIET, 'heard after its outpoint'


def test_an_audio_clip_fades_its_volume(media):
    made = render(sound(media['tone'], duration=3, fadeIn=1, fadeOut=1))

    full = loudness(made.audio, 1.2, 1.8)
    assert full > LOUD
    assert loudness(made.audio, 0, 0.1) < full / 5
    assert loudness(made.audio, 0.45, 0.55) == pytest.approx(full / 2, rel=0.2)
    assert loudness(made.audio, 2.9, 3) < full / 5


def test_an_unfaded_audio_clip_is_loud_at_once(media):
    made = render(sound(media['tone'], duration=3))
    assert loudness(made.audio, 0.05, 0.1) > LOUD


def test_audio_clips_mix_with_the_sound_of_video_clips(media):
    made = render(video(media['wide'], duration=2), sound(media['tone'], duration=2))

    assert strength(made.audio, 0.5, 1.5, 440) > 0.02, "the video's tone is lost"
    assert strength(made.audio, 0.5, 1.5, 1000) > 0.02, "the audio clip's is lost"
    assert strength(made.audio, 0.5, 1.5, 700) < 0.005


def test_sound_past_the_end_of_its_source_is_silence(media):
    """The tone is 3 seconds long; reading past that raised in moviepy."""
    made = render(color_clip(duration=1), sound(media['tone'], duration=5))

    assert made.duration == 5
    assert loudness(made.audio, 2.5, 2.9) > LOUD
    assert loudness(made.audio, 3.1, 5) < QUIET


def test_a_videos_sound_stops_where_its_source_does(media):
    """The 2-second video held for 3 seconds: its picture holds, its sound stops."""
    made = render(video(media['wide'], duration=3))

    assert loudness(made.audio, 1, 1.9) > LOUD
    assert loudness(made.audio, 2.1, 3) < QUIET


def test_video_sound_is_decoded_at_the_output_rate(media):
    made = render(video(media['wide'], duration=1))
    assert made.clips[0].audio.fps == AUDIO_FPS


def test_an_edl_of_sound_alone_plays_over_black(media):
    made = render(sound(media['tone'], duration=2))

    assert tuple(made.size) == FRAME
    assert made.duration == 2
    assert pixel(made, 1, 16, 9) == (0, 0, 0)
    assert loudness(made.audio, 0.5, 1.5) > LOUD


def test_an_inpoint_past_the_end_of_the_sound_is_refused(media):
    with pytest.raises(EdlException, match=r"clip 0 .*inpoint 5.*seconds long"):
        render(sound(media['tone'], inpoint=5, duration=1))


# --- the soundtrack ---------------------------------------------------------


def test_a_soundtrack_path_is_mixed_in(media):
    made = render(color_clip(duration=2), audio=media['tone'])

    assert made.duration == 2, 'the soundtrack does not lengthen the output'
    assert loudness(made.audio, 0.5, 1.5) > LOUD


def test_a_soundtrack_clip_is_mixed_with_the_edls_sound(media):
    track = AudioFileClip(media['tone'], fps=AUDIO_FPS)
    made = render(video(media['wide'], duration=2), audio=track)

    assert strength(made.audio, 0.5, 1.5, 440) > 0.02
    assert strength(made.audio, 0.5, 1.5, 1000) > 0.02


def test_a_soundtrack_of_another_kind_is_refused():
    with pytest.raises(EdlException, match='audio must be an AudioClip'):
        render(color_clip(), audio=42)
