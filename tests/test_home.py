import base64
from dataclasses import asdict


def test_root(client):
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["Location"] == "http://localhost/api/"


def test_home(client):
    response = client.get("/api")
    assert response.headers["Location"] == "http://localhost/api/"

    response = client.get("/api/")
    assert response.headers["Location"] == "http://localhost/api/v1.0/"


def test_whoami_fail(client):
    response = client.get("/api/whoami")
    assert response.status_code == 403


def test_whoami_ok(client, basic_auth):
    response = client.get(
        "/api/whoami",
        headers={"Authorization": basic_auth["user"].auth},
    )
    assert response.status_code == 200
    assert response.json == asdict(basic_auth["user"])
