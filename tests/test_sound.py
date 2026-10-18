"""renderSound writes what an Edl sounds like, alone, as a mono 16-bit WAV.

alfred transcribes a timeline's sound and mixed it itself, through moviepy,
with the codec and ffmpeg options in the control plane. otto writes it now:
the sound renderMultitrack would encode, timed and mixed the same way, at the
rate a listener asks for.

Every file here is real and tiny, synthesised with the ffmpeg moviepy uses,
and read back with the standard library's `wave`.
"""

import wave

import numpy as np
import pytest

from helpers import color_clip, ffmpeg
from otto import render
from otto.exceptions import EdlException, EmptyClipsException, NoSoundException
from otto.models import Clip, Edl
from otto.render import AUDIO_FPS, renderSound

# The shared media's tones are lavfi sines of amplitude 1/8, which read back
# as about 0.085 in each channel of the stereo moviepy decodes to, and so in
# their mono mix.
LOUD = 0.05
QUIET = 0.01


def sound(path, **attrs):
    attrs.setdefault('fadeIn', 0)
    attrs.setdefault('fadeOut', 0)
    return Clip(type='audio', name=path, **attrs)


def video(path, **attrs):
    attrs.setdefault('fadeIn', 0)
    attrs.setdefault('fadeOut', 0)
    return Clip(type='video', name=path, **attrs)


def image(path, **attrs):
    return Clip(type='image', name=path, fadeIn=0, fadeOut=0, **attrs)


def read(path):
    """The WAV at `path`: its (rate, channels, sample width in bytes, codec),
    and its samples, from -1 to 1."""
    with wave.open(str(path), 'rb') as wav:
        shape = (
            wav.getframerate(),
            wav.getnchannels(),
            wav.getsampwidth(),
            wav.getcomptype(),
        )
        frames = wav.readframes(wav.getnframes())
    return shape, np.frombuffer(frames, dtype='<i2') / 32768


def peak(samples, rate, start, end):
    """The loudest sample between `start` and `end` seconds."""
    return float(np.abs(samples[int(start * rate) : int(end * rate)]).max())


def strength(samples, rate, start, end, frequency):
    """How much of `frequency` there is between `start` and `end` seconds."""
    part = samples[int(start * rate) : int(end * rate)]
    spectrum = np.abs(np.fft.rfft(part)) / len(part)
    frequencies = np.fft.rfftfreq(len(part), 1 / rate)
    return float(spectrum[np.argmin(np.abs(frequencies - frequency))])


@pytest.fixture(scope='module')
def tones(tmp_path_factory):
    """Sounds the shared media does not have, as 48 kHz WAVs of 2 seconds."""
    root = tmp_path_factory.mktemp('tones')
    files = {}

    # A 440 Hz tone in the left channel only: one microphone of two.
    files['left'] = str(root / 'left.wav')
    ffmpeg(
        '-f', 'lavfi', '-i', 'aevalsrc=0.25*sin(2*PI*440*t)|0:s=48000:d=2',
        '-c:a', 'pcm_s16le', files['left'],
    )  # fmt: skip

    # A 10 kHz tone: more than a 16 kHz file can carry, whose top is 8 kHz.
    files['high'] = str(root / 'high.wav')
    ffmpeg(
        '-f', 'lavfi', '-i', 'aevalsrc=0.25*sin(2*PI*10000*t):s=48000:d=2',
        '-c:a', 'pcm_s16le', files['high'],
    )  # fmt: skip

    return files


# --- the file ---------------------------------------------------------------


@pytest.mark.parametrize('rate', [16000, 22050, 48000, 16000.0])
def test_the_wav_is_mono_16_bit_pcm_at_the_rate_asked_for(media, tmp_path, rate):
    out = tmp_path / 'sound.wav'

    length = renderSound(Edl(clips=[sound(media['tone'], duration=2)]), out, rate)

    shape, samples = read(out)
    assert shape == (rate, 1, 2, 'NONE')
    assert length == len(samples) / rate, 'not the length of the file written'
    assert length == pytest.approx(2, abs=0.01)


