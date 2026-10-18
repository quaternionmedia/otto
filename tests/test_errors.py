"""Bad input raises an EdlException that names the clip.

Before, an unknown type crashed with UnboundLocalError on the first clip and
silently duplicated the previous layer on any later one; template names were
resolved against the whole module namespace; templates swallowed their own
errors and returned None; a refused download returned None and became the
clip's filename.
"""

import shutil

import pytest

from helpers import BLACK_MP4, color_clip
from otto import getdata, templates
from otto.exceptions import DownloadException, EdlException
from otto.models import Clip, Edl, TemplateData
from otto.render import generateEdl

SIZE = (64, 36)


def render(*clips):
    return generateEdl(Edl(clips=list(clips)), moviesize=SIZE)


# --- clip types -------------------------------------------------------------


@pytest.mark.parametrize('kind', ['bogus', 'Video', '', None])
def test_an_unknown_or_missing_type_is_refused(kind):
    with pytest.raises(EdlException, match=r"clip 0 \('x'\): unknown clip type"):
        render(Clip(type=kind, name='x', duration=1))


def test_an_unknown_type_after_a_good_clip_is_refused_not_duplicated():
    with pytest.raises(EdlException, match=r"clip 1 \('x'\)"):
        render(color_clip(), Clip(type='bogus', name='x', duration=4))


# --- templates --------------------------------------------------------------


@pytest.mark.parametrize(
    'name',
    [
        'no_such_template',
        # Imported into otto.templates, and reachable by name until there was
        # a registry.
        'concatenate_videoclips',
        'rgbToDec',
        'TextClip',
        'ColorClip',
        'CompositeVideoClip',
        'boxReveal',
        'defaults',
        'ct',
    ],
)
def test_only_registered_templates_can_be_named(name):
    clip = Clip(type='template', name=name, duration=1, data=TemplateData(text='x'))
    with pytest.raises(EdlException, match=rf"clip 0 \('{name}'\): no template"):
        render(clip)


# alfred's allowlist (alfred/core/routes/templates.py TEMPLATE_NAMES).
ALFRED_TEMPLATE_NAMES = ('title', 'textBox', 'bullets', 'initial', 'makeColor')


@pytest.mark.parametrize('name', ALFRED_TEMPLATE_NAMES)
def test_every_template_alfred_offers_is_registered(name):
    assert templates.TEMPLATES[name] is getattr(templates, name)


def test_the_registry_holds_templates_and_nothing_else():
    assert set(templates.TEMPLATES) == {
        'title',
        'textBox',
        'bullets',
        'initial',
        'final',
        'makeColor',
    }
    assert set(templates.__all__) == {'TEMPLATES', *templates.TEMPLATES}


def test_a_template_clip_needs_data():
    with pytest.raises(EdlException, match=r"clip 0 \('makeColor'\): .*needs `data`"):
        render(Clip(type='template', name='makeColor', duration=1))


def test_a_failing_template_raises_with_its_cause():
    """`title` needs text. It used to print the TypeError and return None."""
    clip = Clip(type='template', name='title', duration=1, data=TemplateData())
    with pytest.raises(EdlException, match=r"clip 0 \('title'\): template") as raised:
        render(clip)
    assert isinstance(raised.value.__cause__, TypeError)


@pytest.mark.parametrize('name', ['title', 'textBox', 'bullets', 'initial', 'final'])
def test_templates_raise_rather_than_return_none(name):
    with pytest.raises((AttributeError, TypeError)):
        templates.TEMPLATES[name](text=None)


# --- media ------------------------------------------------------------------


def test_a_media_clip_needs_a_name():
    with pytest.raises(EdlException, match=r"clip 0 \(None\): a video clip needs"):
        render(Clip(type='video', duration=1))


def test_a_missing_file_names_the_clip():
    with pytest.raises(EdlException, match=r"clip 0 \('/no/such/file.mp4'\)"):
        render(Clip(type='video', name='/no/such/file.mp4', duration=1))


def test_the_clip_name_is_left_as_the_caller_wrote_it():
    clip = Clip(type='video', name=BLACK_MP4, duration=1)
    edl = Edl(clips=[clip])
    generateEdl(edl, moviesize=SIZE)
    assert edl.clips[0].name == BLACK_MP4


def test_a_downloaded_clip_keeps_its_url(fake_head, monkeypatch):
    """It used to be overwritten with the downloaded file's path."""
    monkeypatch.setattr(
        getdata, 'download_url', lambda url, filename: shutil.copy(BLACK_MP4, filename)
    )
    edl = Edl(clips=[Clip(type='video', name='https://example.test/a.mp4', duration=1)])

    generateEdl(edl, moviesize=SIZE)

    assert edl.clips[0].name == 'https://example.test/a.mp4'


# --- download ---------------------------------------------------------------
#
# `fake_head` (conftest.py) answers the HEAD request a download starts with.


@pytest.mark.parametrize(
    'response, reason',
    [
        ({'content_type': 'text/html'}, 'not allowed'),
        ({'content_type': 'text/plain'}, 'not allowed'),
        ({'content_type': 'application/zip'}, 'type not allowed'),
        ({'content_type': None}, 'no content_type'),
        ({'content_length': str(int(2e10))}, 'too large'),
        ({'content_length': None}, 'size must be known'),
    ],
)
def test_a_refused_download_raises_naming_the_url(
    response, reason, fake_head, monkeypatch
):
    fetched = []
    monkeypatch.setattr(getdata, 'download_url', lambda *args: fetched.append(args))
    monkeypatch.setattr(getdata.path, 'isfile', lambda _: False)
    fake_head(**response)

    with pytest.raises(DownloadException, match=reason) as raised:
        getdata.download('https://example.test/bad')

    assert 'https://example.test/bad' in str(raised.value)
    assert fetched == [], 'a refused file was fetched anyway'


def test_an_unreachable_url_raises(monkeypatch):
    def unreachable(url, allow_redirects):
        raise ConnectionError('no route to host')

    monkeypatch.setattr(getdata, 'head', unreachable)
    with pytest.raises(DownloadException, match='could not be reached'):
        getdata.download('https://example.test/a.mp4')


def test_a_failed_fetch_raises(fake_head, monkeypatch):
    def broken(url, filename):
        raise OSError('disk full')

    monkeypatch.setattr(getdata, 'download_url', broken)
    monkeypatch.setattr(getdata.path, 'isfile', lambda _: False)
    with pytest.raises(DownloadException, match='disk full'):
        getdata.download('https://example.test/a.mp4')


def test_a_content_type_with_parameters_is_accepted(fake_head, monkeypatch):
    monkeypatch.setattr(getdata.path, 'isfile', lambda _: True)
    fake_head(content_type='Video/MP4; charset=binary')
    assert getdata.download('https://example.test/a').endswith('.mp4')


def test_a_refused_download_fails_the_render_naming_the_clip(fake_head, monkeypatch):
    monkeypatch.setattr(getdata.path, 'isfile', lambda _: False)
    fake_head(content_type='text/html')
    clip = Clip(type='video', name='https://example.test/bad', duration=1)

    with pytest.raises(EdlException) as raised:
        render(clip)

    message = str(raised.value)
    assert message.startswith("clip 0 ('https://example.test/bad'):")
    assert 'not allowed' in message
    assert isinstance(raised.value.__cause__, DownloadException)
