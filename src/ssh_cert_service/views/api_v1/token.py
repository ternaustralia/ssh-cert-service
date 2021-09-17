from flask import jsonify
from flask_tern import openapi
from flask_tern.auth import current_user

from .blueprint import bp
from ssh_cert_service.utils.ssh_keygen import SSHKeygen


@bp.route("/token")
@openapi.validate()
def get_token():
    """
    :return: object public-key and private-key
    :rtype: json
    """

    principals = current_user['coesra_uname']
    ssh = SSHKeygen()
    identity = 'COESRA'
    comments = 'COESRA'

    private_key, public_key, cert_key = ssh.gen_key(
        comments,
        '',
        identity,
        'coesra.com.au',
        '-1:+12w',
        principals
    ) 

    ssh.verify_signature(public_key.decode(), cert_key.decode())
    
    return jsonify({
        'public_key': public_key.decode(),
        'private_key': private_key.decode(("utf-8")),
        'cert_key': cert_key.decode(),
    })


@bp.route("/token/signing", methods=["POST"])
@openapi.validate()
def token_login_post():
    """
    Check that the public key is valid hasn't expired and match with the storage in DB 

    :return: object public-key and private-key
    :rtype: json
    """
    pass

