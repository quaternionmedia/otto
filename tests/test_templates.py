"""Templates draw what they are asked to.

The templates that need ImageMagick (every one that draws text) are marked
`render`.
"""

import pytest
from helpers import close_to, color_clip, pixel

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
# (17, 10) is inside it, away from the glyph; (5, 5) is outside it.


@pytest.mark.render
@pytest.mark.parametrize(
    'name, field', [('textBox', 'bg'), ('initial', 'bg'), ('title', 'bg')]
)
def test_a_background_is_painted_in_its_colour(name, field):
    made = render(template(name, **{field: '#0000ff'}))

    assert close_to(pixel(made, 2.9, 46, 10), (0, 0, FAINT), 2)
    assert pixel(made, 2.9, 5, 5) == BLACK


@pytest.mark.render
def test_a_background_blends_at_its_opacity_over_what_is_beneath():
    """Not at its opacity squared, as a composite nested in a composite did."""
    beneath = color_clip('#ff0000', duration=3, fadeIn=0, fadeOut=0)
    made = render(beneath, template('textBox', bg='#0000ff'))

    assert close_to(pixel(made, 1.5, 17, 10), (153, 0, FAINT), 2)
    assert pixel(made, 1.5, 5, 5) == (255, 0, 0)


@pytest.mark.render
def test_bullets_paint_their_box_in_the_theme_colour():
    made = render(template('bullets', themecolor='#ff0000'))

    assert close_to(pixel(made, 1.5, 17, 10), (FAINT, 0, 0), 2)
    assert pixel(made, 1.5, 5, 5) == BLACK


@pytest.mark.render
@pytest.mark.parametrize('name', ['textBox', 'title'])
def test_no_background_is_painted_without_bg(name):
    made = render(template(name))
    assert pixel(made, 2.9, 46, 10) == BLACK
