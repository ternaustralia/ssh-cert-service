def test_token_no_auth(client):
    response = client.post(
        "/api/v1.0/token",
    )
    assert response.status_code == 403


def test_token_gen(client, basic_auth):
    response = client.post(
        "/api/v1.0/token",
        headers={"Authorization": basic_auth["user"]["auth"]},
    )
    assert response.status_code == 200
    assert response.json.keys() == {"private_key", "public_key", "cert_key"}
    assert "PRIVATE KEY" in response.json["private_key"]
    assert response.json["public_key"].startswith("ssh-rsa")
    assert response.json["cert_key"].startswith("ssh-rsa-cert-v01")
