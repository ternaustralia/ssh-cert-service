from datetime import timedelta
from pathlib import Path

import pytest
from flask_tern.testing.fixtures import basic_auth as base_auth  # noqa
from flask_tern.testing.fixtures import cache_spec, monkeypatch_session  # noqa
from ssh_cert_service import create_app


@pytest.fixture
def ca_key():
    """Return path to SSH CA key."""
    return str(Path(__file__).with_name("test_user_ca.key"))


@pytest.fixture
def ca_pass():
    """Return password for SSH CA key."""
    return "test"


@pytest.fixture
def app(ca_key, ca_pass):
    app = create_app(
        {
            "TESTING": True,
            "OIDC_DISCOVERY_URL": "https://auth.example.com/.well-known/openid-configuration",
            "OIDC_CLIENT_ID": "oidc-test",
            "USER_CA_NAME": "COESRA",
            "USER_CA_KEY": ca_key,
            "USER_CA_KEY_PASS": ca_pass,
            "SSH_PRINCIPAL_CLAIM": "coesra_uname",
            "SSH_MIN_VALIDITY": int(timedelta(seconds=0).total_seconds()),
            "SSH_MAX_VALIDITY": int(timedelta(days=1).total_seconds()),
        }
    )
    yield app


@pytest.fixture
def basic_auth(base_auth):  # noqa
    for key, user in base_auth.items():
        base_auth[key].claims["coesra_uname"] = user.name
    return base_auth


@pytest.fixture
def client(app, basic_auth):  # noqa
    return app.test_client()
