from datetime import datetime

from flask import jsonify, request
from flask_tern import openapi
from flask_tern.auth import current_user, require_user
from ssh_cert_service.utils.ssh_keygen import SSHKeygen

from .blueprint import bp

COMMENTS = "COESRA"


@bp.route("/token", methods=["POST"])
@openapi.validate()
def get_token():
    """
    :return: object public-key and private-key
    :rtype: json
    """

    principals = current_user["coesra_uname"]
    ssh = SSHKeygen(COMMENTS)
    identity = "COESRA"

    private_key, public_key, cert_key = ssh.gen_key("", identity, "coesra.com.au", "-1:+12w", principals)

    return jsonify({"public_key": public_key, "private_key": private_key, "cert_key": cert_key})


@bp.route("/token/signing", methods=["POST"])
@openapi.validate(True, False)
def token_login_post():
    """
    Check that the public key is valid hasn't expired and match with the storage in DB

    :return: object public-key and private-key
    :rtype: json
    """
    data = request.json
    cert_key = data.get("cert_key")
    public_key = data.get("public_key")

    if not public_key or not cert_key:
        raise Exception("The public and certificate keys cannot be empty")

    ssh = SSHKeygen(COMMENTS)
    cert_data = ssh.get_certificate_data(cert_key.encode("utf-8"))
    is_valid = ssh.verify_signature(public_key.encode("utf-8"), cert_key.encode("utf-8"))

    # Check if the certificated has expired yet.
    validity = cert_data.get("valid")
    if validity:
        str_expired = validity[validity.rfind(" ") + 1 :]
        date_expired = datetime.strptime(str_expired, "%Y-%m-%dT%H:%M:%S")
        is_valid = datetime.now() <= date_expired

    if not is_valid or current_user["coesra_uname"] not in [x.strip() for x in cert_data.get("principals")]:
        return jsonify(
            {
                "message": "Error!, You do not have access to it, please verify you certificate or public key",
                "code": 403,
            }
        )

    return jsonify({"message": "success", "code": 200})
