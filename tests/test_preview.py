from fastapi.testclient import TestClient
from otto.main import app
from otto.models import Edl, Clip, TemplateData
from otto.exceptions import EmptyClipsException
from pytest import raises


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
    payload = {'edl': Edl(clips=[]).dict()}
    response = client.post('/preview', json=payload)
    assert response.status_code == 422, 'Route requires t parameter'
    error = response.json()
    assert len(error['detail']) == 1, 'There should only be one error here'
    assert error['detail'][0]['loc'] == ['query', 't']
    assert error['detail'][0]['type'] == 'value_error.missing'


def test_empty_edl():
    """POST an Edl with no clips.

    Should validate sucessfully, but raise a rendering exception"""
    with raises(EmptyClipsException):
        payload = {'edl': Edl(clips=[]).dict()}
        client.post('/preview?t=0', json=payload)


def test_color_clip():
    """Test an Edl with one Black video clip"""
    clip = Clip(
        type='template', name='makeColor', data=TemplateData(color='#000000').dict()
    ).dict()
    payload = {'edl': Edl(clips=[clip]).dict()}
    response = client.post('/preview?t=0', json=payload)
    assert response.status_code == 200, 'Black video did not render sucessfully'
    assert response.json().startswith('data/'), 'Returned path is not in data/'


def test_text_clip():
    """Test an Edl with one Text clip"""
    clip = Clip(
        type='template',
        name='textBox',
        duration=1,
        start=0,
        data=TemplateData(text='test', color='#FFFFFF'),
    ).dict()
    payload = {'edl': Edl(clips=[clip]).dict(), 'duration': 1}
    response = client.post('/preview?t=1', json=payload)
    assert response.status_code == 200, 'Text did not render sucessfully'
    assert response.json().startswith('data/'), 'Returned path is not in data/'
