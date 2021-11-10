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


def test_sign_existing(client, basic_auth, ca_key, ca_pass):
    # generate a key pair
    from ssh_cert_service.utils.ssh_keygen import SSHKeygen

    ssh = SSHKeygen(ca_key, ca_pass)
    pub_key, priv_key, cert_key = ssh.gen_key()

    response = client.post(
        "/api/v1.0/token/sign",
        json={
            "public_key": pub_key,
        },
        headers={"Authorization": basic_auth["user"]["auth"]},
    )
    assert response.status_code == 200
    cert_key = response.json["cert_key"]
    assert ssh.verify_signature(pub_key, cert_key)
    cert_data = ssh.get_certificate_data(cert_key)
    assert basic_auth["user"]["coesra_uname"] in cert_data.principals
