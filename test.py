import pytest
from upsmash import create_full_app
from upsmash import db

@pytest.fixture
def app():
    app = create_full_app()
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
    return app

@pytest.fixture
def client(app):
    return app.test_client()


def test_app_is_working(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"UpSmash" in response.data
