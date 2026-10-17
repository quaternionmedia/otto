"""Templates draw what they are asked to.

The templates that need ImageMagick (every one that draws text) are marked
`render`.
"""

import pytest
from helpers import close_to, color_clip, pixel

from otto import templates
from otto.colortransitions import boxReveal
from otto.models import Clip, Edl, TemplateData
from otto.render import generateEdl

FRAME = (64, 36)
BLACK = (0, 0, 0)
# 40% of full intensity: the templates' default background opacity, over black.
FAINT = 102


def render(*clips):
    return generateEdl(Edl(clips=list(clips)), moviesize=FRAME)


def template(name, duration=3, **data):
    data.setdefault('text', 'x')
    data.setdefault('fontsize', 8)  # a small glyph, leaving the box corners bare
    return Clip(
        type='template',
        name=name,
        duration=duration,
        fadeIn=0,
        fadeOut=0,
        data=TemplateData(**data),
    )


# --- colour -----------------------------------------------------------------


@pytest.mark.parametrize(
    'color, rgb',
    [('#f2aa4c', (242, 170, 76)), ('#101820', (16, 24, 32)), ('white', (255,) * 3)],
)
def test_makecolor_paints_the_colour_asked_for(color, rgb):
    made = render(color_clip(color, fadeIn=0, fadeOut=0))
    assert pixel(made, 1, 32, 18) == rgb


# The text box of each of these is half the frame, centred: x 16-48, y 9-27.
# (46, 10) is inside it, away from the glyph; (60, 5) is outside it, and clear
# of the bar title's reveal leaves at the left.


@pytest.mark.render
@pytest.mark.parametrize(
    'name, field', [('textBox', 'bg'), ('initial', 'bg'), ('title', 'bg')]
)
def test_a_background_is_painted_in_its_colour(name, field):
    made = render(template(name, **{field: '#0000ff'}))

    assert close_to(pixel(made, 2.9, 46, 10), (0, 0, FAINT), 2)
    assert pixel(made, 2.9, 60, 5) == BLACK


@pytest.mark.render
def test_a_background_blends_at_its_opacity_over_what_is_beneath():
    """Not at its opacity squared, as a composite nested in a composite did."""
    beneath = color_clip('#ff0000', duration=3, fadeIn=0, fadeOut=0)
    made = render(beneath, template('textBox', bg='#0000ff'))

    assert close_to(pixel(made, 1.5, 46, 10), (153, 0, FAINT), 2)
    assert pixel(made, 1.5, 60, 5) == (255, 0, 0)


@pytest.mark.render
def test_bullets_paint_their_box_in_the_theme_colour():
    made = render(template('bullets', themecolor='#ff0000'))

    assert close_to(pixel(made, 1.5, 46, 10), (FAINT, 0, 0), 2)
    assert pixel(made, 1.5, 60, 5) == BLACK


@pytest.mark.render
@pytest.mark.parametrize('name', ['textBox', 'title'])
def test_no_background_is_painted_without_bg(name):
    made = render(template(name))
    assert pixel(made, 2.9, 46, 10) == BLACK


# --- shapes -----------------------------------------------------------------
#
# The gizeh helpers take `clipsize`. They were called with `size=`, which
# **kwargs swallowed, so every box was drawn at the 800x600 default.


@pytest.mark.render
def test_titles_reveal_box_is_sized_from_the_text():
    made = templates.title(text='x', clipsize=FRAME, duration=3)
    reveal = made.clips[-1]
    assert tuple(reveal.size) == (32 + 200, 18 + 40)  # textsize plus padding


@pytest.mark.render
def test_bullets_overlay_is_sized_from_the_text():
    made = templates.bullets(text='x', clipsize=FRAME, duration=3)
    first_bullet = made.clips[0]
    assert tuple(first_bullet.clips[-1].size) == (32, 18)


@pytest.mark.render
def test_finals_outline_is_sized_from_the_frame():
    made = templates.final(text='x', clipsize=FRAME, duration=3)
    assert tuple(made.clips[0].size) == (54, 30)  # 85% of the frame


@pytest.mark.render
def test_the_reveal_box_starts_covering_all_of_itself():
    box = boxReveal(duration=3, clipsize=(40, 20), padding=(10, 5))
    coverage = box.mask.get_frame(0)

    assert tuple(box.size) == (60, 30)
    # The bottom padding rows were left uncovered.
    assert coverage[1:-1, 1:-1].min() == pytest.approx(1)


# --- effects ----------------------------------------------------------------