def test_without_a_rate_it_is_written_at_the_rate_otto_mixes_at(media, tmp_path):
    out = tmp_path / 'sound.wav'
    renderSound(Edl(clips=[sound(media['tone'], duration=1)]), out)
    assert read(out)[0][0] == AUDIO_FPS


def test_the_file_is_a_wav_whatever_it_is_called(media, tmp_path):
    out = tmp_path / 'timeline.sound'

    renderSound(Edl(clips=[sound(media['tone'], duration=1)]), str(out), 16000)

    assert read(out)[0] == (16000, 1, 2, 'NONE')
    assert [p.name for p in tmp_path.iterdir()] == ['timeline.sound']


# --- what it sounds like ----------------------------------------------------


def test_it_runs_the_whole_edl_with_its_sound_where_it_plays(media, tmp_path):
    """A template and an image are never heard, but the output lasts until
    they end, so a moment in the file is the same moment in the render."""
    out = tmp_path / 'sound.wav'
    edl = Edl(
        clips=[
            color_clip(duration=3),
            sound(media['tone'], start=1, inpoint=0.5, outpoint=2, duration=1.5),
            image(media['wide_png'], start=2, duration=2),
        ]
    )

    length = renderSound(edl, out, 16000)

    samples = read(out)[1]
    assert length == pytest.approx(4, abs=0.01)
    assert peak(samples, 16000, 0, 0.95) < QUIET, 'heard before the clip starts'
    assert peak(samples, 16000, 1.05, 2.45) > LOUD
    assert peak(samples, 16000, 2.55, 4) < QUIET, 'heard after the clip ends'


def test_the_edls_duration_is_the_length(media, tmp_path):
    out = tmp_path / 'sound.wav'
    edl = Edl(clips=[sound(media['tone'], duration=3)], duration=1.5)

    assert renderSound(edl, out, 16000) == pytest.approx(1.5, abs=0.01)


def test_videos_and_audio_clips_are_mixed(media, tmp_path):
    out = tmp_path / 'sound.wav'
    edl = Edl(
        clips=[video(media['wide'], duration=2), sound(media['tone'], duration=2)]
    )

    renderSound(edl, out, 16000)

    samples = read(out)[1]
    assert strength(samples, 16000, 0.5, 1.5, 440) > 0.02, "the video's tone is lost"
    assert strength(samples, 16000, 0.5, 1.5, 1000) > 0.02, "the audio's is lost"
    assert strength(samples, 16000, 0.5, 1.5, 700) < 0.005


def test_a_videos_sound_fades_as_a_render_fades_it(media, tmp_path):
    out = tmp_path / 'sound.wav'
    edl = Edl(clips=[video(media['wide'], duration=2, fadeIn=0.5, fadeOut=0.5)])

    renderSound(edl, out, 16000)

    samples = read(out)[1]
    full = peak(samples, 16000, 0.7, 1.3)
    assert full > LOUD
    assert peak(samples, 16000, 0, 0.025) < full / 5
    assert peak(samples, 16000, 0.24, 0.26) == pytest.approx(full / 2, rel=0.2)
    assert peak(samples, 16000, 1.975, 2) < full / 5


def test_sound_on_one_side_is_heard_in_the_mono_mix(tones, tmp_path):
    """The two channels are folded into one, not one of them kept: a tone on
    the left alone is still heard."""
    out = tmp_path / 'sound.wav'

    renderSound(Edl(clips=[sound(tones['left'], duration=2)]), out, 16000)

    samples = read(out)[1]
    assert strength(samples, 16000, 0.5, 1.5, 440) > 0.02


def test_what_is_too_high_for_the_rate_is_filtered_out_not_folded_down(tones, tmp_path):
    """Taking every third sample of a 48 kHz mix would hear a 10 kHz tone at
    16 kHz as one of 6 kHz; resampled, it is gone."""
    edl = Edl(clips=[sound(tones['high'], duration=2)])
    renderSound(edl, tmp_path / 'full.wav', 48000)
    renderSound(edl, tmp_path / 'speech.wav', 16000)

    full = read(tmp_path / 'full.wav')[1]
    speech = read(tmp_path / 'speech.wav')[1]
    assert peak(full, 48000, 0.5, 1.5) > LOUD
    assert peak(speech, 16000, 0.5, 1.5) < QUIET
    assert strength(speech, 16000, 0.5, 1.5, 6000) < 0.001


