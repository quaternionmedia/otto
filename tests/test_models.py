"""The models take an Edl as they did on pydantic 1."""

import pytest
from pydantic import ValidationError

from otto.models import FX, Clip, Edl, Render, TemplateData


def test_every_optional_field_may_be_left_out():
    clip = Clip()
    assert clip.type is None and clip.name is None and clip.data is None
    assert (clip.duration, clip.fadeIn, clip.fadeOut, clip.relative) == (5, 1, 1, True)
    assert TemplateData().method == 'label'
    assert FX(name='blur').data is None


def test_an_edl_may_say_its_duration_is_null():
    assert Edl(clips=[], duration=None).duration is None
    assert Edl(clips=[]).duration is None


def test_a_number_given_for_text_is_text():
    data = TemplateData(text=2024, color=0, position=5)
    assert (data.text, data.color, data.position) == ('2024', '0', '5')
    assert Clip(name=7).name == '7'


def test_numbers_and_pairs_keep_their_kinds():
    clip = Clip(duration=3, start='1.5', resize=[640, 360], position=[0.5, 'top'])
    assert clip.duration == 3.0 and isinstance(clip.duration, float)
    assert clip.start == 1.5
    assert clip.resize == (640, 360)
    assert clip.position == (0.5, 'top')
    assert Clip(resize=2).resize == 2.0
    assert Clip(position='center').position == 'center'


def test_what_was_sent_is_what_dumps_unset():
    clip = Clip.model_validate({'type': 'template', 'name': 'makeColor'})
    assert clip.model_dump(exclude_unset=True) == {
        'type': 'template',
        'name': 'makeColor',
    }


def test_fields_it_does_not_know_are_dropped():
    assert 'i' not in Clip(i=3).model_dump()


def test_a_clip_with_a_null_duration_is_refused():
    with pytest.raises(ValidationError):
        Clip(duration=None)


def test_a_render_s_edl_is_validated():
    render = Render.model_validate({'edl': {'clips': [{'type': 'video'}]}})
    assert isinstance(render.edl.clips[0], Clip)
    assert (render.width, render.height, render.fps) == (1920, 1080, 30.0)
