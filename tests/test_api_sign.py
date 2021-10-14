def test_sign_no_auth(client):
    response = client.post(
        "/api/v1.0/token/signing",
    )
    assert response.status_code == 403


def test_sign(client, basic_auth):
    # generate a key pair
    response = client.post(
        "/api/v1.0/token",
        headers={"Authorization": basic_auth["user"]["auth"]},
    )

    response = client.post(
        "/api/v1.0/token/signing",
        json={
            "cert_key": response.json["cert_key"],
            "public_key": response.json["public_key"],
        },
        headers={"Authorization": basic_auth["user"]["auth"]},
    )
    assert response.status_code == 200
