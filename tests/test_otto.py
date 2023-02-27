from fastapi.testclient import TestClient
from otto.main import app

client = TestClient(app)


def test_get_home():
    """GET / returns an {'otto': 'semantic.version.number'} response"""
    response = client.get('/')
    assert response.status_code == 200, 'Home page did not return sucessfully'
    assert 'application/json' in response.headers['content-type'], 'Type is not JSON'
    assert response.json()['otto'].find('.'), 'No Otto version number found'


def test_get_templates():
    """GET /templates returns a list of templates"""
    response = client.get('/templates')
    assert response.status_code == 200, 'Template list did not return sucessfully'
    assert (
        'application/json' in response.headers['content-type']
    ), 'Content-Type is not JSON'
    templates = response.json()
    assert type(templates) is list, 'Type of response is not List'
    assert len(templates) > 0, 'Templates list is empty!'