def test_templates_and_images_are_not_built(media, tmp_path, monkeypatch):
    def built(*args, **kwargs):
        raise AssertionError('a clip that cannot sound was built')

    monkeypatch.setattr(render, '_make_template', built)
    monkeypatch.setattr(render, '_open_image', built)
    edl = Edl(
        clips=[
            color_clip(duration=1),
            image(media['wide_png'], duration=1),
            sound(media['tone'], duration=1),
        ]
    )

    assert renderSound(edl, tmp_path / 'sound.wav', 16000) == pytest.approx(1, abs=0.01)


# --- nothing to hear --------------------------------------------------------


def test_an_edl_with_no_video_or_audio_clip_makes_no_sound(media, tmp_path):
    out = tmp_path / 'sound.wav'
    edl = Edl(clips=[color_clip(duration=1), image(media['wide_png'], duration=1)])

    with pytest.raises(NoSoundException, match='no video or audio clip'):
        renderSound(edl, out, 16000)
    assert not out.exists()


def test_videos_without_sound_make_none(media, tmp_path):
    out = tmp_path / 'sound.wav'
    edl = Edl(clips=[color_clip(duration=2), video(media['tall'], duration=2)])

    with pytest.raises(
        NoSoundException, match='none of its video clips has sound where it plays'
    ):
        renderSound(edl, out, 16000)
    assert not out.exists()


def test_making_no_sound_is_an_edl_the_engine_cannot_render_as_sound():
    assert issubclass(NoSoundException, EdlException)


# --- refusals ---------------------------------------------------------------


def test_an_empty_edl_is_refused(tmp_path):
    with pytest.raises(EmptyClipsException):
        renderSound(Edl(clips=[]), tmp_path / 'sound.wav', 16000)


def test_a_clip_is_named_by_its_place_in_the_whole_edl(media, tmp_path):
    """The template before it is not built, and still counts."""
    edl = Edl(clips=[color_clip(), sound(media['tone'], inpoint=5, duration=1)])

    with pytest.raises(EdlException, match=r"^clip 2 .*inpoint 5"):
        renderSound(edl, tmp_path / 'sound.wav', 16000)


def test_the_timing_of_a_clip_that_cannot_sound_is_still_read(media, tmp_path):
    """Its end is the output's: timing that describes no clip is refused."""
    edl = Edl(clips=[sound(media['tone'], duration=1), color_clip(duration=0)])

    with pytest.raises(EdlException, match=r'^clip 2 .*duration must be positive'):
        renderSound(edl, tmp_path / 'sound.wav', 16000)


def test_an_unknown_clip_type_is_refused(media, tmp_path):
    edl = Edl(clips=[Clip(type='speech', name=media['tone'], duration=1)])

    with pytest.raises(EdlException, match=r'^clip 1 .*unknown clip type'):
        renderSound(edl, tmp_path / 'sound.wav', 16000)


def test_an_edl_duration_that_is_not_positive_is_refused(media, tmp_path):
    edl = Edl(clips=[sound(media['tone'], duration=1)], duration=0)

    with pytest.raises(EdlException, match='duration must be positive'):
        renderSound(edl, tmp_path / 'sound.wav', 16000)


@pytest.mark.parametrize(
    'rate', [0, -16000, 16000.5, float('nan'), float('inf'), True, '16000', None]
)
def test_a_rate_that_is_not_a_positive_whole_number_is_refused(media, tmp_path, rate):
    out = tmp_path / 'sound.wav'

    with pytest.raises(EdlException, match='rate must be a positive whole number'):
        renderSound(Edl(clips=[sound(media['tone'], duration=1)]), out, rate)
    assert not out.exists()
