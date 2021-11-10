from datetime import datetime

from flask import current_app, jsonify, request
from flask_tern import openapi
from flask_tern.auth import current_user, require_user
from ssh_cert_service.utils.ssh_keygen import SSHKeygen

from .blueprint import bp


@bp.route("/token", methods=["POST"])
@require_user
@openapi.validate()
def get_token():
    """
    Generate a new signed SSH Key Pair

    :return: object public_key and private_key
    :rtype: json
    """
    principals = current_user[current_app.config["SSH_PRINCIPAL_CLAIM"]]
    ssh = SSHKeygen(current_app.config["USER_CA_KEY"], current_app.config["USER_CA_KEY_PASS"])
    ca_name = current_app.config["USER_CA_NAME"]
    # TODO: what about passphrase? (get from requests or generate a random and return it?)
    passphrase = ""
    # key identity ... use CA name and user principal as identity
    identity = f"{ca_name}:{principals}"
    # comment ... something user readable ... identity works for us as well
    comment = identity
    # domain ... should probably be a list of hosts ... who fills that in?
    domain = ""
    # TODO: validity ... should come from request and min/max should be enforced by server
    validity = "-1:+1d"
    #
    private_key, public_key, cert_key = ssh.gen_key(passphrase, identity, domain, validity, principals, comment)

    return jsonify({"public_key": public_key, "private_key": private_key, "cert_key": cert_key})


@bp.route("/token/signing", methods=["POST"])
@require_user
@openapi.validate(True, False)
def token_login_post():
    """
    Verify a passed in public key and cert key is valid for this CA

    :return: object cert-key
    :rtype: json
    """
    data = request.json
    public_key = data.get("public_key")
    cert_key = data.get("cert_key")

    if not public_key:
        raise Exception("The public and certificate keys cannot be empty")

    ssh = SSHKeygen(current_app.config["USER_CA_KEY"], current_app.config["USER_CA_KEY_PASS"])
    # TODO: maybe change worklow here ?
    #       e.g. verify_signature could return None on failure or cert_data if successful?
    #            would avoid double parsing the cert
    cert_data = ssh.get_certificate_data(cert_key)
    is_valid = ssh.verify_signature(public_key, cert_key)

    # Check if the certificated has expired yet.
    validity = cert_data.get("valid")
    if validity:
        # TODO: get_certificate_data might parse that ['valid'] into a list (from, to)
        #       maybe already as datetime objects
        str_expired = validity[validity.rfind(" ") + 1 :]
        # TODO: what is the timezone to compare dates? always local?
        date_expired = datetime.strptime(str_expired, "%Y-%m-%dT%H:%M:%S")
        is_valid = datetime.now() <= date_expired

    if not (
        is_valid
        and
        # TODO: gw: I don't think this is working as expected ... the regexp in ssh_keygen.py for principals does not generate tuples
        current_user[current_app.config["SSH_PRINCIPAL_CLAIM"]] not in [x.strip() for x in cert_data.get("principals")]
    ):
        return jsonify(
            {
                "message": "Error!, You do not have access to it, please verify you certificate or public key",
                "code": 403,
            }
        )

    return jsonify({"message": "success", "code": 200})
