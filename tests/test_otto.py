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
