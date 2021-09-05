import pytest
from flask_tern.testing.fixtures import basic_auth, cache_spec, monkeypatch_session
from ssh_cert_service import create_app


@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "OIDC_DISCOVERY_URL": "https://auth.example.com/.well-known/openid-configuration",
            "OIDC_CLIENT_ID": "oidc-test",
        }
    )
    yield app


@pytest.fixture
def client(app, basic_auth):
    return app.test_client()
