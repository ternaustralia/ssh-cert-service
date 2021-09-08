from flask import jsonify
from flask_tern import openapi
from flask_tern.auth import current_user, require_user
from flask_tern.logging import create_audit_event, log_audit

from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend

from .blueprint import bp


@bp.route("/example")
@openapi.validate()
def example_get():
    log_audit(create_audit_event("increment", "success"))
    return jsonify({"counter": 1})


@bp.route("/example/<name>", methods=["POST"])
@require_user
@openapi.validate()
def hello_post(name):
    return jsonify(
        {
            "name": name,
            "counter": 1,
            "current_user": dict(current_user),
        }
    )
