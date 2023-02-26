# import pytest

from fastapi.testclient import TestClient
from otto.main import app

client = TestClient(app)


# / response sucessfully gives an {'otto': 'semantic.version.number'} response
def test_get_home():
    response = client.get('/')
    assert response.status_code == 200, 'Home page did not return sucessfully'
    assert 'application/json' in response.headers['content-type'], 'Type is not JSON'
    assert response.json()['otto'].find('.'), 'No Otto version number found'


# /templates returns a list of templates
def test_get_templates():
    response = client.get('/templates')
    assert response.status_code == 200, 'Template list did not return sucessfully'
    assert (
        'application/json' in response.headers['content-type']
    ), 'Content-Type is not JSON'
    templates = response.json()
    assert type(templates) is list, 'Type of response is not List'
    assert len(templates) > 0, 'Templates list is empty!'