SEEDED_FLY_IN = {'c1x': 1, 'c1y': 0, 'ax': 0, 'ay': 0, 'c2x': 0, 'c2y': 1}
"""The bezier2 data alfred's seeded projects give textBox."""


def fx(**data):
    return {'name': 'bezier2', 'data': data}


def still_curve(x, y=0.0):
    """A curve that stays at (x, y)."""
    return fx(c1x=x, c1y=y, ax=x, ay=y, c2x=x, c2y=y)


def test_an_effect_flies_in_horizontally_and_rests():
    position = templates._motion([fx(**SEEDED_FLY_IN)])

    assert position(0) == pytest.approx((1, 0))
    assert position(0.5) == pytest.approx((0.25, 0))  # (1 - t)^2
    assert position(1) == (0, 0)
    assert position(4) == (0, 0)


def test_an_effect_can_move_vertically_when_it_says_so():
    position = templates._motion([fx(**SEEDED_FLY_IN, axes='xy')])
    assert position(0.5) == pytest.approx((0.25, 0.25))  # (t^2 for y)


def test_every_effect_applies_not_just_the_last():
    position = templates._motion([still_curve(0.25), still_curve(0.5, 0.1)])
    assert position(0.5) == pytest.approx((0.75, 0))


def test_an_fx_model_is_accepted_as_well_as_a_dict():
    from otto.models import FX

    position = templates._motion([FX(name='bezier2', data=SEEDED_FLY_IN)])
    assert position(0.5) == pytest.approx((0.25, 0))


@pytest.mark.parametrize(
    'effect, problem',
    [
        ({'name': 'bezier2'}, 'needs data'),
        ({'name': 'bezier2', 'data': {'c1x': 1}}, 'needs data'),
        ({'name': 'makeColor', 'data': SEEDED_FLY_IN}, 'no fx is named'),
        ({'name': 'bezier2', 'data': {**SEEDED_FLY_IN, 'axes': 'z'}}, 'axes'),
    ],
)
def test_a_bad_effect_is_refused_before_any_frame_is_drawn(effect, problem):
    with pytest.raises(ValueError, match=problem):
        templates._motion([effect])


@pytest.mark.render
def test_a_bad_effect_fails_the_clip_by_name():
    from otto.exceptions import EdlException

    clip = template('textBox', fxs=[{'name': 'bezier2'}])
    with pytest.raises(EdlException, match=r"clip 0 \('textBox'\): .*needs data"):
        render(clip)


@pytest.mark.render
@pytest.mark.parametrize('name', ['textBox', 'initial', 'bullets'])
def test_text_templates_move_along_their_effects(name):
    made = render(template(name, fxs=[still_curve(0.25)]))

    assert made.clips[0].pos(0.5) == pytest.approx((0.25, 0))
    assert made.clips[0].pos(1.5) == (0, 0)


@pytest.mark.parametrize('name', ['initial', 'bullets'])
def test_no_template_shares_a_mutable_default(name):
    import inspect

    assert (
        inspect.signature(templates.TEMPLATES[name]).parameters['fxs'].default is None
    )


@pytest.mark.render
def test_bullets_build_their_own_overlay_on_every_call():
    templates.bullets(text='x', clipsize=FRAME, duration=3)
    second = templates.bullets(text='x', clipsize=(128, 72), duration=3)

    assert tuple(second.clips[0].clips[-1].size) == (64, 36)


@pytest.mark.render
def test_bullets_that_end_early_are_held_to_the_duration():
    """Frames after the last bullet raised IndexError in the middle of a render."""
    made = render(template('bullets', duration=10))

    assert made.duration == 10
    made.get_frame(9.5)


@pytest.mark.render
def test_bullets_without_text_are_refused():
    from otto.exceptions import EdlException

    with pytest.raises(EdlException, match='bullets needs text'):
        render(template('bullets', text=' • '))


# --- final ------------------------------------------------------------------


@pytest.mark.render
def test_final_renders_without_a_phone_number():
    """It raised KeyError: the defaults it falls back on have no phone."""
    made = render(template('final', fontsize=None))
    made.get_frame(1)


@pytest.mark.render
def test_final_draws_the_lines_it_has():
    without = templates.final(text='x', clipsize=FRAME, duration=3)
    with_phone = templates.final(text='x', phone='555', clipsize=FRAME, duration=3)

    # The outline and text, address and website; then the phone as well.
    assert len(without.clips) == 4
    assert len(with_phone.clips) == 5
