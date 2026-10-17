"""Clips are placed by their own timing, and zero means zero.

`outpoint` used to be ignored, `start`, `fadeIn`, `fadeOut` and `opacity`
were truthiness checks, and every template faded itself in and out on top of
whatever the clip asked for.
"""

import pytest
from helpers import SECONDS, close_to, color_clip, pixel
from moviepy.video.VideoClip import VideoClip

from otto.exceptions import EdlException
from otto.models import Clip, Edl, TemplateData
from otto.render import Timing, clipTiming, generateEdl

FRAME = (32, 18)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


def render(*clips, **edl):
    return generateEdl(Edl(clips=list(clips), **edl), moviesize=FRAME)


def still(color='#00ff00', **attrs):
    """A colour clip with no fades, so any fade seen is one asked for."""
    attrs.setdefault('fadeIn', 0)
    attrs.setdefault('fadeOut', 0)
    return color_clip(color, **attrs)


def clock(path, **attrs):
    attrs.setdefault('fadeIn', 0)
    attrs.setdefault('fadeOut', 0)
    return Clip(type='video', name=path, **attrs)


def second(n):
    return SECONDS[n][1]


@pytest.fixture
def recorded_fades(monkeypatch):
    calls = []

    def record(name):
        original = getattr(VideoClip, name)

        def wrapper(self, duration, *args, **kwargs):
            calls.append((name, duration))
            return original(self, duration, *args, **kwargs)

        monkeypatch.setattr(VideoClip, name, wrapper)

    record('crossfadein')
    record('crossfadeout')
    return calls


# --- start ------------------------------------------------------------------


def test_start_places_the_clip():
    made = render(still(start=1.5, duration=2))
    assert made.clips[0].start == 1.5
    assert made.duration == 3.5


@pytest.mark.parametrize('offset', [None, 2.0])
def test_start_zero_is_the_same_as_no_start(offset):
    explicit = render(still(start=0, offset=offset)).clips[0]
    absent = render(still(offset=offset)).clips[0]
    assert (explicit.start, explicit.end) == (absent.start, absent.end)


def test_clips_are_layered_not_sequenced():
    made = render(still('#ff0000'), still('#00ff00'))

    assert [c.start for c in made.clips] == [0, 0]
    assert pixel(made, 1, 16, 9) == GREEN, 'the later clip is on top'


def test_a_positive_offset_still_delays_the_clip():
    """`offset` is deprecated; a positive one is added to `start`."""
    assert render(still(offset=2.0)).clips[0].start == 2.0
    assert render(still(start=1.0, offset=2.0)).clips[0].start == 3.0


# --- the source range -------------------------------------------------------


def test_outpoint_trims_the_clip():
    """alfred's strict xfail `test_outpoint_should_trim_the_clip`."""
    made = render(still(duration=2.0, inpoint=1.0, outpoint=1.5))
    assert made.clips[0].duration == 0.5


def test_outpoint_wins_when_duration_disagrees():
    assert render(still(duration=5, inpoint=0, outpoint=3)).clips[0].duration == 3


def test_without_an_outpoint_duration_is_the_length():
    assert render(still(duration=4, inpoint=1)).clips[0].duration == 4


def test_inpoint_and_outpoint_select_part_of_a_video(media):
    made = render(clock(media['clock'], inpoint=1, outpoint=3, duration=2))

    assert made.clips[0].duration == 2
    assert close_to(pixel(made, 0.5, 16, 9), second(1), 12)
    assert close_to(pixel(made, 1.5, 16, 9), second(2), 12)


def test_a_negative_offset_skips_into_the_source(media):
    made = render(clock(media['clock'], offset=-2, duration=1))
    assert close_to(pixel(made, 0.5, 16, 9), second(2), 12)


def test_a_video_shorter_than_its_clip_holds_its_last_frame(media):
    made = render(clock(media['clock'], duration=5))

    assert made.duration == 5
    assert close_to(pixel(made, 4.5, 16, 9), second(3), 12)


def test_an_inpoint_past_the_end_of_a_video_is_refused(media):
    with pytest.raises(EdlException, match=r"clip 0 .*inpoint 9"):
        render(clock(media['clock'], inpoint=9, duration=1))


def test_a_template_is_built_long_enough_to_reach_its_outpoint():
    made = render(still(inpoint=3, outpoint=4))
    assert made.clips[0].duration == 1
    assert pixel(made, 0.5, 16, 9) == GREEN


