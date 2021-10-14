import pytest
from flask_tern.testing.fixtures import basic_auth as base_auth  # noqa
from flask_tern.testing.fixtures import cache_spec, monkeypatch_session  # noqa
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
def basic_auth(base_auth):  # noqa
    for key, value in base_auth.items():
        base_auth[key]["coesra_uname"] = value["name"]
    return base_auth


@pytest.fixture
def client(app, basic_auth):  # noqa
    return app.test_client()
