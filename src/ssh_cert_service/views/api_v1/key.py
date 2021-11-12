from datetime import datetime
import tempfile
import os

from flask import current_app, jsonify, request
from flask_tern import openapi
from flask_tern.auth import current_user, require_user
from ssh_cert_service.utils.ssh_keygen import SSHKeygen

from .blueprint import bp



@bp.route("/key/generate", methods=["POST"])
@require_user
@openapi.validate()
def get_keys():
    """
    Generate a new signed SSH Key Pair

    :return: object public_key and private_key
    :rtype: json
    """
    data = request.json if request.json else dict() 

    principals = current_user[current_app.config["SSH_PRINCIPAL_CLAIM"]]
    ssh = SSHKeygen(current_app.config["USER_CA_KEY"], current_app.config["USER_CA_KEY_PASS"])
    ca_name = current_app.config["USER_CA_NAME"]
    # TODO: what about passphrase? (get from requests or generate a random and return it?)
    passphrase = data.get("passphrase", "")
    # key identity ... use CA name and user principal as identity
    identity = f"{ca_name}:{principals}"
    # comment ... something user readable ... identity works for us as well
    comment = identity
    # domain ... should probably be a list of hosts ... who fills that in?
    domain = ""
    # TODO: validity ... should come from request and min/max should be enforced by server
    validity = data.get("validity", "-1d:+1d")

    private_key, public_key, cert_key = ssh.gen_key(passphrase, identity, domain, validity, principals, comment)

    return jsonify({"public_key": public_key, "private_key": private_key, "cert_key": cert_key})


@bp.route("/key/verify", methods=["POST"])
@require_user
@openapi.validate(True, False)
def verify_keys():
    """
    Verify a passed in public key and cert key is valid for this CA

    :return: object cert-key
    :rtype: json
    """
    data = request.json
    public_cert_key = data.get("public_cert_key")

    if not public_cert_key:
        raise Exception("The public and certificate keys cannot be empty")

    ssh = SSHKeygen(current_app.config["USER_CA_KEY"], current_app.config["USER_CA_KEY_PASS"])
    # TODO: maybe change worklow here ?
    #       e.g. verify_signature could return None on failure or cert_data if successful?
    #            would avoid double parsing the cert
    cert_data = ssh.get_certificate_data(public_cert_key)
    is_valid = ssh.verify_signature(public_cert_key)

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


@bp.route("/key/sign", methods=["POST"])
@require_user
@openapi.validate()
def key_sign():
    """
    Sign public key

    :return: object cert-key
    :rtype: json
    """

    data = request.json
    public_key = data["public_key"]

    principals = current_user[current_app.config["SSH_PRINCIPAL_CLAIM"]]
    ssh = SSHKeygen(current_app.config["USER_CA_KEY"], current_app.config["USER_CA_KEY_PASS"])
    ca_name = current_app.config["USER_CA_NAME"]
    # key identity ... use CA name and user principal as identity
    identity = f"{ca_name}:{principals}"
    # domain ... should probably be a list of hosts that are allowed to connect to the master node
    domain = ""
    # validity ... when it start : whent it will expired 
    validity = data.get("validity", "-1d:+1d")

    # Create temporary dicrectory and storage the keys there
    with tempfile.TemporaryDirectory() as tmp_dir:
        # write pub key to file
        keys_path = f"{tmp_dir}/{ssh.SSH_NAME}"
        public_path = f"{keys_path}.pub"
        tmp_public = open(os.open(public_path, os.O_CREAT | os.O_WRONLY, mode=0o600), "w")
        tmp_public.write(public_key)
        tmp_public.close()

        # Sign key
        ssh.sign_key(public_path, identity, domain, validity, principals)
        private_key, public_key, cert_key = ssh.load_keys(keys_path)

    return jsonify({"public_key": public_key, "cert_key": cert_key})
    
