from fastapi.testclient import TestClient
from otto.main import app
from otto.models import Edl, Clip, TemplateData
from otto.exceptions import EmptyClipsException
from pytest import raises
from os import path
from pytest import mark

TEST_DIR = path.dirname(path.realpath(__file__))

client = TestClient(app)


def test_get_preview():
    """GET /preview should not exist"""
    response = client.get('/preview')
    assert response.status_code == 405, 'GET /preview method not allowed!'


def test_empty_post():
    """POST empty object should fail with a valdation error"""
    response = client.post('/preview', data={})
    assert response.status_code == 422, 'Empty data should raise a validation error'


def test_without_t():
    """POST an Edl with no t content. Should give validation error"""
    edl = {'edl': Edl(clips=[]).dict()}
    response = client.post('/preview', json=edl)
    assert response.status_code == 422, 'Route requires t parameter'
    error = response.json()
    assert len(error['detail']) == 1, 'There should only be one error here'
    assert error['detail'][0]['loc'] == ['query', 't']
    assert error['detail'][0]['type'] == 'value_error.missing'


def test_empty_edl():
    """POST an Edl with no clips.

    Should validate sucessfully, but raise a rendering exception"""
    with raises(EmptyClipsException):
        edl = {'edl': Edl(clips=[]).dict()}
        client.post('/preview?t=0', json=edl)


def check_rendered_image(edl: Edl):
    response = client.post('/preview?t=1', json=edl)
    assert response.status_code == 200, 'Text did not render sucessfully'
    filename = response.json()
    assert filename.startswith('data'), 'Returned path is not in data/'
    assert path.isfile(filename), 'Can not find file that otto generated'


@mark.render
def test_color_clip():
    """Test an Edl with one Black video clip"""
    clip = Clip(
        type='template', name='makeColor', data=TemplateData(color='#000000').dict()
    ).dict()
    edl = {'edl': Edl(clips=[clip]).dict()}
    check_rendered_image(edl)


@mark.render
def test_text_clip():
    """Test an Edl with one Text clip"""
    clip = Clip(
        type='template',
        name='textBox',
        duration=2,
        start=0,
        data=TemplateData(text='test', color='#FFFFFF'),
    ).dict()
    edl = {'edl': Edl(clips=[clip], duration=2).dict()}
    check_rendered_image(edl)


@mark.render
def test_image_clip():
    """Test an Edl with an image clip"""
    clip = Clip(
        type='image',
        name=path.join(TEST_DIR, 'black.png'),
        duration=1,
    ).dict()
    edl = {'edl': Edl(clips=[clip], duration=1).dict()}
    check_rendered_image(edl)


@mark.render
def test_video_clip():
    """Test an Edl with a video clip"""
    clip = Clip(
        type='video',
        name=path.join(TEST_DIR, 'black.mp4'),
        duration=1,
    ).dict()
    edl = {'edl': Edl(clips=[clip], duration=1).dict()}
    check_rendered_image(edl)


# @mark.render
# def test_audio_clip():
#     """Test an Edl with an audio clip"""
