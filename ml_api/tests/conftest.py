import pytest
from server import app as server_app

@pytest.fixture()
def app():
    server_app.config.update({
        "TESTING": True,
    })
    yield server_app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
