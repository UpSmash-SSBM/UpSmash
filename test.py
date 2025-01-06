import pytest
from upsmash import create_full_app

@pytest.fixture
def app():
    app = create_full_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()


def test_app_is_working(client):
    response = client.get('/')
    assert response.status_code == 200