def test_timing_is_available_to_callers():
    """So a preview can ask which clips are playing at t, by the same rules."""
    clip = Clip(start=2, inpoint=1, outpoint=4, duration=99)
    assert clipTiming(clip) == Timing(start=2, inpoint=1, length=3)
    assert clipTiming(clip).outpoint == 4


@pytest.mark.parametrize(
    'attrs, problem',
    [
        ({'start': -1}, 'start must not be negative'),
        ({'inpoint': -1}, 'inpoint must not be negative'),
        ({'inpoint': 2, 'outpoint': 2}, 'outpoint .* must be after'),
        ({'inpoint': 2, 'outpoint': 1}, 'outpoint .* must be after'),
        ({'duration': 0}, 'duration must be positive'),
        ({'duration': -5}, 'duration must be positive'),
        ({'fadeIn': -1}, 'fadeIn must not be negative'),
        ({'fadeOut': -0.5}, 'fadeOut must not be negative'),
        ({'opacity': 4.2}, 'opacity must be between 0 and 1'),
        ({'opacity': -0.1}, 'opacity must be between 0 and 1'),
    ],
)
def test_timing_that_describes_no_clip_is_refused(attrs, problem):
    with pytest.raises(EdlException, match=rf"clip 1 \('makeColor'\): {problem}"):
        render(still(), still(**attrs))


def test_an_edl_duration_must_be_positive():
    with pytest.raises(EdlException, match='duration must be positive'):
        render(still(), duration=0)


def test_edl_duration_is_the_length_of_the_output():
    assert render(still(duration=2), duration=7).duration == 7
    assert render(still(duration=2), duration=1).duration == 1


# --- fades ------------------------------------------------------------------


@pytest.mark.parametrize('seconds', [0, None])
def test_no_fade_means_no_fade(seconds, recorded_fades):
    made = render(color_clip(fadeIn=seconds, fadeOut=seconds, duration=2))

    assert recorded_fades == []
    assert pixel(made, 0, 16, 9) == GREEN
    assert pixel(made, 1.99, 16, 9) == GREEN


def test_a_fade_is_applied_once_for_as_long_as_asked(recorded_fades):
    made = render(color_clip(fadeIn=2.0, fadeOut=0.5, duration=4))

    assert recorded_fades == [('crossfadein', 2.0), ('crossfadeout', 0.5)]
    assert pixel(made, 0, 16, 9) == BLACK
    assert close_to(pixel(made, 1, 16, 9), (0, 128, 0), 2)
    assert pixel(made, 3, 16, 9) == GREEN


def test_the_default_fades_are_one_second(recorded_fades):
    render(color_clip())
    assert recorded_fades == [('crossfadein', 1), ('crossfadeout', 1)]


# Templates that need ImageMagick (and, for title, cairo) to build.
TEXT_TEMPLATES = ['title', 'textBox', 'initial', 'bullets']


@pytest.mark.render
@pytest.mark.parametrize('name', TEXT_TEMPLATES)
def test_templates_add_no_fades_of_their_own(name, recorded_fades):
    clip = Clip(
        type='template',
        name=name,
        duration=3,
        fadeIn=0,
        fadeOut=0,
        data=TemplateData(text='One line'),
    )
    render(clip)
    assert recorded_fades == []


@pytest.mark.render
@pytest.mark.parametrize('name', ['initial', 'bullets'])
def test_sequence_templates_fade_only_between_their_items(name, recorded_fades):
    text = {'initial': 'One. Two. Three', 'bullets': 'One • Two • Three'}
    clip = Clip(
        type='template',
        name=name,
        duration=9,  # three items of 3 seconds each: no padding after them
        fadeIn=0,
        fadeOut=0,
        data=TemplateData(text=text[name]),
    )
    render(clip)

    ins = [c for c in recorded_fades if c[0] == 'crossfadein']
    outs = [c for c in recorded_fades if c[0] == 'crossfadeout']
    # Three items: two transitions, each a fade out and a fade in.
    assert (len(ins), len(outs)) == (2, 2)


# --- opacity ----------------------------------------------------------------


@pytest.mark.parametrize(
    'opacity, expected',
    [(0, RED), (0.5, (128, 128, 0)), (1, GREEN), (None, GREEN)],
)
def test_opacity_zero_is_transparent(opacity, expected):
    made = render(still('#ff0000'), still('#00ff00', opacity=opacity))
    assert close_to(pixel(made, 1, 16, 9), expected, 1)
